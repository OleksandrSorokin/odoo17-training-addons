from odoo import SUPERUSER_ID, _, api, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.convert import convert_file


class HrHospitalLoadDemoWizard(models.TransientModel):
    """Load the module's XML demo fixtures from the Settings-level UI."""

    _name = "hr.hospital.load.demo.wizard"
    _description = "Load Hospital Demonstration Data"

    _demo_files = (
        ("demo/hr_hospital_demo.xml", "hr_hospital_doctor_demo_1"),
        (
            "demo/hr_hospital_disease_hierarchy_demo.xml",
            "disease_demo_respiratory",
        ),
        ("demo/hr_hospital_visit_demo.xml", "hr_hospital_visit_demo_1"),
        ("demo/hr_hospital_module4_demo.xml", "hr_hospital_intern_demo_1"),
        ("demo/hr_hospital_module5_demo.xml", "hr_hospital_m5_doctor_sophia"),
        ("demo/hr_hospital_demo_company.xml", "hr_hospital_demo_company"),
        (
            "demo/hr_hospital_security_demo.xml",
            "hr_hospital_demo_user_patient",
        ),
    )

    def _demo_file_exists(self, root_env, path, marker):
        """Skip existing XML IDs and legacy company-name collisions."""
        if root_env.ref(
            "hr_hospital.%s" % marker, raise_if_not_found=False
        ):
            return True

        if path == "demo/hr_hospital_demo_company.xml":
            return bool(root_env["res.company"].with_context(
                active_test=False
            ).search_count([
                ("name", "=", "Odoo 17 Demo Hospital"),
            ]))
        return False

    def action_load_demo(self):
        """Import missing fixture sets and leave existing records intact."""
        self.ensure_one()
        if not (
            self.env.is_superuser()
            or self.env.user.has_group("hr_hospital.group_hospital_admin")
        ):
            raise AccessError(
                _("Only hospital administrators can load demo data.")
            )

        if not self.env.context.get("hospital_confirm_demo"):
            raise UserError(
                _("Please confirm that this is a training database.")
            )

        root_env = api.Environment(self.env.cr, SUPERUSER_ID, self.env.context)
        loaded = 0
        skipped = 0
        for path, marker in self._demo_files:
            if self._demo_file_exists(root_env, path, marker):
                skipped += 1
                continue
            convert_file(root_env, "hr_hospital", path, {}, mode="init")
            loaded += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Hospital demo data"),
                "message": _(
                    "Loaded %(loaded)s sets; "
                    "skipped %(skipped)s existing sets."
                )
                % {"loaded": loaded, "skipped": skipped},
                "type": "success",
                "sticky": False,
            },
        }
