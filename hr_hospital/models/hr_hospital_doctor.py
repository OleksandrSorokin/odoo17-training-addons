
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDoctor(models.Model):
    _name = "hr.hospital.doctor"
    _inherit = "hr.hospital.person"
    _description = "Hospital Doctor"

    specialty = fields.Selection(
        selection=[
            ("family", "Family Medicine"),
            ("cardiology", "Cardiology"),
            ("neurology", "Neurology"),
            ("pediatrics", "Pediatrics"),
        ],
        string="Specialty",
    )

    is_intern = fields.Boolean(
        string="Intern",
        default=False,
    )

    mentor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Mentor",
        domain=[("is_intern", "=", False)],
        ondelete="restrict",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Odoo User",
        ondelete="restrict",
        groups="base.group_system",
    )
    @api.constrains("is_intern", "mentor_id")
    def _check_mentor(self):
        for doctor in self:
            if doctor.mentor_id:
                if not doctor.is_intern:
                    raise ValidationError(
                        "Only interns can have a mentor."
                    )

                if doctor.mentor_id == doctor:
                    raise ValidationError(
                        "A doctor cannot be their own mentor."
                    )

                if doctor.mentor_id.is_intern:
                    raise ValidationError(
                        "An intern cannot be a mentor."
                    )

            if doctor.is_intern and self.search_count([
                ("mentor_id", "=", doctor.id),
            ]):
                raise ValidationError(
                    "A mentor with assigned interns cannot become an intern."
                )
