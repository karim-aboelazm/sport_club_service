from odoo import models, fields


class SportClubPolicy(models.Model):
    """
    Model: SportClubPolicy
    ------------------
    This model defines the Cancellation / Refund Policy for sport clubs.
    It stores rules for cancellations, refunds, penalties, and rescheduling.
    """
    _name = "sport.club.policy"
    _description = "Cancellation / Refund Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ============================================================
    # Basic Information
    # ============================================================
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    name = fields.Char(
        string="Policy Name",
        required=True,
        tracking=True,
        index=True,
        help="The name of the policy (e.g., 'Standard Cancellation Policy')."
    )

    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Club",
        required=False,
        tracking=True,
        index=True,
        ondelete="cascade",
        help="Select the sport club that this policy applies to."
    )

    # ============================================================
    # Cancellation & Refund Rules
    # ============================================================
    free_cancel_before_hours = fields.Integer(
        string="Free Cancel Before (hours)",
        required=False,
        tracking=True,
        default=24,
        help="Number of hours before the booking time when a cancellation is allowed without penalty."
    )

    refund_percent_before_hours = fields.Integer(
        string="Refund % Before (hours)",
        required=False,
        tracking=True,
        default=50,
        help="Percentage of refund granted if cancellation occurs before the specified time window."
    )

    no_show_penalty_percent = fields.Integer(
        string="No Show Penalty (%)",
        required=False,
        tracking=True,
        default=100,
        help="Percentage penalty applied if the customer does not show up without cancelling."
    )

    # ============================================================
    # Rescheduling Rules
    # ============================================================
    reschedule_allowed = fields.Boolean(
        string="Allow Reschedule",
        required=False,
        tracking=True,
        default=True,
        help="If checked, customers can reschedule their bookings instead of cancelling."
    )

    # ============================================================
    # Policy Terms
    # ============================================================
    terms_html = fields.Html(
        string="Terms & Conditions",
        required=False,
        sanitize=True,
        help="Detailed HTML content describing the full terms and conditions of this policy."
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
