# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request


class SportClubPricingRuleAPIController(http.Controller):

    @http.route('/api/pricing/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_pricing_rule(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.pricing.rule'].sudo()._api_create_pricing_rule(data)
            return valid_response(code=200, message="Pricing rule created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/pricing/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_pricing_rules(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            rules = request.env['sport.club.pricing.rule'].sudo()._api_search_pricing_rules(domain=domain, limit=limit, offset=offset)
            message = "success" if rules and len(rules) > 0 else "There is no data found"
            return valid_response(code=200, message=message, body=rules)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/pricing/search/one/<int:rule_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_pricing_rule(self, rule_id):
        try:
            result = request.env['sport.club.pricing.rule'].sudo()._api_get_pricing_rule(rule_id)
            message = "success" if result else "There is no data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/pricing/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_pricing_rules(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.pricing.rule'].sudo()._api_filter_pricing_rules_with_keyword(keyword)
            message = "success" if result else "There is no data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/pricing/update/<int:rule_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_pricing_rule(self, rule_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = rule_id
            result = request.env['sport.club.pricing.rule'].sudo()._api_update_pricing_rule(data)
            return valid_response(code=200, message="Pricing rule updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/pricing/delete/<int:rule_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_pricing_rule(self, rule_id):
        try:
            result = request.env['sport.club.pricing.rule'].sudo()._api_delete_pricing_rule(rule_id)
            return valid_response(code=200, message="Pricing rule deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))