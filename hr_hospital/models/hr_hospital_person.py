from odoo import fields, models


class HrHospitalPerson(models.AbstractModel):
    """Shared personal details for patients and doctors."""
    _name = "hr.hospital.person"
    _description = "Hospital Person"

    name = fields.Char(string="Full Name", required=True)
    first_name = fields.Char()
    last_name = fields.Char()
    phone = fields.Char()
    image_1920 = fields.Image(string="Photo")
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
    )
