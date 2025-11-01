# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request

class SportClubSportsAPIController(http.Controller):

    @http.route('/api/sport/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_sport(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.sports'].sudo()._api_create_sport(data)
            return valid_response(code=200, message="Sport created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/sport/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_sports(self):
        try:
            # Optional body for domain, limit, offset
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            sports = request.env['sport.club.sports'].sudo()._api_search_sports(domain=domain, limit=limit, offset=offset)
            return valid_response(code=200, message="Success", body=sports)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/sport/search/one/<int:sport_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_sport(self, sport_id):
        try:
            result = request.env['sport.club.sports'].sudo()._api_get_sport(sport_id)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/sport/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_sports(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.sports'].sudo()._api_filter_sports_with_keyword(keyword)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/sport/update/<int:sport_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_sport(self, sport_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = sport_id
            result = request.env['sport.club.sports'].sudo()._api_update_sport(data)
            return valid_response(code=200, message="Sport updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/sport/delete/<int:sport_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_sport(self, sport_id):
        try:
            result = request.env['sport.club.sports'].sudo()._api_delete_sport(sport_id)
            return valid_response(code=200, message="Sport deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
