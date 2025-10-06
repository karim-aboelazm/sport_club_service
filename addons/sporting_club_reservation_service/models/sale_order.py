from odoo import models,fields

class SaleOrder(models.Model):
    _inherit='sale.order'

    reservation_id = fields.Many2one(
        comodel_name="sport.club.reservation",
        string="Reservation",
    )