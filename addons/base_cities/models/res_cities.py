from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResCities(models.Model):
    _name = 'res.country.state.cities'
    _description = 'Cities'
    _rec_name = 'display_name'
    _rec_name_search = ['name_en','name_ar']

    display_name = fields.Char(
        compute="_compute_display_name",
    )
    name_en = fields.Char(
        string='English Name',
        store=True,
        required=True
    )
    name_ar = fields.Char(
        string='Arabic Name',
        store=True,
        required=True
    )
    state_id = fields.Many2one(
        string="State",
        comodel_name='res.country.state',
    )

    @api.depends('name_en', 'name_ar')
    def _compute_display_name(self):
        lang = self.env.user.lang or 'en_US'
        is_ar = lang == 'ar_001'
        for rec in self:
            rec.display_name = rec.name_ar if is_ar else rec.name_en