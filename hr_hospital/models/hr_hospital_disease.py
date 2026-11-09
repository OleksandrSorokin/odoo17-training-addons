from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDisease(models.Model):
    """Hierarchical diagnosis classifier with translatable labels."""

    _name = "hr.hospital.disease"
    _description = "Hospital Disease"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Parent Disease",
        ondelete="restrict",
        index=True,
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(
        comodel_name="hr.hospital.disease",
        inverse_name="parent_id",
        string="Subdiseases",
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        """Prevent recursion in the disease hierarchy."""
        if not self._check_recursion():
            raise ValidationError(_("A disease cannot be a parent of itself."))
