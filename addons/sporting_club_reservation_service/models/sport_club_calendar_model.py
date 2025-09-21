from odoo import models, fields


class SportClubCalendarModel(models.Model):
    """
    Model: Calendar Template
    ------------------------
    Defines availability schedules for facilities.
    Each template can contain multiple lines (time slots)
    and exceptions (holidays or special closures).
    """
    _name = "sport.club.calendar"
    _description = "Facility Availability Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Enables chatter tracking

    # ============================================================
    # Basic Information
    # ============================================================
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    name = fields.Char(
        string="Template Name",
        required=True,
        tracking=True,
        index=True,
        help="Name of the availability template (e.g., Standard Weekdays, Weekend Hours)."
    )

    # ============================================================
    # Relations
    # ============================================================
    facility_id = fields.Many2one(
        comodel_name="sport.club.facility",
        string="Facility",
        required=False,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="Facility that this availability template is linked to."
    )

    line_ids = fields.One2many(
        comodel_name="sport.club.calendar.line",
        inverse_name="calendar_template_id",
        string="Availability Lines",
        tracking=True,
        help="Defines the daily or weekly availability slots for this facility."
    )

    exception_ids = fields.One2many(
        comodel_name="sport.club.calendar.exception",
        inverse_name="calendar_template_id",
        string="Exceptions",
        tracking=True,
        help="Special dates when the facility is unavailable (holidays, maintenance, etc.)."
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