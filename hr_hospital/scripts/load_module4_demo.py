from odoo import fields


def load_demo(env):
    required = [
        "hr_hospital.hr_hospital_doctor_demo_1",
        "hr_hospital.hr_hospital_doctor_demo_2",
        "hr_hospital.hr_hospital_patient_demo_1",
        "hr_hospital.hr_hospital_patient_demo_2",
        "hr_hospital.hr_hospital_patient_demo_3",
        "hr_hospital.hr_hospital_disease_flu",
        "hr_hospital.hr_hospital_disease_pneumonia",
        "hr_hospital.hr_hospital_disease_migraine",
        "hr_hospital.disease_demo_respiratory",
        "hr_hospital.disease_demo_neurological",
        "hr_hospital.disease_demo_bronchitis",
        "hr_hospital.disease_demo_asthma",
        "hr_hospital.disease_demo_neuralgia",
        "hr_hospital.disease_demo_epilepsy",
    ]

    for xml_id in required:
        if not env.ref(xml_id, raise_if_not_found=False):
            raise RuntimeError(
                f"Missing {xml_id}; cannot load module 4 demo data safely."
            )

    samples = [
        ("hr_hospital_intern_demo_1", "Olivia Carter"),
        ("hr_hospital_intern_demo_2", "Noah Evans"),
    ]
    for xml_id, name in samples:
        if not env.ref(f"hr_hospital.{xml_id}", raise_if_not_found=False):
            if env["hr.hospital.doctor"].search_count([("name", "=", name)]):
                raise RuntimeError(
                    f"Doctor {name} exists without demo XML ID."
                )

    def ref(xml_id):
        return env.ref(f"hr_hospital.{xml_id}")

    def upsert(xml_id, model, values):
        existing = env.ref(f"hr_hospital.{xml_id}", raise_if_not_found=False)
        if existing:
            if existing._name != model:
                raise RuntimeError(f"Model mismatch for {xml_id}")
            print(f"EXISTS: {xml_id}")
            return existing
        record = env[model].create(values)
        env["ir.model.data"].sudo().create({
            "module": "hr_hospital",
            "name": xml_id,
            "model": model,
            "res_id": record.id,
            "noupdate": True,
        })
        print(f"CREATED: {xml_id} (id={record.id})")
        return record

    categories = [
        ("hr_hospital_disease_flu", "disease_demo_respiratory"),
        ("hr_hospital_disease_pneumonia", "disease_demo_respiratory"),
        ("hr_hospital_disease_migraine", "disease_demo_neurological"),
    ]
    for disease_xml_id, parent_xml_id in categories:
        disease = ref(disease_xml_id)
        if not disease.parent_id:
            disease.write({"parent_id": ref(parent_xml_id).id})
            print(f"CLASSIFIED: {disease_xml_id}")
        else:
            print(f"UNCHANGED: {disease_xml_id}")

    upsert("hr_hospital_intern_demo_1", "hr.hospital.doctor", {
        "name": "Olivia Carter",
        "specialty": "family",
        "is_intern": True,
        "mentor_id": ref("hr_hospital_doctor_demo_1").id,
    })
    upsert("hr_hospital_intern_demo_2", "hr.hospital.doctor", {
        "name": "Noah Evans",
        "specialty": "neurology",
        "is_intern": True,
        "mentor_id": ref("hr_hospital_doctor_demo_2").id,
    })

    visits = [
        (
            "hr_hospital_visit_demo_6", "hr_hospital_patient_demo_1",
            "hr_hospital_intern_demo_1", "disease_demo_bronchitis",
            "2026-10-27 10:00:00", "planned",
        ),
        (
            "hr_hospital_visit_demo_7", "hr_hospital_patient_demo_2",
            "hr_hospital_intern_demo_2", "disease_demo_neuralgia",
            "2026-10-28 13:00:00", "planned",
        ),
        (
            "hr_hospital_visit_demo_8", "hr_hospital_patient_demo_3",
            "hr_hospital_doctor_demo_1", "disease_demo_asthma",
            "2026-10-29 14:00:00", "planned",
        ),
        (
            "hr_hospital_visit_demo_9", "hr_hospital_patient_demo_1",
            "hr_hospital_doctor_demo_2", "disease_demo_epilepsy",
            "2026-10-30 16:00:00", "cancelled",
        ),
    ]
    for xml_id, patient, doctor, disease, date, state in visits:
        if not env.ref(f"hr_hospital.{xml_id}", raise_if_not_found=False):
            overlapping = env["hr.hospital.visit"].search([
                ("patient_id", "=", ref(patient).id),
                ("doctor_id", "=", ref(doctor).id),
                ("visit_date", "=", fields.Datetime.to_datetime(date)),
            ], limit=1)
            if overlapping:
                raise RuntimeError(
                    f"Visit for {xml_id} exists without demo XML ID"
                )
        upsert(xml_id, "hr.hospital.visit", {
            "patient_id": ref(patient).id,
            "doctor_id": ref(doctor).id,
            "disease_id": ref(disease).id,
            "visit_date": date,
            "state": state,
        })

    diagnoses = [
        (
            "hr_hospital_diagnosis_demo_8",
            "hr_hospital_visit_demo_6", "disease_demo_bronchitis",
            "Observe symptoms and hydration.",
        ),
        (
            "hr_hospital_diagnosis_demo_9",
            "hr_hospital_visit_demo_6", "disease_demo_asthma",
            "Review pulmonary function tests.",
        ),
        (
            "hr_hospital_diagnosis_demo_10",
            "hr_hospital_visit_demo_7", "disease_demo_neuralgia",
            "Evaluate neurological symptoms.",
        ),
        (
            "hr_hospital_diagnosis_demo_11",
            "hr_hospital_visit_demo_8", "disease_demo_asthma",
            "Recommend follow-up examination.",
        ),
        (
            "hr_hospital_diagnosis_demo_12",
            "hr_hospital_visit_demo_8", "disease_demo_bronchitis",
            "Monitor respiratory symptoms.",
        ),
        (
            "hr_hospital_diagnosis_demo_13",
            "hr_hospital_visit_demo_7", "disease_demo_epilepsy",
            "Document referral for reassessment.",
        ),
    ]
    for xml_id, visit, disease, prescription in diagnoses:
        if not env.ref(f"hr_hospital.{xml_id}", raise_if_not_found=False):
            duplicate = env["hr.hospital.diagnosis"].search([
                ("visit_id", "=", ref(visit).id),
                ("disease_id", "=", ref(disease).id),
            ], limit=1)
            if duplicate:
                raise RuntimeError(
                    f"Diagnosis {xml_id} exists without demo XML ID"
                )
        upsert(xml_id, "hr.hospital.diagnosis", {
            "visit_id": ref(visit).id,
            "disease_id": ref(disease).id,
            "treatment_description": prescription,
        })

    env.cr.commit()
    print("Module 4 demo import completed and committed.")
