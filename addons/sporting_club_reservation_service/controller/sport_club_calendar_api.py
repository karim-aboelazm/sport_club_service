# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request


class SportClubCalendarAPIController(http.Controller):

    @http.route('/api/calendar/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def create_calendar(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.calendar'].sudo()._api_create_calendar(data)
            return valid_response(code=200, message="Calendar created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/calendar/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_calendars(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            calendars = request.env['sport.club.calendar'].sudo()._api_search_calendars(
                domain=domain, limit=limit, offset=offset
            )
            return valid_response(code=200, message="Success", body=calendars)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/calendar/search/one/<int:calendar_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_calendar(self, calendar_id):
        try:
            result = request.env['sport.club.calendar'].sudo()._api_get_calendar(calendar_id)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/calendar/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def filter_calendars(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.calendar'].sudo()._api_filter_calendars_with_keyword(keyword)
            return valid_response(code=200, message="Success", body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/calendar/update/<int:calendar_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_calendar(self, calendar_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = calendar_id
            result = request.env['sport.club.calendar'].sudo()._api_update_calendar(data)
            return valid_response(code=200, message="Calendar updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/calendar/delete/<int:calendar_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_calendar(self, calendar_id):
        try:
            result = request.env['sport.club.calendar'].sudo()._api_delete_calendar(calendar_id)
            return valid_response(code=200, message="Calendar deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
