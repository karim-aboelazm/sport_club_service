from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class CalendarTemplateLine(models.Model):
    """
    Model: Calendar Template Line
    -----------------------------
    Represents a single availability slot in a calendar template.
    Each line specifies:
      - The day of the week.
      - A start and end time (expressed as float hours).
    Used to define recurring availability (e.g., Mondays 9:00–17:00).
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
        help="Starting time of availability in float hours "
             "(e.g., 9.0 = 9:00 AM, 13.5 = 1:30 PM)."
    )

    end_time = fields.Float(
        string="End Time",
        required=True,
        tracking=True,
        help="Ending time of availability in float hours "
             "(e.g., 17.0 = 5:00 PM, 20.25 = 8:15 PM)."
    )
    # ============================================================
    # Constraints
    # ============================================================
    @api.constrains("start_time", "end_time")
    def _check_time_range(self):
        """
        Business Constraint:
        Ensure that the start time is always before the end time.
        """
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError(
                    "Start Time must be earlier than End Time."
                )

    _sql_constraints = [
        (
            "unique_day_template",
            "unique(calendar_template_id, day_of_week, start_time, end_time)",
            "Duplicate availability slots are not allowed for the same day in a template."
        ),
    ]

    def add_reservation_slot(self):
        current_reservation_id = self.env['sport.club.reservation'].browse(self._context.get('current_reservation'))

        # Assign slot to reservation
        current_reservation_id.write({
            'time_from': self.start_time,
            'time_to': self.end_time,
        })
        # Rainbow man notification ✨
        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('The time slot %.2f - %.2f has been successfully assigned to the reservation.') % (
                    self.start_time, self.end_time),
                'type': 'rainbow_man',
            }
        }

