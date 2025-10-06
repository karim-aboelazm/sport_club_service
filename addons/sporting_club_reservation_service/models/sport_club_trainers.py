from odoo import models, fields, api,_
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import os

class SportClubTrainer(models.Model):
    _name = "sport.club.trainer"
    _description = "Sport Club Trainers"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # chatter support
    _rec_name = 'partner_id'
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
    priority = fields.Selection(
        selection=[
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
        ],
        string="Priority",
        default='0',
        index=True,
        help="Priority level from 0 (lowest) to 5 (highest).",
    )
    bio = fields.Text(
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
    club_sport_ids = fields.Many2many(
        comodel_name="sport.club.sports",
        string="Sports Offered",
        related="club_id.sport_ids",
    )

    @api.depends("partner_id")
    def _compute_session_count(self):
        """Count sessions linked to this trainer (if you have sc.session model)."""
        for rec in self:
            rec.session_count = self.env["sport.club.training.session"].search_count([("trainer_id", "=", rec.id)])

    def action_view_trainer_sessions(self):
        self.ensure_one()
        return {
            'name': _('Trainer Sessions'),
            'res_model': 'sport.club.training.session',
            'view_mode': 'list,form',
            'domain': [('trainer_id', '=', self.id)],
            'target': 'self',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'edit': False, 'delete': False, 'copy': False}
        }

    @api.onchange('club_id')
    def _onchange_club_id(self):
        for rec in self:
            if not rec.club_id:
                rec.sport_ids = False
                rec.calendar_template_id = False