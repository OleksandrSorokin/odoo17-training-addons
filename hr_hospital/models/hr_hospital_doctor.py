from odoo import _, api, fields, models
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
    )
    is_intern = fields.Boolean(string="Intern", default=False)
    mentor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Mentor",
        domain=[("is_intern", "=", False)],
        ondelete="restrict",
    )
    intern_ids = fields.One2many(
        comodel_name="hr.hospital.doctor",
        inverse_name="mentor_id",
        string="Interns",
    )
    mentor_phone = fields.Char(
        related="mentor_id.phone",
        string="Mentor Phone",
        readonly=True,
    )
    mentor_specialty = fields.Selection(
        related="mentor_id.specialty",
        string="Mentor Specialty",
        readonly=True,
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
                    raise ValidationError(_("Only interns can have a mentor."))
                if doctor.mentor_id == doctor:
                    raise ValidationError(
                        _("A doctor cannot be their own mentor.")
                    )
                if doctor.mentor_id.is_intern:
                    raise ValidationError(_("An intern cannot be a mentor."))

            if doctor.is_intern and self.search_count([
                ("mentor_id", "=", doctor.id),
            ]):
                raise ValidationError(
                    _(
                        "A mentor with assigned interns cannot become "
                        "an intern."
                    )
                )

    def action_schedule_visit(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Schedule Visit",
            "res_model": "hr.hospital.visit",
            "view_mode": "form",
            "view_id": self.env.ref(
                "hr_hospital.hr_hospital_visit_view_form"
            ).id,
            "target": "new",
            "context": {"default_doctor_id": self.id},
        }
