# -*- coding: utf-8 -*-
from .utils import *
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

class SportClubPromotion(models.Model):
    _inherit = "sport.club.promotion"

    @api.model
    def _api_create_promotion(self, vals):
        Promotion = self.env['sport.club.promotion'].sudo()

        if not vals.get('name'):
            raise ValidationError(_("Promotion Name is required."))
        if not vals.get('discount_type') or not vals.get('discount_value'):
            raise ValidationError(_("Discount type and value are required."))

        if 'date_start' in vals and vals['date_start']:
            vals['date_start'] = convert_to_utc(vals['date_start'])
        if 'date_end' in vals and vals['date_end']:
            vals['date_end'] = convert_to_utc(vals['date_end'])

        data = self._from_api_dict(vals)
        promo = Promotion.create(data)
        return promo._to_api_dict()

    @api.model
    def _api_search_promotions(self, domain=None, limit=100, offset=0):
        Promotion = self.env['sport.club.promotion'].sudo()
        domain = domain or []
        promotions = Promotion.search(domain, limit=limit, offset=offset)
        return [p._to_api_dict() for p in promotions]

    @api.model
    def _api_get_promotion(self, promo_id):
        Promotion = self.env['sport.club.promotion'].sudo()
        promo = Promotion.browse(int(promo_id))
        if not promo.exists():
            raise UserError(_("Promotion not found."))
        return promo._to_api_dict()

    @api.model
    def _api_filter_promotions_with_keyword(self, keyword):
        if not keyword:
            return []

        Promotion = self.env['sport.club.promotion'].sudo()
        domain = ['|', '|', '|', '|','|',
                  ('name', 'ilike', keyword),
                  ('code', 'ilike', keyword),
                  ('description', 'ilike', keyword),
                  ('club_id.name', 'ilike', keyword),
                  ('sport_ids.name', 'ilike', keyword),
                  ('facility_ids.name', 'ilike', keyword),]

        # Try parsing dates
        parsed_date = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                parsed_date = datetime.strptime(keyword, fmt)
                break
            except Exception:
                continue

        if parsed_date:
            domain = [
                '|', '|', '|', '|', '|','|',
                '&', ('date_start', '<=', parsed_date), ('date_end', '>=', parsed_date),
                ('name', 'ilike', keyword),
                ('code', 'ilike', keyword),
                ('description', 'ilike', keyword),
                ('club_id.name', 'ilike', keyword),
                ('sport_ids.name', 'ilike', keyword),
                ('facility_ids.name', 'ilike', keyword)
            ]

        promos = Promotion.search(domain)
        return [p._to_api_dict() for p in promos]

    @api.model
    def _api_update_promotion(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Promotion ID is required for update."))

        Promotion = self.env['sport.club.promotion'].sudo()
        promo = Promotion.browse(int(vals['id']))
        if not promo.exists():
            raise UserError(_("Promotion not found."))

        vals.pop('id', None)

        if 'date_start' in vals and vals['date_start']:
            vals['date_start'] = convert_to_utc(vals['date_start'])
        if 'date_end' in vals and vals['date_end']:
            vals['date_end'] = convert_to_utc(vals['date_end'])

        data = self._from_api_dict(vals)
        promo.write(data)
        return promo._to_api_dict()

    @api.model
    def _api_delete_promotion(self, promo_id):
        Promotion = self.env['sport.club.promotion'].sudo()
        promo = Promotion.browse(int(promo_id))
        if not promo.exists():
            raise UserError(_("Promotion not found."))

        promo.unlink()
        return {"deleted": True, "id": promo_id}

    @api.model
    def _from_api_dict(self, data):
        vals = {}

        for field in ['name', 'description', 'active', 'discount_type', 'discount_value','date_start', 'date_end', 'usage_limit', 'color']:
            if field in data:
                vals[field] = data[field]

        if 'club_id' in data and data['club_id']:
            club_val = data['club_id']
            club_model = self.env['sport.club.model'].sudo()

            if isinstance(club_val, int):
                vals['club_id'] = club_val
            elif isinstance(club_val, str):
                club = club_model.search([('name', '=', club_val)], limit=1)
                if not club:
                    raise ValidationError(_("Club with name '%s' not found.") % club_val)
                vals['club_id'] = club.id

        if 'sport_ids' in data and data['sport_ids']:
            sport_model = self.env['sport.club.sports'].sudo()
            sport_ids = []
            for val in data['sport_ids']:
                if isinstance(val, int):
                    sport_ids.append(val)
                elif isinstance(val, str):
                    sport = sport_model.search([('name', '=', val)], limit=1)
                    if sport:
                        sport_ids.append(sport.id)
            vals['sport_ids'] = [(6, 0, sport_ids)]

        if 'facility_ids' in data and data['facility_ids']:
            fac_model = self.env['sport.club.facility'].sudo()
            fac_ids = []
            for val in data['facility_ids']:
                if isinstance(val, int):
                    fac_ids.append(val)
                elif isinstance(val, str):
                    facility = fac_model.search([('name', '=', val)], limit=1)
                    if facility:
                        fac_ids.append(facility.id)
            vals['facility_ids'] = [(6, 0, fac_ids)]

        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "discount_type": self.discount_type,
            "discount_value": self.discount_value,
            "currency_id": {
                "id": self.currency_id.id if self.currency_id else False,
                "name": self.currency_id.name if self.currency_id else "",
                "symbol": self.currency_id.symbol if self.currency_id else "",
            },
            "validity": {
                "date_start": convert_utc_to_local(str(self.date_start)) if self.date_start else None,
                "date_end": convert_utc_to_local(str(self.date_end)) if self.date_end else None,
            },
            "usage": {
                "limit": self.usage_limit,
                "count": self.usage_count,
            },
            "club_id": {
                "id": self.club_id.id if self.club_id else False,
                "name": self.club_id.display_name if self.club_id else "",
            },
            "sport_ids": [
                {"id": s.id, "name": s.display_name} for s in self.sport_ids
            ],
            "facility_ids": [
                {"id": f.id, "name": f.display_name} for f in self.facility_ids
            ],
            "active": self.active,
            "color": self.color,
        }