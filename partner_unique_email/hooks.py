"""Lifecycle hooks for the custom contact email database index."""


def uninstall_hook(env):
    """Restore ordinary Odoo contact behavior when the addon is removed."""
    env.cr.execute("DROP INDEX IF EXISTS partner_unique_email_ci_idx")
