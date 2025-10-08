from odoo import api, models, fields,_
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
        default=lambda self: _('New'),
        required=True,
        copy=False,
        tracking=True,
        index=True,
        help="Name of the pricing rule (e.g., 'Weekend Peak Rate', 'Holiday Discount')."
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('open','Running'),
            ('expired','Expired'),
            ('closed','Closed'),
        ],
        default='draft',
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
    # ============================================================
    # Pricing
    # ============================================================
    base_price = fields.Monetary(
        string="Base Price",
        required=True,
        tracking=True,
        help="The base price before applying taxes and dynamic factors."
    )

    tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Taxes",
        tracking=True,
        help="Taxes applied to this pricing rule."
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

    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this calendar template in views "
             "(e.g., calendar or kanban)."
    )
    # ------------------------------------------------------
    # State Actions
    # ------------------------------------------------------
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_runing(self):
        self.write({'state': 'open'})

    def action_closed(self):
        self.write({'state': 'close'})

    def _cron_expire_pricing_rules(self):
        today = fields.Date.today()
        expired_rules = self.search([
            ('state', '=', 'open'),
            ('date_to', '<', today),
            ('date_to', '!=', False),
        ])

        if expired_rules:
            expired_rules.write({'state': 'expired'})
            # Optional: post a message in the chatter
            expired_rules.message_post(
                body=_("This pricing rule has been automatically expired by the system.")
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sport.club.pricing.rule.seq')
        return super().create(vals_list)
