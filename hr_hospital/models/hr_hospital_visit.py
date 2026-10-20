
from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrHospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _description = "Hospital Visit"

    active = fields.Boolean(default=True)

    state = fields.Selection(
        selection=[
            ("planned", "Planned"),
            ("done", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        default="planned",
    )

    visit_date = fields.Datetime(
        string="Scheduled Date",
        required=True,
        default=fields.Datetime.now,
    )

    actual_visit_date = fields.Datetime(
        string="Actual Visit Date",
    )

    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient",
        required=True,
    )

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Doctor",
        required=True,
    )

    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease (Legacy)",
    )

    diagnosis_ids = fields.One2many(
        comodel_name="hr.hospital.diagnosis",
        inverse_name="visit_id",
        string="Diagnoses",
    )

    @api.constrains("state", "actual_visit_date")
    def _check_actual_date(self):
        for visit in self:
            if visit.state == "done" and not visit.actual_visit_date:
                raise ValidationError(
                    "Completed visits must have an actual visit date."
                )

    @api.constrains("patient_id", "doctor_id", "visit_date", "state", "active")
    def _check_duplicate_visit(self):
        for visit in self:
            if not visit.active or visit.state == "cancelled":
                continue

            if not visit.patient_id or not visit.doctor_id or not visit.visit_date:
                continue

            timezone_name = self.env.company.partner_id.tz or "UTC"
            clinic_tz = pytz.timezone(timezone_name)

            visit_utc = pytz.UTC.localize(
                fields.Datetime.to_datetime(visit.visit_date)
            )
            visit_day = visit_utc.astimezone(clinic_tz).date()

            day_start = clinic_tz.localize(
                datetime.combine(visit_day, time.min)
            )
            day_end = clinic_tz.localize(
                datetime.combine(visit_day + timedelta(days=1), time.min)
            )

            start_utc = day_start.astimezone(pytz.UTC).replace(tzinfo=None)
            end_utc = day_end.astimezone(pytz.UTC).replace(tzinfo=None)

            duplicate = self.search_count([
                ("id", "!=", visit.id),
                ("active", "=", True),
                ("state", "!=", "cancelled"),
                ("patient_id", "=", visit.patient_id.id),
                ("doctor_id", "=", visit.doctor_id.id),
                ("visit_date", ">=", start_utc),
                ("visit_date", "<", end_utc),
            ])

            if duplicate:
                raise ValidationError(
                    "This patient already has an appointment "
                    "with this doctor on the selected day."
                )

    def write(self, vals):
        protected_fields = {
            "state", "visit_date", "actual_visit_date", "doctor_id"
        }

        if protected_fields.intersection(vals):
            if any(visit.state == "done" for visit in self):
                raise UserError(
                    "You cannot change the date, doctor or status "
                    "of a completed visit."
                )

        if vals.get("active") is False:
            if any(visit.diagnosis_ids for visit in self):
                raise UserError(
                    "You cannot archive a visit that has diagnoses."
                )

        return super().write(vals)

    def unlink(self):
        if any(visit.diagnosis_ids for visit in self):
            raise UserError(
                "You cannot delete a visit that has diagnoses."
            )

        return super().unlink()
