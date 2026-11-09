from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHospitalDemoCompany(TransactionCase):
    """Do not recreate the demo company renamed by Module 5."""

    def test_existing_company_without_xml_id_is_skipped(self):
        company_model = self.env["res.company"].with_context(
            active_test=False
        )
        company = company_model.search([
            ("name", "=", "Odoo 17 Demo Hospital"),
        ], limit=1)
        if not company:
            company = company_model.create({
                "name": "Odoo 17 Demo Hospital",
            })

        loader = self.env["hr.hospital.load.demo.wizard"]
        self.assertTrue(loader._demo_file_exists(
            self.env,
            "demo/hr_hospital_demo_company.xml",
            "nonexistent_company_id_for_test",
        ))
        self.assertFalse(loader._demo_file_exists(
            self.env,
            "demo/not_a_company.xml",
            "nonexistent_company_id_for_test",
        ))
