# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request

class SportClubPolicyAPIController(http.Controller):
    @http.route('/api/policy/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_policy(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.policy'].sudo()._api_create_policy(data)
            return valid_response(code=200, message="Policy created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/policy/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_policies(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            policies = request.env['sport.club.policy'].sudo()._api_search_policies(domain=domain, limit=limit, offset=offset)
            return valid_response(code=200, message="Success", body=policies)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/policy/search/one/<int:policy_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_policy(self, policy_id):
        try:
            result = request.env['sport.club.policy'].sudo()._api_get_policy(policy_id)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/policy/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_policies(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.policy'].sudo()._api_filter_policies_with_keyword(keyword)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/policy/update/<int:policy_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_policy(self, policy_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = policy_id
            result = request.env['sport.club.policy'].sudo()._api_update_policy(data)
            return valid_response(code=200, message="Policy updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/policy/delete/<int:policy_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_policy(self, policy_id):
        try:
            result = request.env['sport.club.policy'].sudo()._api_delete_policy(policy_id)
            return valid_response(code=200, message="Policy deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
