
from odoo import api, fields, models


class HrHospitalPatient(models.Model):
    _name = "hr.hospital.patient"
    _inherit = "hr.hospital.person"
    _description = "Hospital Patient"

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Personal Doctor",
    )

    birth_date = fields.Date(
        string="Birth Date",
    )

    age = fields.Integer(
        string="Age",
        compute="_compute_age",
    )

    passport_data = fields.Text(
        string="Passport Details",
    )

    contact_person_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact Person",
    )

    @api.depends("birth_date")
    def _compute_age(self):
        today = fields.Date.context_today(self)

        for patient in self:
            if patient.birth_date:
                birth_date = patient.birth_date
                patient.age = (
                    today.year - birth_date.year
                    - ((today.month, today.day) < (birth_date.month, birth_date.day))
                )
            else:
                patient.age = 0
