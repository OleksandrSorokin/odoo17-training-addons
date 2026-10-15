from odoo import fields, models


class HrHospitalDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Hospital Disease"

    name = fields.Char(required=True)
