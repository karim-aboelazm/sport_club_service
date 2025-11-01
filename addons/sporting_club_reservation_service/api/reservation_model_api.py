# -*- coding: utf-8 -*-
from .utils import *
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

class SportClubReservation(models.Model):
    _inherit = "sport.club.reservation"

    @api.model
    def _api_create_reservation(self, vals):
        Reservation = self.env['sport.club.reservation'].sudo()

        required = ['club_id', 'facility_id', 'time_from', 'time_to']
        missing = [f for f in required if not vals.get(f)]
        if missing:
            raise ValidationError(_("Missing required fields: %s") % ', '.join(missing))

        vals_data = self._from_api_dict(vals)
        resv = Reservation.create(vals_data)
        return resv._to_api_dict()

    @api.model
    def _api_search_reservations(self, domain=None, limit=100, offset=0):
        Reservation = self.env['sport.club.reservation'].sudo()
        domain = domain or []
        reservations = Reservation.search(domain, limit=limit, offset=offset)
        return [r._to_api_dict() for r in reservations]

    @api.model
    def _api_get_reservation(self, reservation_id):
        Reservation = self.env['sport.club.reservation'].sudo()
        resv = Reservation.browse(int(reservation_id))
        if not resv.exists():
            raise UserError(_("Reservation not found."))
        return resv._to_api_dict()

    @api.model
    def _api_filter_reservations_with_keyword(self, keyword):
        if not keyword:
            return []

        Reservation = self.env['sport.club.reservation'].sudo()
        domain = ['|', '|', '|', '|', '|',
                  ('name', 'ilike', keyword),
                  ('code', 'ilike', keyword),
                  ('player_id.name', 'ilike', keyword),
                  ('club_id.name', 'ilike', keyword),
                  ('facility_id.name', 'ilike', keyword),
                  ('sport_id.name', 'ilike', keyword)]

        # Try date parsing for filtering by reservation date
        parsed_date = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                parsed_date = datetime.strptime(keyword, fmt).date()
                break
            except Exception:
                continue

        if parsed_date:
            domain = ['|'] + domain + [('date', '=', parsed_date)]

        reservations = Reservation.search(domain)
        return [r._to_api_dict() for r in reservations]

    @api.model
    def _api_update_reservation(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Reservation ID is required for update."))

        Reservation = self.env['sport.club.reservation'].sudo()
        resv = Reservation.browse(int(vals['id']))
        if not resv.exists():
            raise UserError(_("Reservation not found."))

        vals_data = self._from_api_dict(vals)
        vals.pop('id', None)
        resv.write(vals_data)
        return resv._to_api_dict()

    @api.model
    def _api_delete_reservation(self, reservation_id):
        Reservation = self.env['sport.club.reservation'].sudo()
        resv = Reservation.browse(int(reservation_id))
        if not resv.exists():
            raise UserError(_("Reservation not found."))

        resv.equipment_line_ids.unlink()
        resv.attendance_ids.unlink()
        resv.unlink()
        return {"deleted": True, "id": reservation_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}

        # Basic fields
        for field in ['state', 'source', 'time_from', 'time_to', 'notes','number_of_attandance', 'partner_include_attendance', 'color']:
            if field in data:
                vals[field] = data[field]

        # Date
        if data.get('date'):
            vals['date'] = data['date'] if isinstance(data['date'], str) else data['date']

        # Club
        if data.get('club_id'):
            club_val = data['club_id']
            Club = self.env['sport.club.model'].sudo()
            if isinstance(club_val, int):
                vals['club_id'] = club_val
            else:
                club = Club.search([('name', '=', club_val)], limit=1)
                if not club:
                    raise ValidationError(_("Club '%s' not found.") % club_val)
                vals['club_id'] = club.id

        # Facility
        if data.get('facility_id'):
            fac_val = data['facility_id']
            Fac = self.env['sport.club.facility'].sudo()
            if isinstance(fac_val, int):
                vals['facility_id'] = fac_val
            else:
                fac = Fac.search([('name', '=', fac_val)], limit=1)
                if not fac:
                    raise ValidationError(_("Facility '%s' not found.") % fac_val)
                vals['facility_id'] = fac.id


        if vals.get('facility_id') and vals.get('date') and vals.get('time_from') is not None and vals.get('time_to') is not None:
            weekday_number = fields.Date.from_string(vals['date']).weekday()
            current_calendar = self.env['sport.club.calendar'].search([
                ('club_id', '=', vals['club_id']),
                ('facility_id', '=', vals['facility_id'])
            ], limit=1)

            if not current_calendar:
                raise ValidationError(_("No calendar found for the selected club and facility."))

            slots = self.env['sport.club.calendar.line'].search([
                ('day_of_week', '=', str(weekday_number)),
                ('calendar_template_id', '=', current_calendar.id),
            ])

            valid_slot = False
            for slot in slots:
                if vals['time_from'] >= slot.start_time and vals['time_to'] <= slot.end_time:
                    valid_slot = True
                    break

            if not valid_slot:
                raise ValidationError(_("Selected time %s-%s does not match any available calendar slot.") %
                                      (vals['time_from'], vals['time_to']))

            reservation_domain = [
                ('facility_id', '=', vals['facility_id']),
                ('date', '=', vals['date']),
                ('state', 'in', ['requested', 'confirmed', 'checked_in']),
                ('time_from', '<', vals['time_to']),
                ('time_to', '>', vals['time_from']),
            ]
            if vals.get('sport_id'):
                reservation_domain.append(('sport_id', '=', vals['sport_id']))
            if data.get('id'):
                reservation_domain.append(('id', '!=', data['id']))

            overlapping = self.env['sport.club.reservation'].search(reservation_domain, limit=1)
            if overlapping:
                raise ValidationError(_(
                    "The selected time overlaps with an existing reservation "
                    "(Reservation: %s, Time: %s-%s)"
                ) % (overlapping.name, overlapping.time_from, overlapping.time_to))

        # Sport
        if data.get('sport_id'):
            sport_val = data['sport_id']
            Sport = self.env['sport.club.sports'].sudo()
            if isinstance(sport_val, int):
                sport = Sport.browse(sport_val)
                if not sport.exists():
                    raise ValidationError(_("Sport with ID %s not found.") % sport_val)
            else:
                sport = Sport.search([('name', '=', sport_val)], limit=1)
                if not sport:
                    raise ValidationError(_("Sport '%s' not found.") % sport_val)
            if 'club_id' in vals and vals['club_id']:
                if sport.id not in self.env['sport.club.model'].browse(vals['club_id']).sport_ids.ids:
                    raise ValidationError(
                        _("Sport '%s' is not offered by the selected club.") % sport.display_name
                    )
            vals['sport_id'] = sport.id

        # Player
        if data.get('player_id'):
            player_val = data['player_id']
            Partner = self.env['res.partner'].sudo()
            if isinstance(player_val, int):
                vals['player_id'] = player_val
            else:
                player = Partner.search([('name', '=', player_val)], limit=1)
                if not player:
                    raise ValidationError(_("Player '%s' not found.") % player_val)
                vals['player_id'] = player.id

        # Trainer
        if data.get('trainer_id'):
            trainer_val = data['trainer_id']
            Trainer = self.env['sport.club.trainer'].sudo()
            if isinstance(trainer_val, int):
                vals['trainer_id'] = trainer_val
            else:
                trainer = Trainer.search([('partner_id.name', '=', trainer_val)], limit=1)
                if not trainer:
                    raise ValidationError(_("Trainer '%s' not found.") % trainer_val)
                vals['trainer_id'] = trainer.id

        # Pricing rule
        if data.get('pricing_rule_id'):
            rule_val = data['pricing_rule_id']
            Rule = self.env['sport.club.pricing.rule'].sudo()
            if isinstance(rule_val, int):
                rule = Rule.browse(rule_val)
                if not rule.exists():
                    raise ValidationError(_("Pricing Rule with ID %s not found.") % rule_val)
            else:
                rule = Rule.search([('name', '=', rule_val)], limit=1)
                if not rule:
                    raise ValidationError(_("Pricing Rule '%s' not found.") % rule_val)
            if rule.state != 'open':
                raise ValidationError(
                    _("Pricing Rule '%s' is not open (current state: %s).") % (rule.display_name, rule.state)
                )
            vals['pricing_rule_id'] = rule.id

        # Policy
        if data.get('policy_id'):
            policy_val = data['policy_id']
            Policy = self.env['sport.club.policy'].sudo()
            if isinstance(policy_val, int):
                policy = Policy.browse(policy_val)
                if not policy.exists():
                    raise ValidationError(_("Policy with ID %s not found.") % policy_val)
                vals['policy_id'] = policy.id
            else:
                policy = Policy.search([('club_id', '=', vals['club_id']), ('name', '=', policy_val)], limit=1)
                if not policy:
                    raise ValidationError(_("Policy '%s' not found.") % policy_val)
                vals['policy_id'] = policy.id

        # Promotion
        if data.get('promotion_id'):
            promo_val = data['promotion_id']
            Promo = self.env['sport.club.promotion'].sudo()
            if isinstance(promo_val, int):
                vals['promotion_id'] = promo_val
            else:
                promo = Promo.search([('name', '=', promo_val)], limit=1)
                if promo:
                    vals['promotion_id'] = promo.id

        # Attendance
        if data.get('attendance_ids'):
            Partner = self.env['res.partner'].sudo()
            partner_ids = []
            reservation_id = data.get('id', False)
            for val in data['attendance_ids']:
                if isinstance(val, dict):
                    name = val.get('name')
                    email = val.get('email')
                    mobile = val.get('mobile')
                    if not name:
                        continue
                    partner = Partner.search([('name', '=', name), ('email', '=', email), ('mobile', '=', mobile)],
                                             limit=1)
                    if not partner:
                        partner = Partner.create({
                            'name': name,
                            'email': email,
                            'mobile': mobile,
                        })
                    partner_ids.append(partner.id)
            vals['attendance_ids'] = [(6, 0, partner_ids)]

        # Equipment
        if data.get('equipment_line_ids'):
            equip_commands = []
            reservation_id = data.get('id', False)
            Equipment = self.env['sport.club.equipment.booking'].sudo()
            Product = self.env['product.product'].sudo()
            for eq in data['equipment_line_ids']:
                if isinstance(eq, dict):
                    prod_val = eq.get('equipment_product_id')
                    if isinstance(prod_val, int):
                        product_id = prod_val
                    else:
                        product = Product.search([('name', '=', prod_val)], limit=1)
                        if not product:
                            raise ValidationError(_("Equipment '%s' not found.") % prod_val)
                        product_id = product.id

                    # Search existing line for this reservation and product
                    existing_line = Equipment.search([
                        ('reservation_id', '=', reservation_id),
                        ('equipment_product_id', '=', product_id)
                    ], limit=1)

                    line_vals = {
                        'equipment_product_id': product_id,
                        'qty': eq.get('qty', 1.0),
                        'hours': eq.get('hours', 1.0),
                    }

                    if existing_line:
                        equip_commands.append((1, existing_line.id, line_vals))  # update
                    else:
                        equip_commands.append((0, 0, line_vals))  # create new

            vals['equipment_line_ids'] = equip_commands

        return vals

    def _to_api_dict(self):
        self.ensure_one()
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "state": self.state,
            "source": self.source,
            "date": str(self.date) if self.date else None,
            "time_from_12": float_to_time_str_12(self.time_from),
            "time_to_12": float_to_time_str_12(self.time_to),
            "time_from_24": float_to_time_str_24(self.time_from),
            "time_to_24": float_to_time_str_24(self.time_to),
            "duration_hours": self.duration_hours,
            "club": {
                "id": self.club_id.id,
                "name": self.club_id.display_name,
            } if self.club_id else {},
            "facility": {
                "id": self.facility_id.id,
                "name": self.facility_id.display_name,
            } if self.facility_id else {},
            "sport": {
                "id": self.sport_id.id,
                "name": self.sport_id.display_name,
            } if self.sport_id else {},
            "player": {
                "id": self.player_id.id,
                "name": self.player_id.display_name,
            } if self.player_id else {},
            "trainer": {
                "id": self.trainer_id.id,
                "name": self.trainer_id.display_name,
            } if self.trainer_id else {},
            "policy": {
                "id": self.policy_id.id,
                "name": self.policy_id.display_name,
            } if self.policy_id else {},
            "promotion": {
                "id": self.promotion_id.id,
                "name": self.promotion_id.display_name,
            } if self.promotion_id else {},
            "pricing_rule": {
                "id": self.pricing_rule_id.id,
                "name": self.pricing_rule_id.display_name,
                "price_hour": self.price_hour,
            } if self.pricing_rule_id else {},
            "financials": {
                "amount_untaxed": self.amount_untaxed,
                "amount_tax": self.amount_tax,
                "amount_total": self.amount_total,
                "currency": self.currency_id.name,
            },
            "attendance": [
                {
                    "id": p.id,
                    "name": p.name,
                    "email": p.email,
                    "mobile": getattr(p, 'mobile', False)
                } for p in self.attendance_ids
            ],
            "equipment_lines": [
                {
                    "id": eq.id,
                    "equipment_product_id": {
                        "id": eq.equipment_product_id.id,
                        "name": eq.equipment_product_id.display_name
                    } if eq.equipment_product_id else {},
                    "qty": eq.qty,
                    "hours": eq.hours,
                    "price_subtotal": eq.price_subtotal
                } for eq in self.equipment_line_ids
            ],
            "payment_state": self.payment_state,
            "notes": self.notes,
        }