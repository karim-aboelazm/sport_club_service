# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from .utils import check_api_key, valid_response, invalid_response, error_response


class SportClubPromotionAPIController(http.Controller):

    @http.route('/api/promotion/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_promotion(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.promotion'].sudo()._api_create_promotion(data)
            return valid_response(code=200, message="Promotion created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/promotion/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_promotions(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            records = request.env['sport.club.promotion'].sudo()._api_search_promotions(domain=domain, limit=limit, offset=offset)
            message = "success" if records and len(records) > 0 else "There is no data found"
            return valid_response(code=200, message=message, body=records)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/promotion/search/one/<int:promotion_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_promotion(self, promotion_id):
        try:
            result = request.env['sport.club.promotion'].sudo()._api_get_promotion(promotion_id)
            message = "success" if result else "There is no data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/promotion/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_promotions(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.promotion'].sudo()._api_filter_promotions_with_keyword(keyword)
            message = "success" if result else "There is no data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/promotion/update/<int:promotion_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_promotion(self, promotion_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = promotion_id
            result = request.env['sport.club.promotion'].sudo()._api_update_promotion(data)
            return valid_response(code=200, message="Promotion updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/promotion/delete/<int:promotion_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_promotion(self, promotion_id):
        try:
            result = request.env['sport.club.promotion'].sudo()._api_delete_promotion(promotion_id)
            return valid_response(code=200, message="Promotion deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
