from collections import defaultdict

from odoo import api, fields, models


class HrHospitalDoctor(models.Model):
    _inherit = "hr.hospital.doctor"

    intern_names = fields.Text(
        string="Interns",
        compute="_compute_intern_names",
    )

    @api.depends("intern_ids.name")
    def _compute_intern_names(self):
        for doctor in self:
            doctor.intern_names = "\n".join(doctor.intern_ids.mapped("name"))

    def action_print_doctor_report(self):
        self.ensure_one()
        return self.env.ref(
            "hr_hospital.action_report_hr_hospital_doctor"
        ).report_action(self)


class ReportHrHospitalDoctor(models.AbstractModel):
    _name = "report.hr_hospital.hr_hospital_doctor_report_template"
    _description = "Hospital Doctor PDF Report"

    def _get_visits_by_doctor(self, doctors):
        visits = self.env["hr.hospital.visit"].with_context(
            active_test=False
        ).search(
            [("doctor_id", "in", doctors.ids)],
            order="visit_date desc, id desc",
        )
        visits_by_doctor = defaultdict(list)
        visited_patients = defaultdict(set)
        latest_visits = {}
        for visit in visits:
            doctor_id = visit.doctor_id.id
            patient_id = visit.patient_id.id
            visits_by_doctor[doctor_id].append(visit)
            visited_patients[doctor_id].add(patient_id)
            latest_visits.setdefault((doctor_id, patient_id), visit)
        return visits, visits_by_doctor, visited_patients, latest_visits

    @api.model
    def _get_report_values(self, docids, data=None):
        doctors = self.env["hr.hospital.doctor"].browse(docids).exists()
        (
            visits,
            visits_by_doctor,
            visited_patients,
            latest_visits,
        ) = self._get_visits_by_doctor(doctors)
        patients = self.env["hr.hospital.patient"].search(
            [
                "|",
                ("doctor_id", "in", doctors.ids),
                ("id", "in", visits.mapped("patient_id").ids),
            ],
            order="name asc, id asc",
        )
        reports = []
        for doctor in doctors:
            patient_rows = [
                {
                    "patient": patient,
                    "last_visit": latest_visits.get((doctor.id, patient.id)),
                }
                for patient in patients
                if patient.doctor_id.id == doctor.id
                or patient.id in visited_patients[doctor.id]
            ]
            reports.append({
                "doctor": doctor,
                "visits": visits_by_doctor[doctor.id],
                "patient_rows": patient_rows,
            })

        printed_at = fields.Datetime.context_timestamp(
            self, fields.Datetime.now()
        ).strftime("%d.%m.%Y %H:%M")
        return {
            "doc_ids": doctors.ids,
            "doc_model": "hr.hospital.doctor",
            "docs": doctors,
            "reports": reports,
            "printed_at": printed_at,
        }
