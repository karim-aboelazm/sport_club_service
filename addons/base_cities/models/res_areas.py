from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResAreas(models.Model):
    _name = 'res.country.state.cities.areas'
    _description = 'Areas'
    _rec_name = 'name'

    name = fields.Char(
        string='Area Name',
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

