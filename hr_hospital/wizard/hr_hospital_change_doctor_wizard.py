from odoo import _, fields, models
from odoo.exceptions import UserError


class HrHospitalChangeDoctorWizard(models.TransientModel):
    _name = "hr.hospital.change.doctor.wizard"
    _description = "Mass Change of Personal Doctor"

    patient_ids = fields.Many2many(
        comodel_name="hr.hospital.patient",
        string="Selected Patients",
        required=True,
        readonly=True,
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="New Personal Doctor",
        required=True,
    )

    def action_apply(self):
        self.ensure_one()
        patients = self.patient_ids.exists()
        if not patients:
            raise UserError(_("Select at least one patient."))
        if not self.doctor_id:
            raise UserError(_("Select the new personal doctor."))
        patients.write({"doctor_id": self.doctor_id.id})
        return {
            "type": "ir.actions.act_window",
            "name": _("Updated Patients"),
            "res_model": "hr.hospital.patient",
            "view_mode": "tree,form",
            "domain": [("id", "in", patients.ids)],
            "target": "current",
        }
