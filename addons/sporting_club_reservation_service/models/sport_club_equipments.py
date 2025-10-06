from odoo import models, fields


class SportClubEquipmentProduct(models.Model):
    """
    Model: Club Equipment (as Product)
    ----------------------------------
    Extends Odoo's product.template to represent club equipment.
    Fully integrates with Odoo sales, rentals, and invoicing.
    """
    _inherit = "product.product"

    # ============================================================
    # Club & Sport Links
    # ============================================================
    is_equipment = fields.Boolean(
        string="Is Club Equipment",
        default=False,
        tracking=True,
        help="Mark this product as rentable equipment for a sports club.",
    )
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        tracking=True,
        help="The club that owns this equipment.",
    )
    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        tracking=True,
        help="The sport this equipment is associated with.",
    )

    # ============================================================
    # Rental Information
    # ============================================================
    price_hour = fields.Monetary(
        string="Hourly Rental Price",
        tracking=True,
        currency_field='currency_id',
        help="Rental price per hour for this equipment.",
    )
