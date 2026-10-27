from odoo import api, fields, models


class HrHospitalDiagnosisReport(models.Model):
    _inherit = "hr.hospital.diagnosis"

    doctor_id = fields.Many2one(
        related="visit_id.doctor_id",
        string="Doctor",
        readonly=True,
        store=True,
    )
    patient_id = fields.Many2one(
        related="visit_id.patient_id",
        string="Patient",
        readonly=True,
        store=True,
    )
    visit_date = fields.Datetime(
        related="visit_id.visit_date",
        string="Scheduled Date",
        readonly=True,
        store=True,
        index=True,
    )
    disease_type_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease Type",
        compute="_compute_disease_type_id",
        readonly=True,
        store=True,
    )

    @api.depends("disease_id", "disease_id.parent_id")
    def _compute_disease_type_id(self):
        for diagnosis in self:
            diagnosis.disease_type_id = (
                diagnosis.disease_id.parent_id or diagnosis.disease_id
            )
