from odoo import api, fields, models


class HrHospitalPatient(models.Model):
    _name = "hr.hospital.patient"
    _inherit = "hr.hospital.person"
    _description = "Hospital Patient"

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Personal Doctor",
    )
    birth_date = fields.Date()
    age = fields.Integer(compute="_compute_age")
    passport_data = fields.Text(string="Passport Details")
    contact_person_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact Person",
    )
    visit_ids = fields.One2many(
        comodel_name="hr.hospital.visit",
        inverse_name="patient_id",
        string="Visits",
    )
    diagnosis_ids = fields.Many2many(
        comodel_name="hr.hospital.diagnosis",
        compute="_compute_diagnosis_ids",
        string="Diagnosis History",
    )

    @api.depends("birth_date")
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for patient in self:
            if patient.birth_date:
                birth_date = patient.birth_date
                patient.age = (
                    today.year - birth_date.year
                    - ((today.month, today.day) < (
                        birth_date.month, birth_date.day
                    ))
                )
            else:
                patient.age = 0

    @api.depends("visit_ids.diagnosis_ids")
    def _compute_diagnosis_ids(self):
        for patient in self:
            patient.diagnosis_ids = patient.visit_ids.mapped("diagnosis_ids")

    def action_show_visits(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Patient Visits",
            "res_model": "hr.hospital.visit",
            "view_mode": "tree,calendar,form",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
            "target": "current",
        }

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
            "context": {
                "default_patient_id": self.id,
                "default_doctor_id": self.doctor_id.id or False,
            },
        }
