Hospital for Odoo 17
====================

Educational hospital management application developed across Odoo School
modules 2-6. Supports patients, doctors, interns, mentors, appointments,
diagnoses, disease hierarchies, analytical reports, PDF printing, and wizards.

User roles
----------

Roles form a chain: Patient -> Intern -> Doctor -> Manager -> Administrator.

* Patient: read own visits and diagnoses.
* Intern: read/create/edit visits and diagnoses assigned to their own doctor profile.
* Doctor: read/create/edit their visits and those of their mentored interns.
* Manager: see all visits and diagnoses; inherited doctor write access remains
  limited to doctor/mentee ownership.
* Administrator: full CRUD on hospital records, including deletion of
  diagnosed visits (their dependent diagnoses are deleted first).

The hospital user identity must be linked to a ``hr.hospital.patient`` record
for a patient or ``hr.hospital.doctor`` for a clinician. Use the Odoo User
field as a Settings administrator. A user without a matching profile is shown
no owned appointments. Hospital roles should be assigned to internal users.

Demo data
---------

Demo records are stored exclusively in ``demo/*.xml`` and loaded normally
when the database was created with demonstration data enabled. On an existing
training database an administrator with the Hospital Administrator role can
use Hospital -> Load Demo Data. That action imports missing fixture sets and
skips sets already represented by their XML IDs.

Demo user logins have ``@hospital.invalid`` suffixes and no assigned passwords.
Set their passwords via Settings -> Users before logging in as these users.
A fictional company is created as a **separate** res.company record. The
current main company is never overwritten.

Translation
-----------

Install/activate Ukrainian (uk_UA) in Settings -> Translations -> Languages,
then update Hospital or load ``i18n/uk_UA.po``. Disease labels are marked
``translate=True`` so their names can be localized.

Tests
-----

The tests do not depend on demo data. Run against a disposable database:

::

   odoo-bin -d odoo17_p1_test -u hr_hospital --test-tags /hr_hospital --stop-after-init

Tests cover age, mentors, visit conflicts, diagnoses, disease recursion and
all five role-based visibility rules. Validate menus and reports manually too.

Warning
-------

This is educational software, not a production medical-record solution.
It does not provide audit trails, consent, retention policies, or the security
reviews required for real patient data.

License: LGPL-3.
