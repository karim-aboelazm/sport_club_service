from odoo import models, fields


class SportClubSports(models.Model):
    """
    Model: Sport Club Sports
    ------------------------
    Defines the list of sports that can be offered by clubs.
    Each record represents a sport type (e.g., Football, Tennis, Padel).
    Clubs can then reference these records via Many2many relations.
    """

    # --------------------------------------------------------------------------------
    # Model Metadata
    # --------------------------------------------------------------------------------
    _name = "sport.club.sports"                   # Creates new DB table: sport_club_sports
    _description = "Sport Club Sports"            # Human-readable name
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # -> Enables chatter tracking (followers, messages, activities, log notes)

    # ============================================================
    # Basic Information
    # ============================================================

    # Char -> Sport Name
    # - Required: must always be filled
    # - tracking=True: logs any change in chatter
    # - index=True: speeds up searching/filtering in DB
    # - Example: "Football", "Tennis"
    name = fields.Char(
        string="Sport Name",
        required=True,
        tracking=True,
        index=True,
        help="The full name of the sport (e.g., Tennis, Padel, Football)."
    )

    # Char -> Sport Code
    # - Optional short code / abbreviation
    # - index=True: allows fast lookup by code
    # - size=10: restricts field to 10 characters max
    # - Example: "FB", "TEN", "PAD"
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

    # Integer -> Color Index
    # - Default = 0 (no color)
    # - Typically used in Kanban, Calendar, or custom views
    # - Makes it easy to visually differentiate sports
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this sport in views (e.g., calendar or kanban)."
    )
