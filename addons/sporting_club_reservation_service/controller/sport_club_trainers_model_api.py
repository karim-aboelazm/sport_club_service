# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from .utils import check_api_key, valid_response, invalid_response, error_response


class SportClubTrainerAPIController(http.Controller):

    # -------------------------------------------------------
    # CREATE
    # -------------------------------------------------------
    @http.route('/api/trainer/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_trainer(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.trainer'].sudo()._api_create_trainer(data)
            return valid_response(code=200, message="Trainer created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    # -------------------------------------------------------
    # LIST / SEARCH ALL
    # -------------------------------------------------------
    @http.route('/api/trainer/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_trainers(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            records = request.env['sport.club.trainer'].sudo()._api_search_trainers(domain=domain, limit=limit, offset=offset)
            message = "success" if records and len(records) > 0 else "There is no data found"
            return valid_response(code=200, message=message, body=records)
        except Exception as e:
            return error_response(code=400, message=str(e))

    # -------------------------------------------------------
    # GET ONE
    # -------------------------------------------------------
    @http.route('/api/trainer/search/one/<int:trainer_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_trainer(self, trainer_id):
        try:
            result = request.env['sport.club.trainer'].sudo()._api_get_trainer(trainer_id)
            message = "success" if result else "There is no data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    # -------------------------------------------------------
    # FILTER
    # -------------------------------------------------------
    @http.route('/api/trainer/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_trainers(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.trainer'].sudo()._api_filter_trainers_with_keyword(keyword)
            message = "success" if result else "There is no data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    # -------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------
    @http.route('/api/trainer/update/<int:trainer_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_trainer(self, trainer_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = trainer_id
            result = request.env['sport.club.trainer'].sudo()._api_update_trainer(data)
            return valid_response(code=200, message="Trainer updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    # -------------------------------------------------------
    # DELETE
    # -------------------------------------------------------
    @http.route('/api/trainer/delete/<int:trainer_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_trainer(self, trainer_id):
        try:
            result = request.env['sport.club.trainer'].sudo()._api_delete_trainer(trainer_id)
            return valid_response(code=200, message="Trainer deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
