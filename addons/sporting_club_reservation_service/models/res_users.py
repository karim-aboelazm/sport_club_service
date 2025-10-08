from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit='res.users'

    is_club_owner = fields.Boolean(
        string="Is Club Owner ?",
        default=False,
        help="Check if this contact is an owner of a sporting club."
    )