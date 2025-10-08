import random
import string
from datetime import datetime, date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
        readonly=True,  # Make the field readonly to prevent manual changes
        default='New',  # Set a default value before code generation
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
    date_start = fields.Datetime(
        string="Valid From",
        tracking=True,
    )
    date_end = fields.Datetime(
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
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this calendar template in views "
             "(e.g., calendar or kanban)."
    )
    # ============================================================
    # Constraints / Validations
    # ============================================================
    @api.constrains("discount_type", "discount_value")
    def _check_discount_value(self):
        for rec in self:
            if rec.discount_type == "percent" and not (0 < rec.discount_value <= 100):
                raise ValidationError("Percentage discount must be between 0 and 100.")
            if rec.discount_type == "fixed" and rec.discount_value <= 0:
                raise ValidationError("Fixed discount must be a positive value.")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError("End date cannot be before start date.")

    @api.constrains("usage_limit", "usage_count")
    def _check_usage(self):
        for rec in self:
            if rec.usage_limit < 0:
                raise ValidationError("Promotion Usage limit cannot be negative.")
            if rec.usage_count < 0:
                raise ValidationError("Promotion Usage count cannot be negative.")
            if rec.usage_limit and rec.usage_count > rec.usage_limit:
                raise ValidationError("Promotion Usage count cannot exceed usage limit.")

    @api.constrains("code")
    def _check_code_unique(self):
        for rec in self:
            if rec.code and rec.code != 'New':
                existing = self.search([("code", "=", rec.code), ("id", "!=", rec.id)], limit=1)
                if existing:
                    raise ValidationError("Promo Code must be unique.")

    # ============================================================
    # Helpers
    # ============================================================
    def _generate_coupon_code(self):
        """Generates a random, unique coupon code in the format 'XXXX-XXXX-XXXX'."""
        length = 4
        characters = string.ascii_uppercase + string.digits
        characters = ''.join(c for c in characters if c not in '01IO')

        while True:
            code = "-".join(
                ''.join(random.choice(characters) for _ in range(length))
                for _ in range(3)
            )
            if not self.search([('code', '=', code)]):
                return code

    def is_valid(self):
        """Check if promotion is currently valid"""
        today = datetime.now()
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

    # ============================================================
    # Overrides
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self._generate_coupon_code()
        return super(SportClubPromotion, self).create(vals_list)

    def write(self, vals):
        """Prevent manual overwrite of code unless regenerating."""
        if "code" in vals and vals["code"] != self.code:
            raise ValidationError("Promo Code cannot be changed once generated.")
        return super(SportClubPromotion, self).write(vals)