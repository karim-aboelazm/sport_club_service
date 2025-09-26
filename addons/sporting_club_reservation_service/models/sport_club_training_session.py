from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SportClubTrainingSession(models.Model):
    _name = "sport.club.training.session"
    _description = "Sport Club Training Session"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ========================
    # Basic Info
    # ========================
    name = fields.Char(
        string="Session Title",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    trainer_id = fields.Many2one(
        comodel_name="sport.club.trainer",
        string="Trainer",
        required=True,
        tracking=True,
    )
    player_id = fields.Many2one(
        comodel_name="res.partner",
        string="Player",
        domain=[("is_player", "=", True)],
        required=True,
        tracking=True,
    )
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        tracking=True,
    )
    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        required=True,
        tracking=True,
    )

    # ========================
    # Scheduling
    # ========================
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
    duration = fields.Float(
        string="Duration (hrs)",
        compute="_compute_duration",
        store=True,
        help="Calculated duration in hours.",
    )
    level = fields.Selection(
        selection=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        string="Skill Level",
        default="beginner",
    )

    # ========================
    # Financials
    # ========================
    price_hour = fields.Monetary(
        string="Hourly Rate",
        related="trainer_id.hourly_rate",
        store=True,
        readonly=False,
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        compute="_compute_amount_total",
        store=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    reservation_id = fields.Many2one(
        comodel_name="sport.club.reservation",
        string="Linked Reservation",
    )

    # ========================
    # Status
    # ========================
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # ========================
    # Compute Methods
    # ========================
    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                delta = rec.date_end - rec.date_start
                rec.duration = delta.total_seconds() / 3600.0
            else:
                rec.duration = 0.0

    @api.depends("duration", "price_hour")
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.duration * rec.price_hour

    # ========================
    # Constraints
    # ========================
    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end <= rec.date_start:
                raise ValidationError("End time must be after start time.")
