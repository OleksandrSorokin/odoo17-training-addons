
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


class HrHospitalDiagnosis(models.Model):
    _name = "hr.hospital.diagnosis"
    _description = "Hospital Diagnosis"
    _rec_name = "disease_id"

    visit_id = fields.Many2one(
        comodel_name="hr.hospital.visit",
        string="Visit",
        required=True,
        ondelete="restrict",
        index=True,
    )

    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease",
        required=True,
        ondelete="restrict",
    )

    treatment_description = fields.Text(
        string="Treatment Prescription",
    )

    is_approved = fields.Boolean(
        string="Approved",
        default=False,
        readonly=True,
    )

    doctor_is_intern = fields.Boolean(
        related="visit_id.doctor_id.is_intern",
        string="Doctor Is Intern",
        readonly=True,
    )

    approved_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        readonly=True,
    )

    approved_at = fields.Datetime(
        string="Approved At",
        readonly=True,
    )

    def _check_mentor_permission(self):
        for diagnosis in self:
            doctor = diagnosis.visit_id.doctor_id

            if not doctor.is_intern:
                raise UserError(
                    "Mentor approval is only required for intern diagnoses."
                )

            mentor = doctor.mentor_id
            mentor_user = mentor.sudo().user_id if mentor else False

            if not mentor_user:
                raise UserError(
                    "The intern must have a mentor linked to an Odoo user."
                )

            if mentor_user.id != self.env.uid:
                raise AccessError(
                    "Only the assigned mentor can approve this diagnosis."
                )

    def action_approve(self):
        for diagnosis in self:
            if diagnosis.is_approved:
                continue

            diagnosis._check_mentor_permission()
            diagnosis.write({
                "is_approved": True,
                "approved_by_id": self.env.uid,
                "approved_at": fields.Datetime.now(),
            })

        return True

    @api.constrains("is_approved", "visit_id")
    def _check_approved_intern_diagnoses(self):
        for diagnosis in self:
            if diagnosis.is_approved and diagnosis.doctor_is_intern:
                diagnosis._check_mentor_permission()
