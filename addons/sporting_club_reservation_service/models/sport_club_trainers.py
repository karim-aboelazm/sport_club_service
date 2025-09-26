from odoo import models, fields, api


class SportClubTrainer(models.Model):
    _name = "sport.club.trainer"
    _description = "Sport Club Trainers"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # chatter support

    # ========================
    # Relations
    # ========================
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Trainer",
        required=True,
        domain=[("is_trainer", "=", True)],
        tracking=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        tracking=True,
    )
    sport_ids = fields.Many2many(
        comodel_name="sport.club.sports",
        string="Sports",
        tracking=True,
    )
    calendar_template_id = fields.Many2one(
        comodel_name="sport.club.calendar",
        string="Availability Calendar",
        tracking=True,
    )

    # ========================
    # Profile
    # ========================
    hourly_rate = fields.Monetary(
        string="Hourly Rate",
        tracking=True,
        help="The cost per hour for booking this trainer.",
    )
    rating_avg = fields.Float(
        string="Average Rating",
        digits=(2, 1),
        help="Average rating from clients (scale 0–5).",
    )
    bio = fields.Html(
        string="Biography",
        help="Trainer profile, background, and qualifications.",
    )

    # ========================
    # Financial
    # ========================
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # ========================
    # Computed Fields
    # ========================
    session_count = fields.Integer(
        string="Number of Sessions",
        compute="_compute_session_count",
    )

    @api.depends("partner_id")
    def _compute_session_count(self):
        """Count sessions linked to this trainer (if you have sc.session model)."""
        for rec in self:
            rec.session_count = self.env["sport.club.training.session"].search_count([("trainer_id", "=", rec.id)])
