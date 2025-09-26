from odoo import api, models, fields
from odoo.exceptions import ValidationError


class PricingRule(models.Model):
    """
    Model: Pricing Rule
    -------------------
    Defines dynamic pricing rules for sport clubs.
    Rules can be applied by club, sport, facility type, facility,
    and can vary by date, day of week, and time range.
    """
    _name = "sport.club.pricing.rule"
    _description = "Dynamic Pricing Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Enables chatter tracking

    # ============================================================
    # Basic Information
    # ============================================================
    name = fields.Char(
        string="Rule Name",
        required=True,
        tracking=True,
        index=True,
        help="Name of the pricing rule (e.g., 'Weekend Peak Rate', 'Holiday Discount')."
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )
    priority = fields.Integer(
        string="Priority",
        default=10,
        tracking=True,
        help="Higher priority rules are applied first when multiple rules match."
    )

    # ============================================================
    # Relations
    # ============================================================
    sport_club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Sport Club",
        required=False,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="The sport club this pricing rule applies to."
    )

    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        required=False,
        tracking=True,
        ondelete="set null",
        index=True,
        help="Specific sport this rule applies to (optional)."
    )

    facility_type = fields.Selection(
        selection=[
            ("court", "Court"),
            ("field", "Field"),
            ("room", "Room"),
            ("lane", "Lane"),
        ],
        string="Facility Type",
        required=False,
        tracking=True,
        help="Restrict this rule to a specific type of facility."
    )

    facility_id = fields.Many2one(
        comodel_name="sport.club.facility",
        string="Facility",
        required=False,
        tracking=True,
        ondelete="set null",
        index=True,
        help="Restrict this rule to a specific facility."
    )

    # ============================================================
    # Date & Time Rules
    # ============================================================
    date_from = fields.Date(
        string="Start Date",
        required=False,
        tracking=True,
        help="Date when this rule starts being active."
    )

    date_to = fields.Date(
        string="End Date",
        required=False,
        tracking=True,
        help="Date when this rule stops being active."
    )

    day_of_week = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Day of Week",
        required=False,
        tracking=True,
        help="Restrict this rule to a specific day of the week (optional)."
    )

    time_from = fields.Float(
        string="Start Time",
        required=False,
        tracking=True,
        help="Start time of the rule (in hours, e.g. 8.5 = 8:30 AM)."
    )

    time_to = fields.Float(
        string="End Time",
        required=False,
        tracking=True,
        help="End time of the rule (in hours, e.g. 20.0 = 8:00 PM)."
    )

    # ============================================================
    # Pricing
    # ============================================================
    base_price = fields.Monetary(
        string="Base Price",
        required=True,
        tracking=True,
        help="The base price before applying taxes and dynamic factors."
    )

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
        tracking=True,
        help="Taxes applied to this pricing rule."
    )

    dynamic_factor = fields.Float(
        string="Dynamic Factor",
        default=1.0,
        tracking=True,
        help="Multiplier for dynamic pricing (e.g., 1.2 = 20% increase, 0.8 = 20% discount)."
    )

    peak = fields.Boolean(
        string="Peak Pricing",
        default=False,
        tracking=True,
        help="If checked, this rule is considered a peak pricing rule."
    )

    # ============================================================
    # Duration Restrictions
    # ============================================================
    min_duration = fields.Float(
        string="Minimum Duration",
        required=False,
        tracking=True,
        help="Minimum booking duration (in hours) this rule applies to."
    )

    max_duration = fields.Float(
        string="Maximum Duration",
        required=False,
        tracking=True,
        help="Maximum booking duration (in hours) this rule applies to."
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
    # Constraints
    # ============================================================
    @api.constrains('time_to','time_from')
    def _check_time_range(self):
        """
        Ensure time_from is before time_to if both are set.
        """
        for record in self:
            if record.time_from and record.time_to and record.time_from >= record.time_to:
                raise ValidationError("Start Time must be earlier than End Time.")

    @api.constrains('max_duration', 'min_duration')
    def _check_duration_range(self):
        """
        Ensure min_duration is <= max_duration if both are set.
        """
        for record in self:
            if record.min_duration and record.max_duration and record.min_duration > record.max_duration:
                raise ValidationError("Minimum Duration cannot exceed Maximum Duration.")
