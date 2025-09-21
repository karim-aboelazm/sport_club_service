from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class ResState(models.Model):
    _inherit = 'res.country.state'
    _rec_name = 'display_name'

    display_name = fields.Char(
        compute="_compute_display_name",
    )
    name_ar = fields.Char(
        string=_('Arabic Name'),
    )

    @api.depends('name', 'name_ar')
    def _compute_display_name(self):
        lang = self.env.user.lang or 'en_US'
        is_ar = lang == 'ar_001'
        for rec in self:
            rec.display_name = rec.name
            if rec.name_ar and is_ar:
                rec.display_name = rec.name_ar


