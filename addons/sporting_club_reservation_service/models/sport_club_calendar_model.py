from odoo import models, fields


class SportClubCalendarModel(models.Model):
    _name = "sport.club.calendar"
    _description = "Facility Availability Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Template Name",
        required=True,
        tracking=True,
        index=True,
        help="Name of the availability template "
             "(e.g., Standard Weekdays, Weekend Hours)."
    )
    club_id = fields.Many2one(
        comodel_name="sport.club.model",
        string="Sport Club",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="The sport club that owns this facility."
    )
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
        help="Special dates when the facility is unavailable "
             "(holidays, maintenance, etc.)."
    )
    color = fields.Integer(
        string="Color Index",
        required=False,
        tracking=True,
        default=0,
        help="Used to assign a color for this calendar template in views "
             "(e.g., calendar or kanban)."
    )

    # ============================================================
    # Wizard Launcher for Server Action / Button
    # ============================================================
    def action_open_generate_times_wizard(self):
        """
        Opens the 'Generate Available Times' wizard prefilled with this calendar.
        Can be used in server actions or form buttons.
        """
        self.ensure_one()
        return {
            'name':'Generate Available Times',
            'type': 'ir.actions.act_window',
            'res_model': 'sport.club.calendar.times.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_calendar_id': self.id,
            },
        }