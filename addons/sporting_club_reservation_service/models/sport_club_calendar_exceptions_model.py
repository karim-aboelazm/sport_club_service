from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CalendarException(models.Model):
    """
    Model: Calendar Exception
    -------------------------
    Represents an exception to a facility's availability template.
    Use cases:
      - Public holidays
      - Maintenance periods
      - Private events
    Exceptions override the standard availability lines of the facility.
    """
    _name = "sport.club.calendar.exception"
    _description = "Calendar Exception"
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
        help="The calendar template this exception belongs to."
    )

    # ============================================================
    # Exception Details
    # ============================================================
    date_from = fields.Datetime(
        string="Start Date",
        required=True,
        tracking=True,
        help="The start date and time of the exception "
             "(when the facility becomes unavailable)."
    )

    date_to = fields.Datetime(
        string="End Date",
        required=True,
        tracking=True,
        help="The end date and time of the exception "
             "(when the facility becomes available again)."
    )

    reason = fields.Char(
        string="Reason",
        tracking=True,
        help="Reason for the exception (e.g., Maintenance, Public Holiday, Private Event)."
    )

    is_closed = fields.Boolean(
        string="Closed",
        default=True,
        tracking=True,
        help="If checked, the facility is considered closed during this exception period."
    )

    # ============================================================
    # Constraints
    # ============================================================
    @api.constrains("date_from", "date_to")
    def _check_date_range(self):
        """
        Business Constraint:
        Ensure that the start date/time is always earlier than the end date/time.
        """
        for record in self:
            if record.date_from and record.date_to and record.date_from >= record.date_to:
                raise ValidationError(
                    "The start date must be earlier than the end date."
                )

    _sql_constraints = [
        (
            "unique_exception",
            "unique(calendar_template_id, date_from, date_to)",
            "Duplicate exceptions are not allowed for the same calendar template."
        ),
    ]
