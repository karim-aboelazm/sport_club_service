from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

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

    def _create_session_from_reservation(self, reservation):
        # Helper to convert fractional hour to time safely
        def float_to_time(float_hour):
            hour = int(float_hour)
            minute = int((float_hour % 1) * 60)
            # Handle 24:00 edge case
            if hour == 24:
                hour = 0
            return datetime.strptime(f"{hour:02d}:{minute:02d}:00", "%H:%M:%S").time()

        start_time = float_to_time(reservation.time_from)
        end_time = float_to_time(reservation.time_to)

        date_start = datetime.combine(reservation.date, start_time)
        date_end = datetime.combine(reservation.date, end_time)

        # If end_time was 00:00 (24.0), move it to next day
        if reservation.time_to == 24.0:
            date_end += timedelta(days=1)

        return self.create({
            'name': f"Training: {reservation.player_id.name} - {reservation.date}",
            'trainer_id': reservation.trainer_id.id,
            'player_id': reservation.player_id.id,
            'club_id': reservation.club_id.id,
            'sport_id': reservation.sport_id.id,
            'date_start': fields.Datetime.to_string(date_start),
            'date_end': fields.Datetime.to_string(date_end),
            'reservation_id': reservation.id,
        })