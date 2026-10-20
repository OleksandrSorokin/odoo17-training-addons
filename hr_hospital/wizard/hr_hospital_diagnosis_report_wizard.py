import calendar
from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDiagnosisReportWizard(models.TransientModel):
    _name = "hr.hospital.diagnosis.report.wizard"
    _description = "Diagnosis Report Wizard"

    doctor_ids = fields.Many2many(
        comodel_name="hr.hospital.doctor",
        string="Doctors (empty means all)",
    )
    disease_ids = fields.Many2many(
        comodel_name="hr.hospital.disease",
        string="Diseases (empty means all)",
    )
    date_from = fields.Date(
        string="Date From",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(
        string="Date To",
        required=True,
        default=lambda self: self._default_date_to(),
    )

    @api.model
    def _default_date_to(self):
        today = fields.Date.context_today(self)
        last_day = calendar.monthrange(today.year, today.month)[1]
        return today.replace(day=last_day)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wizard in self:
            if (
                wizard.date_from and wizard.date_to
                and wizard.date_from > wizard.date_to
            ):
                raise ValidationError(_("Date From cannot be later than Date To."))

    def action_show_report(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise ValidationError(_("Date From cannot be later than Date To."))

        tz = pytz.timezone(self.env.user.tz or "UTC")
        local_start = tz.localize(datetime.combine(self.date_from, time.min))
        next_day = self.date_to + timedelta(days=1)
        local_end = tz.localize(datetime.combine(next_day, time.min))
        utc_start = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
        utc_end = local_end.astimezone(pytz.UTC).replace(tzinfo=None)

        domain = [
            ("visit_id.visit_date", ">=", fields.Datetime.to_string(utc_start)),
            ("visit_id.visit_date", "<", fields.Datetime.to_string(utc_end)),
        ]
        if self.doctor_ids:
            domain.append(("visit_id.doctor_id", "in", self.doctor_ids.ids))
        if self.disease_ids:
            domain.append(("disease_id", "in", self.disease_ids.ids))

        list_view = self.env.ref("hr_hospital.hr_hospital_diagnosis_report_view_tree")
        form_view = self.env.ref("hr_hospital.hr_hospital_diagnosis_report_view_form")
        search_view = self.env.ref(
            "hr_hospital.hr_hospital_diagnosis_report_view_search"
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Diagnosis Report by Disease"),
            "res_model": "hr.hospital.diagnosis",
            "view_mode": "tree,form",
            "views": [(list_view.id, "tree"), (form_view.id, "form")],
            "search_view_id": search_view.id,
            "domain": domain,
            "context": {"search_default_group_by_disease": 1},
            "target": "current",
        }
