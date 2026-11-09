# Odoo 17 Training Addons

Odoo School modules 1-6, finished on 2026-11-09.

## Environment

- Odoo 17, Ubuntu 22.04 / WSL2, PostgreSQL 14.
- Project 1: port 15069; Project 2: port 15070.
- OCA/web 17.0 for compatible third-party addons.

## Addons

- `hr_hospital`: hospital workflow, role-based access, Ukrainian translation,
  XML demo fixtures, reporting, wizards and ORM tests.
- `partner_unique_email`: independent contacts addon with a unique email rule,
  Odoo Apps landing page, icon/banner, and ORM tests.

## Install and test

Use a **test** Odoo database. First, update the Apps list. Install or upgrade
`hr_hospital` and `partner_unique_email` from Apps.

For old databases without sample data, assign Hospital Administrator to your
internal user and select **Hospital → Load Demo Data**. Do not do this in a
production database. On new databases, enable demonstration data during
creation so Odoo loads the `demo/*.xml` files automatically.

To run tests from a configured Odoo instance, use `--test-tags /hr_hospital`
and `--test-tags /partner_unique_email` with `--stop-after-init`.

Read each module's `README.rst` and `changelog.rst` for details.

## Git workflow

Use a feature branch for module 6, run `git diff --check` and
`odoo-helper lint pylint .` / `odoo-helper lint flake8 .`, then submit a PR.
The `partner_unique_email` directory is ready to be copied into a separate
private repository for registration on Odoo Apps. Marketplace publication
requires the author's own GitHub/Odoo Apps account configuration.
