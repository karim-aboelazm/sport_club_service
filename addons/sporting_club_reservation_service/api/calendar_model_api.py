from .utils import *
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

class SportClubCalendarModel(models.Model):
    _inherit = "sport.club.calendar"

    # ============================================================
    # API: CREATE
    # ============================================================
    @api.model
    def _api_create_calendar(self, vals):
        Calendar = self.env['sport.club.calendar'].sudo()

        if not vals.get('name'):
            raise ValidationError(_("Template Name is required."))
        if not vals.get('club_id'):
            raise ValidationError(_("Sport Club is required."))

        data = self._from_api_dict(vals)
        calendar = Calendar.create(data)
        return calendar._to_api_dict()

    # ============================================================
    # API: SEARCH
    # ============================================================
    @api.model
    def _api_search_calendars(self, domain=None, limit=100, offset=0):
        Calendar = self.env['sport.club.calendar'].sudo()
        domain = domain or []
        records = Calendar.search(domain, limit=limit, offset=offset)
        return [rec._to_api_dict() for rec in records]

    # ============================================================
    # API: GET ONE
    # ============================================================
    @api.model
    def _api_get_calendar(self, calendar_id):
        Calendar = self.env['sport.club.calendar'].sudo()
        record = Calendar.browse(int(calendar_id))
        if not record.exists():
            raise UserError(_("Calendar not found."))
        return record._to_api_dict()

    # ============================================================
    # API: FILTER (keyword search)
    # ============================================================
    @api.model
    def _api_filter_calendars_with_keyword(self, keyword):
        if not keyword:
            return []

        Calendar = self.env['sport.club.calendar'].sudo()
        domain = [
            '|', '|',
            ('name', 'ilike', keyword),
            ('club_id.name', 'ilike', keyword),
            ('facility_id.name', 'ilike', keyword),
        ]
        records = Calendar.search(domain)
        return [rec._to_api_dict() for rec in records]

    # ============================================================
    # API: UPDATE
    # ============================================================
    @api.model
    def _api_update_calendar(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Calendar ID is required for update."))

        Calendar = self.env['sport.club.calendar'].sudo()
        record = Calendar.browse(int(vals['id']))
        if not record.exists():
            raise UserError(_("Calendar not found."))

        data = self._from_api_dict(vals)
        vals.pop('id', None)
        try:
            record.write(data)
        except Exception as e:
            raise ValidationError(e)
        return record._to_api_dict()

    # ============================================================
    # API: DELETE
    # ============================================================
    @api.model
    def _api_delete_calendar(self, calendar_id):
        Calendar = self.env['sport.club.calendar'].sudo()
        record = Calendar.browse(int(calendar_id))
        if not record.exists():
            raise UserError(_("Calendar not found."))

        record.unlink()
        return {"deleted": True, "id": calendar_id}

    # ============================================================
    # Helpers
    # ============================================================
    @api.model
    def _from_api_dict(self, data):
        """
        Convert incoming API dictionary into values for record creation,
        including related lines and exceptions.
        """
        vals = {}

        # ------------------------------------------------------------
        # Basic fields
        # ------------------------------------------------------------
        for field in ['name', 'color', 'active']:
            if field in data:
                vals[field] = data[field]

        # ------------------------------------------------------------
        # Club (resolve by ID or name)
        # ------------------------------------------------------------
        if 'club_id' in data and data['club_id']:
            club_val = data['club_id']
            club_model = self.env['sport.club.model'].sudo()

            if isinstance(club_val, int):
                vals['club_id'] = club_val
            elif isinstance(club_val, str):
                club = club_model.search([('name', '=', club_val)], limit=1)
                if not club:
                    raise ValidationError(_("Sport Club with name '%s' not found.") % club_val)
                vals['club_id'] = club.id

        # ------------------------------------------------------------
        # Facility (resolve by ID or name)
        # ------------------------------------------------------------
        if 'facility_id' in data and data['facility_id']:
            fac_val = data['facility_id']
            fac_model = self.env['sport.club.facility'].sudo()

            if isinstance(fac_val, int):
                vals['facility_id'] = fac_val
            elif isinstance(fac_val, str):
                facility = fac_model.search([('name', '=', fac_val)], limit=1)
                if not facility:
                    raise ValidationError(_("Facility with name '%s' not found.") % fac_val)
                vals['facility_id'] = facility.id

        # ------------------------------------------------------------
        # Availability Lines (One2many)
        # ------------------------------------------------------------
        line_commands = []
        if 'line_ids' in data and isinstance(data['line_ids'], (list, tuple)):
            line_model = self.env['sport.club.calendar.line'].sudo()
            template_id = data.get('id')  # only present on update

            for line in data['line_ids']:
                if isinstance(line, dict):
                    day_code = get_weekday_code(line.get('day_of_week').lower())

                    # Convert times
                    start_val = line.get('start_time')
                    end_val = line.get('end_time')

                    if isinstance(start_val, str):
                        start_time = time_str_to_float(start_val)
                    elif isinstance(start_val, (float, int)):
                        start_time = float(start_val)
                    else:
                        raise ValidationError(_("Invalid start_time format: must be string or float."))

                    if isinstance(end_val, str):
                        end_time = time_str_to_float(end_val)
                    elif isinstance(end_val, (float, int)):
                        end_time = float(end_val)
                    else:
                        raise ValidationError(_("Invalid end_time format: must be string or float."))

                    # ✅ Skip duplicates if same combination already exists
                    if template_id:
                        existing_line = line_model.search([
                            ('calendar_template_id', '=', template_id),
                            ('day_of_week', '=', day_code),
                            ('start_time', '=', start_time),
                            ('end_time', '=', end_time),
                        ], limit=1)
                        if existing_line:
                            continue  # skip duplicate

                    # Add to creation list
                    line_commands.append((0, 0, {
                        'day_of_week': day_code,
                        'start_time': start_time,
                        'end_time': end_time,
                    }))

                elif isinstance(line, int):
                    line_commands.append((4, line))

        if line_commands:
            vals['line_ids'] = line_commands

        # ------------------------------------------------------------
        # Exception Lines (One2many)
        # ------------------------------------------------------------
        exc_commands = []
        if 'exception_ids' in data and isinstance(data['exception_ids'], (list, tuple)):
            exc_model = self.env['sport.club.calendar.exception'].sudo()
            template_id = data.get('id')

            for exc in data['exception_ids']:
                if isinstance(exc, dict):
                    date_from = convert_to_utc(exc.get('date_from'))
                    date_to = convert_to_utc(exc.get('date_to'))
                    reason = exc.get('reason')
                    is_closed = exc.get('is_closed', True)

                    # ✅ Skip duplicates if same date_from/date_to already exists
                    if template_id:
                        existing_exc = exc_model.search([
                            ('calendar_template_id', '=', template_id),
                            ('date_from', '=', date_from),
                            ('date_to', '=', date_to),
                        ], limit=1)
                        if existing_exc:
                            continue  # skip duplicate exception

                    exc_commands.append((0, 0, {
                        'date_from': date_from,
                        'date_to': date_to,
                        'reason': reason,
                        'is_closed': is_closed,
                    }))

                elif isinstance(exc, int):
                    exc_commands.append((4, exc))

        if exc_commands:
            vals['exception_ids'] = exc_commands

        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "color": self.color,
            "club": {
                "id": self.club_id.id if self.club_id else False,
                "name": self.club_id.display_name if self.club_id else "",
            },
            "facility": {
                "id": self.facility_id.id if self.facility_id else False,
                "name": self.facility_id.display_name if self.facility_id else "",
            },
            "lines": [
                {
                    "id": line.id,
                    "day_of_week": line.day_of_week,
                    "day_label": dict(line._fields['day_of_week'].selection).get(line.day_of_week, ''),
                    "start_time_12": float_to_time_str_12(line.start_time),
                    "end_time_12": float_to_time_str_12(line.end_time),
                    "start_time_24": float_to_time_str_24(line.start_time),
                    "end_time_24": float_to_time_str_24(line.end_time)
                }
                for line in self.line_ids
            ],
            "exceptions": [
                {
                    "id": exc.id,
                    "date_from": convert_utc_to_local(fields.Datetime.to_string(exc.date_from)) if exc.date_from else None,
                    "date_to": convert_utc_to_local(fields.Datetime.to_string(exc.date_to)) if exc.date_to else None,
                    "reason": exc.reason or "",
                    "is_closed": exc.is_closed,
                }
                for exc in self.exception_ids
            ],
        }