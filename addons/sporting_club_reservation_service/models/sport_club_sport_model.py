from odoo import models, fields


class SportClubSports(models.Model):
    """
    Model: Sport Club Sports
    ------------------------
    Represents the relationship between a Sport Club and the Sports it offers.
    Each record links a club to a specific sport with additional metadata if needed.
    """
    _name = "sport.club.sports"
    _description = "Sport Club Sports"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ============================================================
    # Basic Information
    # ============================================================
    name = fields.Char(
        string="Sport Name",
        required=True,
        tracking=True,
        index=True,
        help="The full name of the sport (e.g., Tennis, Padel, Football)."
    )

    code = fields.Char(
        string="Code",
        required=False,
        tracking=True,
        index=True,
        size=10,
        help="Short code or abbreviation for the sport (e.g., TEN for Tennis, PAD for Padel)."
    )
    # ============================================================
    # Display Settings
    # ============================================================
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this sport in views (e.g., calendar or kanban)."
    )
