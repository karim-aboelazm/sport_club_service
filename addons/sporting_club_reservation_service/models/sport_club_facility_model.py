from odoo import models, fields


class SportClubFacility(models.Model):
    """
    Model: Sport Club Facility
    --------------------------
    Represents a physical facility within a sport club.
    Examples: courts, fields, rooms, or swimming lanes.
    Each facility can be linked to a specific sport and calendar template.
    """
    _name = "sport.club.facility"
    _description = "Sport Club Facility"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ============================================================
    # Basic Information
    # ============================================================
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    name = fields.Char(
        string="Facility Name",
        required=True,
        tracking=True,
        index=True,
        help="Name of the facility (e.g., Court 1, Football Field A)."
    )

    facility_type = fields.Selection(
        selection=[
            ("court", "Court"),
            ("field", "Field"),
            ("room", "Room"),
            ("lane", "Swimming Lane"),
        ],
        string="Facility Type",
        required=True,
        tracking=True,
        help="Type of facility (Court, Field, Room, Swimming Lane)."
    )

    capacity = fields.Integer(
        string="Capacity",
        required=False,
        tracking=True,
        default=1,
        help="Maximum number of players or participants allowed in this facility."
    )

    # ============================================================
    # Relations
    # ============================================================
    sport_club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Sport Club",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="The sport club that owns this facility."
    )

    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        required=False,
        tracking=True,
        ondelete="set null",
        index=True,
        help="The sport associated with this facility (if any)."
    )

    calendar_template_id = fields.Many2one(
        comodel_name="sport.club.calendar",
        string="Calendar Template",
        required=False,
        tracking=True,
        help="Defines the default availability schedule for this facility."
    )

    # ============================================================
    # Facility Features
    # ============================================================
    indoor = fields.Boolean(
        string="Indoor",
        default=False,
        tracking=True,
        help="Indicates whether this facility is indoors."
    )

    lighting = fields.Boolean(
        string="Lighting Available",
        default=False,
        tracking=True,
        help="Indicates if the facility has lighting for evening use."
    )

    surface_type = fields.Selection(
        selection=[
            ("grass", "Grass"),
            ("clay", "Clay"),
            ("hard", "Hard"),
        ],
        string="Surface Type",
        required=False,
        tracking=True,
        help="The surface type of the facility (Grass, Clay, Hard)."
    )

    # ============================================================
    # Status
    # ============================================================
    is_active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Indicates whether this facility is currently active and usable."
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