from odoo import api, models, fields


class SportClubEquipmentBooking(models.Model):
    """
    Model: Equipment Booking
    ------------------------
    Represents an equipment rental line inside a reservation.
    """
    _name = "sport.club.equipment.booking"
    _description = "Equipment Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_equipment_product_domain(self):
        self.ensure_one()
        domain = [
            ('is_equipment', '=', True),
            ('club_id','=',self.reservation_id.club_id.id),
            ('sport_id','=',self.reservation_id.sport_id.id)
        ]
        return domain if self.reservation_id else []

    name = fields.Char(
        string="Equipment Booking Name",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    reservation_id = fields.Many2one(
        comodel_name="sport.club.reservation",
        string="Reservation",
        required=True,
        tracking=True,
    )
    equipment_product_id = fields.Many2one(
        comodel_name="product.template",
        string="Equipment",
        required=True,
        tracking=True,
    )
    qty = fields.Float(
        string="Quantity",
        required=True,
        tracking=True,
    )
    hours = fields.Float(
        string="Duration (Hours)",
        required=True,
        tracking=True,
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_price_subtotal",
        store=True,
        tracking=True,
        help="qty × hours × hourly price",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("qty", "hours", "equipment_product_id", "equipment_product_id.price_hour")
    def _compute_price_subtotal(self):
        for rec in self:
            subtotal = rec.qty * rec.hours * (rec.equipment_product_id.price_hour or 0.0)
            rec.price_subtotal = round(subtotal,2)