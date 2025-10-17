# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from .utils import check_api_key
from .responses import valid_response, error_response, invalid_response


class SportClubSportsAPIController(http.Controller):
    # -------------------------------------------------------
    # CREATE
    # -------------------------------------------------------
    @http.route('/api/sport/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def create_sport(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.sports'].sudo()._api_create_sport(data)
            return valid_response(code=200, message="Sport created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    # -------------------------------------------------------
    # SEARCH ALL
    # -------------------------------------------------------
    @http.route('/api/sport/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
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

    # -------------------------------------------------------
    # GET ONE
    # -------------------------------------------------------
    @http.route('/api/sport/search/one/<int:sport_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def get_sport(self, sport_id):
        try:
            result = request.env['sport.club.sports'].sudo()._api_get_sport(sport_id)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    # -------------------------------------------------------
    # FILTER BY KEYWORD
    # -------------------------------------------------------
    @http.route('/api/sport/filter/<string:keyword>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def filter_sports(self, keyword):
        try:
            result = request.env['sport.club.sports'].sudo()._api_filter_sports_with_keyword(keyword)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    # -------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------
    @http.route('/api/sport/update/<int:sport_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
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

    # -------------------------------------------------------
    # DELETE
    # -------------------------------------------------------
    @http.route('/api/sport/delete/<int:sport_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def delete_sport(self, sport_id):
        try:
            result = request.env['sport.club.sports'].sudo()._api_delete_sport(sport_id)
            return valid_response(code=200, message="Sport deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
