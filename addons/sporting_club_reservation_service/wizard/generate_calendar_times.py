from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class SportClubCalendarAvailableTimesGenerator(models.TransientModel):
    _name = 'sport.club.calendar.times.generator'
    _description = 'Generate Calendar Available Times Wizard'

    # ============================================================
    # Fields
    # ============================================================
    calendar_id = fields.Many2one(
        comodel_name='sport.club.calendar',
        string='Calendar Template',
        required=True,
        help='The calendar template where availability slots will be generated.'
    )

    week_days = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string='Day of Week',
        help='Select the day for which to generate available times.'
    )

    for_all_days = fields.Boolean(
        string='Apply to All Days',
        help='If enabled, the generator will apply to all days of the week.'
    )

    start_time = fields.Float(
        string='Start Time',
        required=True,
        help='Starting time of availability (e.g., 9.0 = 9:00 AM).'
    )

    end_time = fields.Float(
        string='End Time',
        required=True,
        help='Ending time of availability (e.g., 17.0 = 5:00 PM).'
    )

    split_time_period = fields.Float(
        string='Time Slot Duration (Hours)',
        required=True,
        help='Duration of each generated time slot in hours (e.g., 1.0 = 1 hour).'
    )

    # ============================================================
    # Core Logic
    # ============================================================
    def _generate_available_times(self, day_code):
        """
        Generate availability slots for a single day.
        It splits the start_time–end_time range into slots based on split_time_period.
        """
        self.ensure_one()

        # Validate time range
        if self.start_time >= self.end_time:
            raise ValidationError(_("Start Time must be earlier than End Time."))

        if self.split_time_period <= 0:
            raise ValidationError(_("Time Slot Duration must be greater than 0."))

        # Remove existing slots for that day to avoid duplicates
        existing_lines = self.env['sport.club.calendar.line'].search([
            ('calendar_template_id', '=', self.calendar_id.id),
            ('day_of_week', '=', day_code),
        ])
        existing_lines.unlink()

        # Generate new slots
        current_time = self.start_time
        while current_time < self.end_time:
            next_time = current_time + self.split_time_period
            if next_time > self.end_time:
                next_time = self.end_time  # Trim to end time if last slot is shorter

            self.env['sport.club.calendar.line'].create({
                'calendar_template_id': self.calendar_id.id,
                'day_of_week': day_code,
                'start_time': current_time,
                'end_time': next_time,
            })
            current_time = next_time

    # ============================================================
    # Confirmation
    # ============================================================
    def confirm(self):
        """
        Called when the user clicks 'Confirm' in the wizard.
        Generates slots either for the selected day or all days.
        """
        self.ensure_one()
        if self.for_all_days:
            for day_code in [str(i) for i in range(7)]:
                self._generate_available_times(day_code)
        else:
            if not self.week_days:
                raise ValidationError(_("Please select a day of the week or enable 'Apply to All Days'."))
            self._generate_available_times(self.week_days)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('Availability slots have been successfully generated!'),
                'type': 'rainbow_man',
            }
        }
