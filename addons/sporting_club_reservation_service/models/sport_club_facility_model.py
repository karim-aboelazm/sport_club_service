from odoo import models, fields


class SportClubFacility(models.Model):
    """
    Model: Sport Club Facility
    --------------------------
    Represents a physical facility within a sport club.
    Examples:
        - Court (Tennis Court 1, Squash Court A)
        - Field (Football Field A)
        - Room (Yoga Room, Conference Hall)
        - Lane (Swimming Lane 3)

    Facilities can be:
        - Linked to a specific sport
        - Assigned a calendar template for availability
        - Marked with features (indoor, lighting, surface type, etc.)
    """

    # --------------------------------------------------------------------------------
    # Model Metadata
    # --------------------------------------------------------------------------------
    _name = "sport.club.facility"                   # DB table: sport_club_facility
    _description = "Sport Club Facility"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # -> Enables chatter (tracking, followers, activities)

    # ============================================================
    # Basic Information
    # ============================================================

    # Boolean -> Active flag
    # - Default True = facility is active
    # - Can archive facilities without deleting them
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Char -> Facility name
    # - Required
    # - Example: "Court 1", "Football Field A"
    name = fields.Char(
        string="Facility Name",
        required=True,
        tracking=True,
        index=True,
        help="Name of the facility (e.g., Court 1, Football Field A)."
    )

    # Selection -> Facility type
    # - Required
    # - Restricts facility types to known categories
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

    # Integer -> Capacity
    # - Optional
    # - Example: 2 players (tennis), 22 players (football), 20 people (yoga room)
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

    # Many2one -> Sport Club (owner)
    # - Required
    # - Cascade delete: deleting a club removes its facilities
    sport_club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Sport Club",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="The sport club that owns this facility."
    )

    # Many2one -> Sport
    # - Optional
    # - Example: Tennis, Football, Padel
    sport_id = fields.Many2one(
        comodel_name="sport.club.sports",
        string="Sport",
        required=False,
        tracking=True,
        ondelete="set null",
        index=True,
        help="The sport associated with this facility (if any)."
    )

    # Many2one -> Calendar template
    # - Defines default schedule/availability of facility
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

    # Boolean -> Indoor/outdoor
    # - Example: Indoor squash court vs outdoor tennis court
    indoor = fields.Boolean(
        string="Indoor",
        default=False,
        tracking=True,
        help="Indicates whether this facility is indoors."
    )

    # Boolean -> Lighting available
    # - Useful for evening/night use
    lighting = fields.Boolean(
        string="Lighting Available",
        default=False,
        tracking=True,
        help="Indicates if the facility has lighting for evening use."
    )

    # Selection -> Surface type
    # - Optional
    # - Common for courts/fields
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

    # Boolean -> Operational status
    # - This is redundant with `active` above
    # - Could be renamed to `is_operational` to distinguish
    is_active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
        help="Indicates whether this facility is currently active and usable."
    )

    # ============================================================
    # Display Settings
    # ============================================================

    # Integer -> Color index
    # - Used in Kanban/Calendar views
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this facility in views (e.g., calendar or kanban)."
    )
