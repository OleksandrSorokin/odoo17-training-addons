from odoo import fields, models


class HrHospitalPatient(models.Model):
    _name = "hr.hospital.patient"
    _description = "Hospital Patient"

    name = fields.Char(required=True)
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Attending Doctor",
    )
