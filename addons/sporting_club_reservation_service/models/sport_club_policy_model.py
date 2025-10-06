from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


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
    _name = "sport.club.policy"
    _description = "Cancellation / Refund Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'id'

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
    state = fields.Selection(
        selection=[
           ('draft', 'Draft'),
           ('run', 'Running'),
           ('cancel', 'Cancelled')
        ],
        string='Status',
        default='draft'
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
    free_cancel_before_hours = fields.Integer(
        string="Free Cancel Before (hours)",
        required=False,
        tracking=True,
        default=24,
        help="Number of hours before the booking time when a cancellation "
             "is allowed without penalty."
    )
    refund_percent_before_hours = fields.Integer(
        string="Refund % Before (hours)",
        required=False,
        tracking=True,
        default=50,
        help="Percentage of refund granted if cancellation occurs before "
             "the specified time window."
    )
    no_show_penalty_percent = fields.Integer(
        string="No Show Penalty (%)",
        required=False,
        tracking=True,
        default=100,
        help="Percentage penalty applied if the customer does not show up "
             "without cancelling."
    )
    reschedule_allowed = fields.Boolean(
        string="Allow Reschedule",
        required=False,
        tracking=True,
        default=True,
        help="If checked, customers can reschedule their bookings "
             "instead of cancelling."
    )
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this policy in views "
    )
    usage_reservation_count = fields.Integer(
        string="Usage Count",
        compute="_calculate_policy_usage_count"
    )

    @api.constrains('refund_percent_before_hours', 'no_show_penalty_percent')
    def _check_percentage_fields(self):
        for rec in self:
            if rec.refund_percent_before_hours < 0 or rec.refund_percent_before_hours > 100:
                raise ValidationError(_("Refund percentage must be between 0 and 100."))
            if rec.no_show_penalty_percent < 0 or rec.no_show_penalty_percent > 100:
                raise ValidationError(_("No-show penalty percentage must be between 0 and 100."))

    @api.constrains('free_cancel_before_hours')
    def _check_free_cancel_hours(self):
        for rec in self:
            if rec.free_cancel_before_hours < 0:
                raise ValidationError(_("Free cancellation hours cannot be negative."))

    @api.constrains('state','club_id','free_cancel_before_hours','refund_percent_before_hours','no_show_penalty_percent','reschedule_allowed')
    def _check_uniqueness(self):
        for rec in self:
            domain = [
                ('state','=',rec.state),
                ('club_id','=',rec.club_id.id),
                ('free_cancel_before_hours','=',rec.free_cancel_before_hours),
                ('refund_percent_before_hours','=',rec.refund_percent_before_hours),
                ('no_show_penalty_percent','=',rec.no_show_penalty_percent),
                ('id','!=',rec.id),
            ]
            existing = self.search(domain, limit=1)
            if existing:
                raise ValidationError(_(
                    "A policy with the same configuration already exists for club '%s'. "
                    "Please adjust the values or use the existing policy."
                ) % (rec.club_id.name))

    def _calculate_policy_usage_count(self):
        Reservation = self.env['sport.club.reservation'].sudo()
        for rec in self:
            domain = [('policy_id', '=', rec.id)]
            rec.usage_reservation_count = Reservation.search_count(domain)

    def action_state_to_run(self):
        self.write({'state':'run'})

    def action_state_to_cancel(self):
        self.write({'state':'cancel'})

    def action_state_to_draft(self):
        self.write({'state':'draft'})

    def get_all_policy_reservation_usage(self):
        self.ensure_one()
        domain = [('policy_id','in',self.ids)]
        return {
            'name': 'Reservations',
            'type': 'ir.actions.act_window',
            'res_model': 'sport.club.reservation',
            'domain': domain,
            'view_mode': 'list,form',
            'target': 'self',
            'context':{
                'create':False,
                'edit':False,
                'delete':False,
                'copy':False
            }
        }