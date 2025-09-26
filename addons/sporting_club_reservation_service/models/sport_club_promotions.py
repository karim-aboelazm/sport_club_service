from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class SportClubPromotion(models.Model):
    _name = "sport.club.promotion"
    _description = "Sport Club Promotion"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ============================================================
    # Basic Information
    # ============================================================
    name = fields.Char(
        string="Promotion Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Promo Code",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Unique code players can enter during reservation.",
    )
    description = fields.Text(
        string="Description"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    # ============================================================
    # Discount Logic
    # ============================================================
    discount_type = fields.Selection(
        selection=[
            ("percent", "Percentage"),
            ("fixed", "Fixed Amount")
        ],
        string="Discount Type",
        required=True,
        default="percent",
        tracking=True,
    )
    discount_value = fields.Float(
        string="Discount Value",
        required=True,
        tracking=True,
        help="If percentage, enter 10 for 10%. If fixed, enter amount in company currency.",
    )
    # ============================================================
    # Currency
    # ============================================================
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        help="Currency for the pricing rule."
    )

    # ============================================================
    # Validity
    # ============================================================
    date_start = fields.Date(
        string="Valid From",
        tracking=True,
    )
    date_end = fields.Date(
        string="Valid Until",
        tracking=True,
    )
    usage_limit = fields.Integer(
        string="Max Usage",
        help="Maximum number of times this promo can be used (0 = unlimited).",
    )
    usage_count = fields.Integer(
        string="Times Used",
        readonly=True,
        tracking=True,
    )

    # ============================================================
    # Relations
    # ============================================================
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        required=True,
        tracking=True,
    )
    sport_ids = fields.Many2many(
        comodel_name="sport.club.sports",
        string="Applicable Sports",
    )
    facility_ids = fields.Many2many(
        comodel_name="sport.club.facility",
        string="Applicable Facilities",
    )

    # ============================================================
    # Compute & Constraints
    # ============================================================
    @api.constrains("discount_type", "discount_value")
    def _check_discount_value(self):
        for rec in self:
            if rec.discount_type == "percent" and not (0 < rec.discount_value <= 100):
                raise ValidationError("Percentage discount must be between 0 and 100.")
            if rec.discount_type == "fixed" and rec.discount_value < 0:
                raise ValidationError("Fixed discount must be a positive value.")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError("End date cannot be before start date.")

    # ============================================================
    # Helpers
    # ============================================================
    def is_valid(self):
        """Check if promotion is currently valid"""
        today = date.today()
        for rec in self:
            if not rec.active:
                return False
            if rec.date_start and today < rec.date_start:
                return False
            if rec.date_end and today > rec.date_end:
                return False
            if rec.usage_limit and rec.usage_count >= rec.usage_limit:
                return False
        return True

    def apply_discount(self, amount):
        """Return discounted amount based on type"""
        self.ensure_one()
        if not self.is_valid():
            return amount
        if self.discount_type == "percent":
            return amount * (1 - (self.discount_value / 100.0))
        elif self.discount_type == "fixed":
            return max(0.0, amount - self.discount_value)
        return amount
