from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Reservation(models.Model):
    _name = "sport.club.reservation"
    _description = "Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ============================================================
    # Basic Information
    # ============================================================
    active = fields.Boolean(
        string="Active",
        default=True
    )
    name = fields.Char(
        string="Reservation Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Reservation Code",
        copy=False,
        index=True,
        tracking=True,
        help="Unique code for reservation identification.",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("confirmed", "Confirmed"),
            ("checked_in", "Checked In"),
            ("checked_out", "Checked Out"),
            ("cancelled", "Cancelled"),
            ("no_show", "No Show"),
            ("refunded", "Refunded"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    source = fields.Selection(
        selection=[
            ("backend", "Backend"),
            ("portal", "Portal"),
            ("app", "App")
        ],
        string="Booking Source",
        default="backend",
        tracking=True,
    )

    # ============================================================
    # Player & Club
    # ============================================================
    player_id = fields.Many2one(
        comodel_name="res.partner",
        string="Player",
        domain=[("is_player", "=", True)],
        tracking=True,
    )
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        required=True,
        tracking=True,
    )
    facility_id = fields.Many2one(
        comodel_name="sport.club.facility",
        string="Facility",
        required=True,
        tracking=True,
    )
    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        tracking=True,
    )

    # ============================================================
    # Scheduling
    # ============================================================
    date_start = fields.Datetime(
        string="Start Time",
        required=True,
        tracking=True,
    )
    date_end = fields.Datetime(
        string="End Time",
        required=True,
        tracking=True,
    )
    duration_hours = fields.Float(
        string="Duration (Hours)",
        compute="_compute_duration",
        store=True,
        help="Automatically calculated as End - Start in hours.",
    )

    # ============================================================
    # Financials
    # ============================================================
    price_hour = fields.Monetary(
        string="Hourly Price",
        tracking=True,
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        tracking=True,
        help="Automatically calculated: duration_hours × price_hour",
    )
    amount_equipment = fields.Monetary(
        string="Equipment Total",
        tracking=True,
    )
    amount_trainer = fields.Monetary(
        string="Trainer Fee",
        tracking=True,
    )
    # promo_id = fields.Many2one(
    #     comodel_name="sport.club.promotion",
    #     string="Promotion Applied",
    # )
    tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Taxes",
        tracking=True,
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_totals",
        store=True,
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        compute="_compute_totals",
        store=True,
        tracking=True,
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        compute="_compute_totals",
        store=True,
        tracking=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        tracking=True,
        default=lambda self: self.env.company.currency_id,
    )

    payment_state = fields.Selection(
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partially Paid"),
            ("paid", "Paid"),
            ("refunded", "Refunded"),
        ],
        string="Payment Status",
        default="unpaid",
        tracking=True,
    )
    # payment_transaction_ids = fields.One2many(
    #     comodel_name="payment.transaction",
    #     inverse_name="reservation_id",
    #     string="Transactions"
    # )

    # ============================================================
    # QR / Tracking
    # ============================================================
    qr_image = fields.Binary(
        string="QR Code",
        tracking=True
    )
    qr_payload = fields.Char(
        string="QR Payload",
        tracking=True
    )
    notes = fields.Text(
        string="Notes",
        tracking=True
    )

    # ============================================================
    # Relations
    # ============================================================
    equipment_line_ids = fields.One2many(
        comodel_name="sport.club.equipment.booking",
        inverse_name="reservation_id",
        string="Equipment Bookings",
    )
    trainer_id = fields.Many2one(
        comodel_name="sport.club.trainer",
        string="Trainer",
        tracking=True
    )
    policy_id = fields.Many2one(
        comodel_name="sport.club.policy",
        string="Cancellation Policy",
        tracking=True
    )

    # ============================================================
    # Check-in/out
    # ============================================================
    checkin_at = fields.Datetime(
        string="Check-in At",
        tracking=True
    )
    checkout_at = fields.Datetime(
        string="Check-out At",
        tracking=True
    )

    # ============================================================
    # Multi-company
    # ============================================================
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        tracking=True
    )

    # ============================================================
    # Compute Methods
    # ============================================================
    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                delta = rec.date_end - rec.date_start
                rec.duration_hours = delta.total_seconds() / 3600.0
            else:
                rec.duration_hours = 0.0

    @api.depends("duration_hours", "price_hour")
    def _compute_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.duration_hours * rec.price_hour if rec.duration_hours and rec.price_hour else 0.0

    @api.depends("price_subtotal", "amount_equipment", "amount_trainer", "tax_id")
    def _compute_totals(self):
        for rec in self:
            base = rec.price_subtotal + rec.amount_equipment + rec.amount_trainer
            taxes_res = rec.tax_id.compute_all(base, rec.currency_id) if rec.tax_id else {"taxes": [], "total_included": base, "total_excluded": base}
            rec.amount_untaxed = taxes_res["total_excluded"]
            rec.amount_tax = sum(t.get("amount", 0.0) for t in taxes_res["taxes"])
            rec.amount_total = taxes_res["total_included"]

    # ============================================================
    # Constraints
    # ============================================================
    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end <= rec.date_start:
                raise ValidationError("Reservation end time must be after start time.")
