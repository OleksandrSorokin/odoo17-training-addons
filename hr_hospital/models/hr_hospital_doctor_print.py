from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class HrHospitalDoctor(models.Model):
    """Doctor helpers used by PDF reporting."""
    _inherit = "hr.hospital.doctor"

    intern_heading = fields.Char(compute="_compute_intern_heading")

    intern_names = fields.Text(
        compute="_compute_intern_names",
    )

    @api.depends("intern_ids.name")
    def _compute_intern_names(self):
        """Show mentor intern names on the doctor card."""
        for doctor in self:
            doctor.intern_names = "\n".join(doctor.intern_ids.mapped("name"))

    @api.depends_context("lang")
    def _compute_intern_heading(self):
        for doctor in self:
            doctor.intern_heading = _("Interns:")

    def action_print_doctor_report(self):
        """Print the report for staff with doctor-level privileges."""
        self.ensure_one()
        if not (self.env.is_superuser() or self.env.user.has_group(
            "hr_hospital.group_hospital_doctor"
        )):
            raise AccessError(_("Only doctors can print this report."))
        return self.env.ref(
            "hr_hospital.action_report_hr_hospital_doctor"
        ).report_action(self)


class ReportHrHospitalDoctor(models.AbstractModel):
    """Aggregated doctor report QWeb data provider."""
    _name = "report.hr_hospital.hr_hospital_doctor_report_template"
    _description = "Hospital Doctor PDF Report"

    def _get_visits_by_doctor(self, doctors):
        """Collect all visits and latest patient visits per doctor."""
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
        """Build the input dictionary used by QWeb."""
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
