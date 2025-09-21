from odoo import models, fields


class CalendarTemplateLine(models.Model):
    """
    Model: Calendar Template Line
    -----------------------------
    Represents a single availability slot in a calendar template.
    Defines which day of the week and what time range is available.
    """
    _name = "sport.club.calendar.line"
    _description = "Calendar Template Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ============================================================
    # Relations
    # ============================================================
    calendar_template_id = fields.Many2one(
        comodel_name="sport.club.calendar",
        string="Calendar Template",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="The calendar template this line belongs to."
    )

    # ============================================================
    # Availability Definition
    # ============================================================
    day_of_week = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Day of Week",
        required=True,
        tracking=True,
        help="Day of the week this availability applies to."
    )

    start_time = fields.Float(
        string="Start Time",
        required=True,
        tracking=True,
        help="Starting time of availability (in hours, 0.0 = midnight, 13.5 = 1:30 PM)."
    )

    end_time = fields.Float(
        string="End Time",
        required=True,
        tracking=True,
        help="Ending time of availability (in hours, 0.0 = midnight, 13.5 = 1:30 PM)."
    )

    # ============================================================
    # Constraints
    # ============================================================
    def _check_time_range(self):
        """
        Ensure start_time is always before end_time.
        """
        for record in self:
            if record.start_time >= record.end_time:
                raise ValueError("Start Time must be earlier than End Time.")

    _sql_constraints = [
        (
            "unique_day_template",
            "unique(calendar_template_id, day_of_week, start_time, end_time)",
            "Duplicate availability slots are not allowed for the same day in a template."
        ),
    ]
