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
    _order = 'id,sequence'

    def _get_equipment_product_domain(self):
        self.ensure_one()
        domain = [
            ('is_equipment', '=', True),
            ('club_id','=',self.reservation_id.club_id.id),
            ('sport_id','=',self.reservation_id.sport_id.id)
        ]
        return domain if self.reservation_id else []

    sequence = fields.Integer(
        help='Used to order Journals in the dashboard view',
        default=10
    )
    name = fields.Char(
        string="Equipment Booking Name",
        compute='_compute_name',
        readonly=False
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
        comodel_name="product.product",
        string="Equipment",
        tracking=True,
    )
    qty = fields.Float(
        string="Quantity",
        tracking=True,
    )
    hours = fields.Float(
        string="Duration (Hours)",
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
        default=lambda self: self.env.company.currency_id,
    )
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False
    )
    @api.depends('equipment_product_id')
    def _compute_name(self):
        for rec in self:
            rec.name = ''
            if rec.equipment_product_id:
                if rec.equipment_product_id.description_sale:
                    rec.name = rec.equipment_product_id.description_sale
                else:
                    rec.name = rec.equipment_product_id.display_name

    @api.depends("qty", "hours", "equipment_product_id", "equipment_product_id.price_hour")
    def _compute_price_subtotal(self):
        for rec in self:
            subtotal = rec.qty * rec.hours * (rec.equipment_product_id.price_hour or 0.0)
            rec.price_subtotal = round(subtotal,2)

    @api.onchange('display_type')
    def _onchange_display_type(self):
        for rec in self:
            if rec.display_type:
                rec.equipment_product_id = False
                rec.qty = 0.0
                rec.hours = 0.0
                rec.price_subtotal = 0.0
