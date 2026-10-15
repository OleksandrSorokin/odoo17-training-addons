{
    "name": "Hospital",
    "summary": "Hospital management",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "author": "Oleksandr Sorokin",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_hospital_disease_data.xml",
        "views/hr_hospital_doctor_views.xml",
        "views/hr_hospital_patient_views.xml",
        "views/hr_hospital_disease_views.xml",
        "views/hr_hospital_visit_views.xml",
        "views/hr_hospital_menu.xml",
    ],
    "demo": [
        "demo/hr_hospital_demo.xml",
    ],
    "application": True,
    "installable": True,
}
