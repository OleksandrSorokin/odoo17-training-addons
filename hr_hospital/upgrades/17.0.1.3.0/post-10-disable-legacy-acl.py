"""Retire broad hospital ACLs introduced by earlier training modules."""

import logging

_logger = logging.getLogger(__name__)

LEGACY_ACCESS_XMLIDS = (
    "access_hr_hospital_doctor",
    "access_hr_hospital_patient",
    "access_hr_hospital_disease",
    "access_hr_hospital_visit",
    "access_hr_hospital_diagnosis",
    "access_hr_hospital_change_doctor_wizard",
    "access_hr_hospital_diagnosis_report_wizard",
)


def migrate(cr, version):
    """Deactivate only old ACLs owned by hr_hospital for Internal User."""
    cr.execute(
        """
        UPDATE ir_model_access AS access
           SET active = FALSE
          FROM ir_model_data AS access_xmlid,
               ir_model_data AS group_xmlid
         WHERE access.id = access_xmlid.res_id
           AND access_xmlid.model = 'ir.model.access'
           AND access_xmlid.module = 'hr_hospital'
           AND access_xmlid.name = ANY(%s)
           AND group_xmlid.model = 'res.groups'
           AND group_xmlid.module = 'base'
           AND group_xmlid.name = 'group_user'
           AND access.group_id = group_xmlid.res_id
           AND access.active
        """,
        [list(LEGACY_ACCESS_XMLIDS)],
    )

    _logger.info("Hospital %s: disabled %s old ACLs", version, cr.rowcount)
