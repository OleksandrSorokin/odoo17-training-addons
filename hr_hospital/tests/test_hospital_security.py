from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHospitalSecurity(TransactionCase):
    """Verify real ORM access instead of merely hiding form buttons."""

    @classmethod
    def setUpClass(cls):
        """Create separate identities and three appointments."""
        super().setUpClass()
        cls.user_patient = cls._user("patient", "group_hospital_patient")
        cls.user_intern = cls._user("intern", "group_hospital_intern")
        cls.user_doctor = cls._user("doctor", "group_hospital_doctor")
        cls.user_manager = cls._user("manager", "group_hospital_manager")
        cls.user_admin = cls._user("admin", "group_hospital_admin")
        cls.mentor = cls.env["hr.hospital.doctor"].create({
            "name": "Doctor A",
            "user_id": cls.user_doctor.id,
        })
        cls.intern = cls.env["hr.hospital.doctor"].create({
            "name": "Intern A",
            "is_intern": True,
            "mentor_id": cls.mentor.id,
            "user_id": cls.user_intern.id,
        })
        cls.other = cls.env["hr.hospital.doctor"].create({
            "name": "Unrelated Doctor",
        })
        cls.patient = cls.env["hr.hospital.patient"].create({
            "name": "Own Patient",
            "user_id": cls.user_patient.id,
        })
        cls.other_patient = cls.env["hr.hospital.patient"].create({
            "name": "Other Patient",
        })
        cls.visit_own = cls._visit(cls.patient, cls.mentor, "2026-12-01")
        cls.visit_intern = cls._visit(
            cls.other_patient, cls.intern, "2026-12-02"
        )
        cls.visit_other = cls._visit(
            cls.other_patient, cls.other, "2026-12-03"
        )

    @classmethod
    def _user(cls, name, group_xmlid):
        """Create an internal user with exactly one selected hospital role."""
        group = cls.env.ref("hr_hospital." + group_xmlid)
        return cls.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "Hospital test " + name,
            "login": "hospital.test.%s@example.invalid" % name,
            "groups_id": [
                (6, 0, [cls.env.ref("base.group_user").id, group.id])
            ],
        })

    @classmethod
    def _visit(cls, patient, doctor, date):
        """Create a visit using a distinct clinic calendar date."""
        return cls.env["hr.hospital.visit"].create({
            "patient_id": patient.id,
            "doctor_id": doctor.id,
            "visit_date": date + " 09:00:00",
        })

    def _visible_ids(self, user):
        """Fetch all records visible to a non-superuser identity."""
        test_ids = (
            self.visit_own | self.visit_intern | self.visit_other
        ).ids
        visits = self.env["hr.hospital.visit"].with_user(user).search(
            [("id", "in", test_ids)]
        )
        return set(visits.ids)

    def test_patient_can_read_only_own(self):
        """Patient sees exactly the appointment linked to their login."""
        self.assertEqual(
            self._visible_ids(self.user_patient), {self.visit_own.id}
        )
        with self.assertRaises(AccessError):
            self.visit_own.with_user(self.user_patient).write({
                "state": "cancelled"
            })

    def test_intern_only_own_and_doctor_mentor(self):
        """Intern has own appointments; supervising doctor sees both."""
        self.assertEqual(
            self._visible_ids(self.user_intern), {self.visit_intern.id}
        )
        self.assertEqual(
            self._visible_ids(self.user_doctor),
            {self.visit_own.id, self.visit_intern.id},
        )

    def test_manager_reads_all_admin_can_delete(self):
        """Manager reads all visits, and only the admin can unlink."""
        expected_ids = {
            self.visit_own.id,
            self.visit_intern.id,
            self.visit_other.id,
        }
        self.assertTrue(
            expected_ids.issubset(self._visible_ids(self.user_manager))
        )
        with self.assertRaises(AccessError):
            self.visit_other.with_user(self.user_manager).unlink()
        self.visit_other.with_user(self.user_admin).unlink()
        self.assertFalse(self.visit_other.exists())
