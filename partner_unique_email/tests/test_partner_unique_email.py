from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUniquePartnerEmail(TransactionCase):
    """Validate duplicate protection on create, write, and empty values."""

    def test_case_and_whitespace_are_ignored(self):
        """Emails that differ only in capitalization and spaces are equal."""
        self.env["res.partner"].create({
            "name": "First Contact",
            "email": "first.unique@example.invalid",
        })
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["res.partner"].create({
                "name": "Duplicate Contact",
                "email": " FIRST.UNIQUE@EXAMPLE.INVALID ",
            })

    def test_update_cannot_duplicate(self):
        """An edited partner must not take another contact's address."""
        self.env["res.partner"].create({
            "name": "First Contact",
            "email": "write.unique@example.invalid",
        })
        second = self.env["res.partner"].create({
            "name": "Second Contact",
        })
        with self.assertRaises(ValidationError), self.cr.savepoint():
            second.email = "WRITE.UNIQUE@EXAMPLE.INVALID"

    def test_empty_emails_are_allowed(self):
        """Partners without an email are not treated as duplicates."""
        for name in ("No Email One", "No Email Two"):
            self.env["res.partner"].create({"name": name})
