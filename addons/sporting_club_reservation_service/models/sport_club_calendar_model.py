from odoo import models, fields


class SportClubCalendarModel(models.Model):
    """
    Model: Facility Availability Template
    -------------------------------------
    Defines recurring availability schedules for facilities.

    Key Points:
        - Each template can be linked to a specific facility
        - Availability is defined by multiple "lines" (time slots)
        - Exceptions (holidays, closures) can override availability

    Example Use Case:
        - Standard Weekday Schedule: Mon–Fri, 8:00 AM – 10:00 PM
        - Weekend Hours: Sat–Sun, 10:00 AM – 8:00 PM
        - Exceptions: "Closed on Public Holidays"
    """

    # --------------------------------------------------------------------------------
    # Model Metadata
    # --------------------------------------------------------------------------------
    _name = "sport.club.calendar"                   # DB table: sport_club_calendar
    _description = "Facility Availability Template" # Human-readable name
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # -> Enables chatter (tracking, followers, activities, log notes)

    # ============================================================
    # Basic Information
    # ============================================================

    # Boolean -> Active flag
    # - Standard Odoo practice for archiving without deleting
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Char -> Template name
    # - Required
    # - Example: "Standard Weekdays", "Weekend Hours"
    name = fields.Char(
        string="Template Name",
        required=True,
        tracking=True,
        index=True,
        help="Name of the availability template "
             "(e.g., Standard Weekdays, Weekend Hours)."
    )

    # ============================================================
    # Relations
    # ============================================================

    # Many2one -> Linked Facility
    # - Optional: a template can be reused across facilities
    # - ondelete="cascade": removing a facility deletes its templates
    facility_id = fields.Many2one(
        comodel_name="sport.club.facility",
        string="Facility",
        required=False,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="Facility that this availability template is linked to."
    )

    # One2many -> Availability Lines
    # - Defines recurring availability slots (e.g., Mon–Fri, 9–17h)
    line_ids = fields.One2many(
        comodel_name="sport.club.calendar.line",
        inverse_name="calendar_template_id",
        string="Availability Lines",
        tracking=True,
        help="Defines the daily or weekly availability slots for this facility."
    )

    # One2many -> Exceptions
    # - Overrides availability on specific dates
    # - Example: Public Holidays, Maintenance closures
    exception_ids = fields.One2many(
        comodel_name="sport.club.calendar.exception",
        inverse_name="calendar_template_id",
        string="Exceptions",
        tracking=True,
        help="Special dates when the facility is unavailable "
             "(holidays, maintenance, etc.)."
    )

    # ============================================================
    # Display Settings
    # ============================================================

    # Integer -> Color index
    # - Used in Kanban/Calendar views
    # - Helps visually distinguish different templates
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this calendar template in views "
             "(e.g., calendar or kanban)."
    )
