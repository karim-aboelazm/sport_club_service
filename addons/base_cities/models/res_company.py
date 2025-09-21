from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one(
        string='City',
        comodel_name='res.country.state.cities',
        domain="[('state_id','=?',state_id)]"
    )
