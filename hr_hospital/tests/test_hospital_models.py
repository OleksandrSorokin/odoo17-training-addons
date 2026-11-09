from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHospitalModels(TransactionCase):
    """Exercise the model constraints and computed values from module 3."""

    @classmethod
    def setUpClass(cls):
        """Create clinical fixtures without demo data."""
        super().setUpClass()
        cls.doctor = cls.env["hr.hospital.doctor"].create({
            "name": "Doctor for Tests",
        })
        cls.patient = cls.env["hr.hospital.patient"].create({
            "name": "Patient for Tests",
            "birth_date": "2000-06-15",
        })
        cls.disease = cls.env["hr.hospital.disease"].create({
            "name": "Test Disease",
        })

    def test_compute_age(self):
        """Age is full years, not merely calendar-year subtraction."""
        today = fields.Date.context_today(self.patient)
        birthday = date(today.year - 20, today.month, today.day)
        self.patient.birth_date = birthday
        self.assertEqual(self.patient.age, 20)
        self.patient.birth_date = today - timedelta(days=1)
        self.assertEqual(self.patient.age, 0)

    def test_mentor_validation(self):
        """A mentor must be a real doctor, never another intern or self."""
        intern = self.env["hr.hospital.doctor"].create({
            "name": "Test Intern",
            "is_intern": True,
            "mentor_id": self.doctor.id,
        })
        self.assertEqual(intern.mentor_id, self.doctor)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            intern.write({"mentor_id": intern.id})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.doctor.write({"is_intern": True})

    def test_duplicate_visit_and_actual_date(self):
        """Reject an overlapping visit and an invalid completed state."""
        appointment_date = "2026-11-12 09:00:00"
        self.env["hr.hospital.visit"].create({
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
            "visit_date": appointment_date,
        })
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["hr.hospital.visit"].create({
                "patient_id": self.patient.id,
                "doctor_id": self.doctor.id,
                "visit_date": "2026-11-12 16:00:00",
            })
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["hr.hospital.visit"].create({
                "patient_id": self.patient.id,
                "doctor_id": self.doctor.id,
                "visit_date": "2026-11-13 16:00:00",
                "state": "done",
            })

    def test_diagnosis_history(self):
        """A diagnosis created for a visit appears in patient history."""
        visit = self.env["hr.hospital.visit"].create({
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
            "visit_date": "2026-11-14 10:00:00",
        })
        diagnosis = self.env["hr.hospital.diagnosis"].create({
            "visit_id": visit.id,
            "disease_id": self.disease.id,
        })
        self.assertIn(diagnosis, self.patient.diagnosis_ids)
        with self.assertRaises(UserError), self.cr.savepoint():
            visit.write({"active": False})

    def test_disease_recursion(self):
        """A disease cannot become its own ancestor."""
        with self.assertRaises(UserError), self.cr.savepoint():
            self.disease.parent_id = self.disease.id
