from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrHospitalVisit(models.Model):
    """Appointment with patient/doctor ownership and clinical validations."""

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
        index=True,
    )
    actual_visit_date = fields.Datetime()
    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient",
        required=True,
        ondelete="restrict",
        index=True,
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Doctor",
        required=True,
        ondelete="restrict",
        index=True,
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

    @api.depends("patient_id.name", "doctor_id.name")
    def _compute_display_name(self):
        """Build a readable caption for visit selectors and calendar views."""
        for visit in self:
            visit.display_name = " | ".join(filter(None, [
                visit.patient_id.name,
                visit.doctor_id.name,
            ])) or _("New Visit")

    @api.constrains("state", "actual_visit_date")
    def _check_actual_date(self):
        """Allow an actual visit date only on completed appointments."""
        for visit in self:
            if visit.state == "done" and not visit.actual_visit_date:
                raise ValidationError(
                    _("Completed visits must have an actual visit date.")
                )
            if visit.state != "done" and visit.actual_visit_date:
                raise ValidationError(
                    _("Only completed visits can have an actual visit date.")
                )

    @api.constrains("patient_id", "doctor_id", "visit_date", "state", "active")
    def _check_duplicate_visit(self):
        """Disallow the same doctor/patient pair twice per clinic-local day."""
        timezone_name = self.env.company.partner_id.tz or "UTC"
        clinic_tz = pytz.timezone(timezone_name)
        for visit in self:
            if not visit.active or visit.state == "cancelled":
                continue
            if not (visit.patient_id and visit.doctor_id and visit.visit_date):
                continue

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
                raise ValidationError(_(
                    "This patient already has an appointment "
                    "with this doctor on the selected day."
                ))

    def write(self, vals):
        """Protect completed visits and diagnosed appointments."""
        protected_fields = {
            "state", "visit_date", "actual_visit_date", "doctor_id"
        }
        if protected_fields.intersection(vals) and any(
            visit.state == "done" for visit in self
        ):
            raise UserError(_(
                "You cannot change the date, doctor or status "
                "of a completed visit."
            ))
        if vals.get("active") is False and any(
            visit.diagnosis_ids for visit in self
        ):
            raise UserError(
                _("You cannot archive a visit that has diagnoses.")
            )
        return super().write(vals)

    def unlink(self):
        """Let hospital administrators remove diagnosed visits explicitly."""
        if any(visit.diagnosis_ids for visit in self):
            if not (
                self.env.is_superuser()
                or self.env.user.has_group("hr_hospital.group_hospital_admin")
            ):
                raise UserError(
                    _("You cannot delete a visit that has diagnoses.")
                )
            self.mapped("diagnosis_ids").unlink()
        return super().unlink()
