import werkzeug
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = "res.users"

    is_club_owner = fields.Boolean(
        string="Is Club Owner ?",
        default=False,
        help="Check if this contact is an owner of a sporting club."
    )
    access_token_ids = fields.One2many(
        string='Access Tokens',
        comodel_name='jwt_provider.access_token',
        inverse_name='user_id',
    )
    avatar = fields.Char(
        compute='_compute_avatar'
    )

    def _compute_avatar(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for u in self:
            u.avatar = werkzeug.urls.url_join(base, 'web/avatar/%d' % u.id)

    def to_dict(self, single=False):
        res = []
        for u in self:
            d = u.read(['email', 'name', 'avatar', 'company_id'])[0]
            res.append(d)

        return res[0] if single else res