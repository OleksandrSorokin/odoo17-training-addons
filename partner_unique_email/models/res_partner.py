from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """Enforce a unique, case-insensitive email across all partners."""

    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        """Check duplicates before the SQL unique constraint."""
        emails = [
            (vals.get("email") or "").strip().lower()
            for vals in vals_list
        ]
        existing = [email for email in emails if email]
        if len(existing) != len(set(existing)):
            raise ValidationError(
                _("Duplicate emails in the imported contacts.")
            )
        for email in existing:
            self._assert_unique_email(email)
        return super().create(vals_list)

    def write(self, vals):
        """Check edits against the whole contacts table, including archives."""
        if "email" in vals and vals["email"]:
            if len(self) > 1:
                raise ValidationError(_(
                    "The same email cannot be assigned to multiple contacts."
                ))
            self._assert_unique_email(vals["email"], self.ids)
        return super().write(vals)

    def _assert_unique_email(self, email, excluded_ids=None):
        """Match the same normalized expression as the unique SQL index."""
        normalized = (email or "").strip().lower()
        if not normalized:
            return
        self.env.cr.execute(
            """
            SELECT id
              FROM res_partner
             WHERE NOT (id = ANY(%s))
               AND lower(btrim(email)) = %s
             LIMIT 1
            """,
            [excluded_ids or [], normalized],
        )
        if self.env.cr.fetchone():
            raise ValidationError(_(
                "Another contact already uses this email address: "
                "%(email)s"
            ) % {"email": email})

    @api.constrains("email")
    def _check_unique_email(self):
        """Give a readable error before PostgreSQL raises its unique error."""
        for partner in self:
            email = (partner.email or "").strip().lower()
            if not email:
                continue
            self.env.cr.execute(
                """
                SELECT id
                  FROM res_partner
                 WHERE id <> %s
                   AND lower(btrim(email)) = %s
                 LIMIT 1
                """,
                [partner.id, email],
            )
            if self.env.cr.fetchone():
                raise ValidationError(_(
                    "Another contact already uses this email address: "
                    "%(email)s"
                ) % {"email": partner.email})

    def init(self):
        """Prevent concurrent transactions from inserting duplicate emails."""
        self.env.cr.execute(
            """
            SELECT lower(btrim(email)), count(*)
              FROM res_partner
             WHERE email IS NOT NULL AND btrim(email) <> ''
             GROUP BY lower(btrim(email))
            HAVING count(*) > 1
             LIMIT 1
            """
        )
        duplicate = self.env.cr.fetchone()
        if duplicate:
            raise ValidationError(_(
                "Cannot install Partner Unique Email. Existing partners "
                "share the address %(email)s (%(count)s records). "
                "Resolve duplicates first."
            ) % {"email": duplicate[0], "count": duplicate[1]})
        self.env.cr.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS partner_unique_email_ci_idx
                ON res_partner (lower(btrim(email)))
             WHERE email IS NOT NULL AND btrim(email) <> ''
            """
        )
