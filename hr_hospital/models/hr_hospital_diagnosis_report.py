from odoo import fields, models


class HrHospitalDiagnosisReport(models.Model):
    _inherit = "hr.hospital.diagnosis"

    doctor_id = fields.Many2one(
        related="visit_id.doctor_id",
        string="Doctor",
        readonly=True,
    )
    patient_id = fields.Many2one(
        related="visit_id.patient_id",
        string="Patient",
        readonly=True,
    )
    visit_date = fields.Datetime(
        related="visit_id.visit_date",
        string="Scheduled Date",
        readonly=True,
    )
