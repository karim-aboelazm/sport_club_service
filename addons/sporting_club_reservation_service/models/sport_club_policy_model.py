from odoo import models, fields


class SportClubPolicy(models.Model):
    """
    Model: Sport Club Policy
    ------------------------
    Defines the cancellation, refund, penalty, and rescheduling rules
    that apply to bookings within a sport club.

    Example Use Cases:
        - Club can define a "24h Free Cancellation" policy
        - Different clubs may have different policies
        - Policies can be reused and attached to bookings/reservations
    """

    # --------------------------------------------------------------------------------
    # Model Metadata
    # --------------------------------------------------------------------------------
    _name = "sport.club.policy"                     # DB table: sport_club_policy
    _description = "Cancellation / Refund Policy"   # Human-readable model name
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # -> Enables chatter features (tracking, followers, activities)

    # ============================================================
    # Basic Information
    # ============================================================

    # Boolean -> Active flag
    # - Default True = policy is active
    # - Can be toggled to archive policies without deleting them
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Char -> Policy Name
    # - Required
    # - Index for quick searching
    # - Example: "Standard Cancellation Policy"
    name = fields.Char(
        string="Policy Name",
        required=True,
        tracking=True,
        index=True,
        help="The name of the policy (e.g., 'Standard Cancellation Policy')."
    )

    # Many2one -> Linked Club
    # - Links policy to a specific sport club
    # - ondelete="cascade": deleting a club removes its policies
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

    # Integer -> Free cancellation period
    # - Default 24 hours
    # - Cancelling before this period applies no penalty
    free_cancel_before_hours = fields.Integer(
        string="Free Cancel Before (hours)",
        required=False,
        tracking=True,
        default=24,
        help="Number of hours before the booking time when a cancellation "
             "is allowed without penalty."
    )

    # Integer -> Refund percentage
    # - Default 50%
    # - Refund applied if cancellation occurs before time window
    refund_percent_before_hours = fields.Integer(
        string="Refund % Before (hours)",
        required=False,
        tracking=True,
        default=50,
        help="Percentage of refund granted if cancellation occurs before "
             "the specified time window."
    )

    # Integer -> Penalty for no-shows
    # - Default 100%
    # - Typically means customer is fully charged
    no_show_penalty_percent = fields.Integer(
        string="No Show Penalty (%)",
        required=False,
        tracking=True,
        default=100,
        help="Percentage penalty applied if the customer does not show up "
             "without cancelling."
    )

    # ============================================================
    # Rescheduling Rules
    # ============================================================

    # Boolean -> Allow Reschedule
    # - Default True
    # - If checked, customers may reschedule instead of cancelling
    reschedule_allowed = fields.Boolean(
        string="Allow Reschedule",
        required=False,
        tracking=True,
        default=True,
        help="If checked, customers can reschedule their bookings "
             "instead of cancelling."
    )

    # ============================================================
    # Policy Terms
    # ============================================================

    # Html -> Policy terms & conditions
    # - Rich text field (HTML)
    # - Can include styled descriptions, bullet points, etc.
    terms_html = fields.Html(
        string="Terms & Conditions",
        required=False,
        sanitize=True,
        help="Detailed HTML content describing the full terms and conditions "
             "of this policy."
    )

    # ============================================================
    # Display Settings
    # ============================================================

    # Integer -> Color Index
    # - Used in Kanban/Calendar views for visual grouping
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this policy in views "
             "(e.g., calendar or kanban)."
    )
