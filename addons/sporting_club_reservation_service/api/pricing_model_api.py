# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, models,fields,_
from odoo.exceptions import ValidationError, UserError

class SportClubPricingRule(models.Model):
    _inherit = "sport.club.pricing.rule"

    @api.model
    def _api_create_pricing_rule(self, vals):
        PricingRule = self.env['sport.club.pricing.rule'].sudo()

        if not vals.get('base_price'):
            raise ValidationError(_("Base Price is required."))

        data = self._from_api_dict(vals)
        rule = PricingRule.create(data)
        return rule._to_api_dict()

    @api.model
    def _api_search_pricing_rules(self, domain=None, limit=100, offset=0):
        PricingRule = self.env['sport.club.pricing.rule'].sudo()
        domain = domain or []
        rules = PricingRule.search(domain, limit=limit, offset=offset)
        return [r._to_api_dict() for r in rules]

    @api.model
    def _api_get_pricing_rule(self, rule_id):
        PricingRule = self.env['sport.club.pricing.rule'].sudo()
        rule = PricingRule.browse(int(rule_id))
        if not rule.exists():
            raise UserError(_("Pricing Rule not found."))
        return rule._to_api_dict()

    @api.model
    def _api_filter_pricing_rules_with_keyword(self, keyword):
        if not keyword:
            return []

        PricingRule = self.env['sport.club.pricing.rule'].sudo()
        domain = []

        parsed_date = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                parsed_date = datetime.strptime(keyword, fmt).date()
                break
            except Exception:
                continue

        if parsed_date:
            domain = [
                '|', '|', '|', '|', '|','|',
                '&', ('date_from', '<=', parsed_date), ('date_to', '>=', parsed_date),
                ('name', 'ilike', keyword),
                ('state', 'ilike', keyword),
                ('sport_club_id.name', 'ilike', keyword),
                ('sport_id.name', 'ilike', keyword),
                ('tax_id.name', 'ilike', keyword),
                ('facility_id.name', 'ilike', keyword),
            ]
            rules = PricingRule.search(domain)
            return [r._to_api_dict() for r in rules]

        price_value = None
        try:
            price_value = float(keyword)
        except ValueError:
            price_value = None

        if price_value is not None:
            domain = [
                '|', '|', '|', '|', '|','|',
                ('name', 'ilike', keyword),
                ('state', 'ilike', keyword),
                ('sport_club_id.name', 'ilike', keyword),
                ('sport_id.name', 'ilike', keyword),
                ('tax_id.name', 'ilike', keyword),
                ('base_price', '=', price_value),
                ('facility_id.name', 'ilike', keyword),
            ]
        else:
            domain = [
                '|', '|', '|', '|','|',
                ('name', 'ilike', keyword),
                ('state', 'ilike', keyword),
                ('sport_club_id.name', 'ilike', keyword),
                ('sport_id.name', 'ilike', keyword),
                ('tax_id.name', 'ilike', keyword),
                ('facility_id.name', 'ilike', keyword),
            ]

        rules = PricingRule.search(domain)
        return [r._to_api_dict() for r in rules]

    # ============================================================
    # API: UPDATE
    # ============================================================
    @api.model
    def _api_update_pricing_rule(self, vals):
        if 'id' not in vals:
            raise ValidationError(_("Pricing Rule ID is required for update."))

        PricingRule = self.env['sport.club.pricing.rule'].sudo()
        rule = PricingRule.browse(int(vals['id']))
        if not rule.exists():
            raise UserError(_("Pricing Rule not found."))

        vals.pop('id', None)
        data = self._from_api_dict(vals)
        rule.write(data)
        return rule._to_api_dict()

    # ============================================================
    # API: DELETE
    # ============================================================
    @api.model
    def _api_delete_pricing_rule(self, rule_id):
        PricingRule = self.env['sport.club.pricing.rule'].sudo()
        rule = PricingRule.browse(int(rule_id))
        if not rule.exists():
            raise UserError(_("Pricing Rule not found."))

        rule.unlink()
        return {"deleted": True, "id": rule_id}

    # ============================================================
    # Helpers
    # ============================================================
    @api.model
    def _from_api_dict(self, data):
        vals = {}

        for field in ['state', 'date_from', 'date_to', 'base_price', 'currency_id', 'color']:
            if field in data:
                vals[field] = data[field]

        if 'sport_club_id' in data and data['sport_club_id']:
            club_val = data['sport_club_id']
            club_model = self.env['sport.club.model'].sudo()

            if isinstance(club_val, int):
                vals['sport_club_id'] = club_val
            elif isinstance(club_val, str):
                club = club_model.search([('name', '=', club_val)], limit=1)
                if not club:
                    raise ValidationError(_("Sport Club with name '%s' not found.") % club_val)
                vals['sport_club_id'] = club.id

        if 'sport_id' in data and data['sport_id']:
            sport_val = data['sport_id']
            sport_model = self.env['sport.club.sports'].sudo()

            if isinstance(sport_val, int):
                vals['sport_id'] = sport_val
            elif isinstance(sport_val, str):
                sport = sport_model.search([('name', '=', sport_val)], limit=1)
                if not sport:
                    raise ValidationError(_("Sport with name '%s' not found.") % sport_val)
                vals['sport_id'] = sport.id

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

        if 'tax_id' in data and data['tax_id']:
            tax_val = data['tax_id']
            tax_model = self.env['account.tax'].sudo()

            if isinstance(tax_val, int):
                vals['tax_id'] = tax_val
            elif isinstance(tax_val, str):
                tax = tax_model.search([('name', '=', tax_val)], limit=1)
                if not tax:
                    raise ValidationError(_("Tax with name '%s' not found.") % tax_val)
                vals['tax_id'] = tax.id

        return vals

    def _to_api_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "priority": self.priority,
            "club_id":{
                "id": self.sport_club_id.id if self.sport_club_id else False,
                "name":self.sport_club_id.display_name if self.sport_club_id else "",
            },
            "sport_id":{
                "id": self.sport_id.id if self.sport_id else False,
                "name": self.sport_id.display_name if self.sport_id else "",
            },
            "facility_id":{
                "id": self.facility_id.id if self.facility_id else False,
                "name": self.facility_id.display_name if self.facility_id else False,
            },
            "tax_id": {
                "id": self.tax_id.id if self.tax_id else False,
                "name": self.tax_id.display_name if self.tax_id else "",
                "type": self.tax_id.type_tax_use if self.tax_id else "",
                "amount": f"{round(self.tax_id.amount, 2)} %" if self.tax_id else "",
            },
            "currency_id":{
                "id": self.currency_id.id if self.currency_id else False,
                "name": self.currency_id.name if self.currency_id else False,
                "symbol": self.currency_id.symbol if self.currency_id else False,
            },
            "date_range":{
                "date_from": fields.Date.to_string(self.date_from) if self.date_from else None,
                "date_to": fields.Date.to_string(self.date_to) if self.date_to else None,
            },
            "base_price": self.base_price,
            "active": self.active,
        }
