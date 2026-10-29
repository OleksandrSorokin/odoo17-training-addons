"""Load module 5 demonstration fixtures into the training database.

Run through Odoo shell from the repository root.
"""

import base64
from pathlib import Path

from odoo.modules.module import get_module_resource
from odoo.tools.convert import convert_file


DEMO_DATABASE = "odoo17_p1_dev"


def _fill_previous_demo(odoo_env):
    """Complete existing sample records without requiring them to exist."""
    patient_updates = (
        (
            "hr_hospital_patient_demo_1", "male",
            "1985-05-14", "+380 00 000 02 01",
        ),
        (
            "hr_hospital_patient_demo_2", "female",
            "1992-02-23", "+380 00 000 02 02",
        ),
        (
            "hr_hospital_patient_demo_3", "male",
            "1978-08-09", "+380 00 000 02 03",
        ),
    )
    for xmlid, gender, birth_date, phone in patient_updates:
        patient = odoo_env.ref(
            "hr_hospital." + xmlid, raise_if_not_found=False
        )
        if patient:
            patient.write({
                "gender": gender,
                "birth_date": birth_date,
                "phone": phone,
            })

    doctor_updates = (
        ("hr_hospital_doctor_demo_1", "+380 00 000 03 01"),
        ("hr_hospital_doctor_demo_2", "+380 00 000 03 02"),
        ("hr_hospital_doctor_demo_3", "+380 00 000 03 03"),
        ("hr_hospital_intern_demo_1", "+380 00 000 03 04"),
        ("hr_hospital_intern_demo_2", "+380 00 000 03 05"),
    )
    for xmlid, phone in doctor_updates:
        doctor = odoo_env.ref("hr_hospital." + xmlid, raise_if_not_found=False)
        if doctor:
            doctor.write({"phone": phone})


def load_module5_demo(odoo_env):
    """Import only module 5 fixtures and set a fictional training company."""
    if odoo_env.cr.dbname != DEMO_DATABASE:
        raise RuntimeError("Demo loading is restricted to odoo17_p1_dev.")

    convert_file(
        odoo_env,
        "hr_hospital",
        "demo/hr_hospital_module5_demo.xml",
        {},
        mode="update",
    )

    logo_path = get_module_resource(
        "hr_hospital", "static", "description", "demo_company_logo.png"
    )
    company = odoo_env.ref("base.main_company").sudo()
    company.write({
        "name": "Odoo 17 Demo Hospital",
        "street": "17 Training Street",
        "street2": "Training database only",
        "city": "Kyiv",
        "zip": "01001",
        "country_id": odoo_env.ref("base.ua").id,
        "state_id": False,
        "company_details": (
            "<div>Odoo 17 Demo Hospital<br/>"
            "17 Training Street<br/>Training database only<br/>"
            "01001 Kyiv<br/>Ukraine</div>"
        ),
        "phone": "+380 00 000 00 00",
        "email": "demo@example.com",
        "website": "https://example.com",
        "logo": base64.b64encode(Path(logo_path).read_bytes()),
    })
    company.partner_id.sudo().write({"state_id": False})
    _fill_previous_demo(odoo_env)
    odoo_env.cr.commit()
    print("MODULE 5 DEMO LOADED")
    print("Company:", company.name, "|", company.city)
    print("Doctors: Sofia Kovalenko, Maksym Honchar, Iryna Melnyk")
    print("Interns: Oksana Shevchenko, Nazar Boiko")
    print("New demo: 5 doctors (including 2 interns), 6 patients, 8 visits")
    print(
        "Previous demo: patient demographics and doctor phones "
        "completed where found"
    )
    print("Repeat run: existing demonstration records will not duplicate.")


load_module5_demo(globals()["env"])
