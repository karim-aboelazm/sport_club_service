from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResZones(models.Model):
    _name = 'res.country.state.cities.areas.zones'
    _description = 'Zones'
    _rec_name = 'name'

    name = fields.Char(
        string='Zone Name',
        required=True
    )
    state_id = fields.Many2one(
        string="Governorate",
        comodel_name='res.country.state',
    )
    city_id = fields.Many2one(
        string="City",
        comodel_name='res.country.state.cities',
        domain="[('state_id','=?',state_id)]",
    )
    area_id = fields.Many2one(
        string="Area",
        comodel_name='res.country.state.cities.areas',
        domain="[('city_id','=?',city_id)]",
    )

