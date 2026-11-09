Partner Unique Email
====================

Odoo 17 add-on preventing multiple contacts (``res.partner``) from sharing
an email address. Matching ignores leading/trailing spaces and letter case.

Installation
------------

Install the module from Apps. If duplicate addresses already exist, the module
refuses installation and identifies the offending address. Clean existing
contacts, then retry. Empty email values are allowed.

The module uses both an ORM validation message and a unique PostgreSQL index,
so concurrent writes cannot bypass the rule. The rule applies to all partners,
including company contacts and archived records.

Testing
-------

Run with Odoo's ``--test-tags /partner_unique_email`` option. Cover duplicate
create, duplicate update, case-insensitive matching and missing addresses.

License: LGPL-3.
