# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request

class SportClubFacilityAPIController(http.Controller):

    @http.route('/api/facility/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_facility(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.facility'].sudo()._api_create_facility(data)
            return valid_response(code=200, message="Facility created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/facility/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_facilities(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            facilities = request.env['sport.club.facility'].sudo()._api_search_facilities(domain=domain, limit=limit, offset=offset)
            return valid_response(code=200, message="Success", body=facilities)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/facility/search/one/<int:facility_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_facility(self, facility_id):
        try:
            result = request.env['sport.club.facility'].sudo()._api_get_facility(facility_id)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/facility/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_facilities(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.facility'].sudo()._filter_facilities_with_keywords(keyword)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/facility/update/<int:facility_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_facility(self, facility_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = facility_id
            result = request.env['sport.club.facility'].sudo()._api_update_facility(data)
            return valid_response(code=200, message="Facility updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/facility/delete/<int:facility_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_facility(self, facility_id):
        try:
            result = request.env['sport.club.facility'].sudo()._api_delete_facility(facility_id)
            return valid_response(code=200, message="Facility deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
