from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _rec_name_search = ['name', 'mobile', 'email', 'state_id', 'country_id', 'city_id', 'city_id','area_id','zone_id']

    city_id = fields.Many2one(
        string='City',
        comodel_name='res.country.state.cities',
        domain="[('state_id','=?',state_id)]"
    )
    area_id = fields.Many2one(
        string='Area',
        comodel_name='res.country.state.cities.areas',
        domain="[('city_id','=?',city_id)]"
    )
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='res.country.state.cities.areas.zones',
        domain="[('area_id','=?',area_id)]"
    )

