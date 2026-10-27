from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Hospital Disease"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(required=True)
    parent_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Parent Disease",
        ondelete="restrict",
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        comodel_name="hr.hospital.disease",
        inverse_name="parent_id",
        string="Subdiseases",
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("A disease cannot be a parent of itself."))
