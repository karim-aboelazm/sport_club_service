# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request


class SportClubReservationAPIController(http.Controller):

    @http.route('/api/reservation/create', type='http', auth='none', methods=['POST'], csrf=False, save_session=False,cors="*")
    @check_api_key()
    def create_reservation(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.reservation'].sudo()._api_create_reservation(data)
            return valid_response(code=200, message="Reservation created successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/reservation/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def list_reservations(self):
        try:
            body_data = {}
            if request.httprequest.data:
                body_data = json.loads(request.httprequest.data.decode('utf-8'))

            domain = body_data.get("domain", [])
            limit = body_data.get("limit", 100)
            offset = body_data.get("offset", 0)

            reservations = request.env['sport.club.reservation'].sudo()._api_search_reservations(domain=domain,
                                                                                                 limit=limit,
                                                                                                 offset=offset)
            message = "success" if reservations and len(reservations) > 0 else "No data found"
            return valid_response(code=200, message=message, body=reservations)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/reservation/search/one/<int:reservation_id>', type='http', auth='none', methods=['GET'],csrf=False, save_session=False, cors="*")
    @check_api_key()
    def get_reservation(self, reservation_id):
        try:
            result = request.env['sport.club.reservation'].sudo()._api_get_reservation(reservation_id)
            message = "success" if result else "No data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/reservation/filter', type='http', auth='none', methods=['GET'], csrf=False, save_session=False,cors="*")
    @check_api_key()
    def filter_reservations(self, **kwargs):
        try:
            keyword = kwargs.get('key', '').strip()
            if not keyword:
                return invalid_response(message="Missing 'key' query parameter", code=400, body={})
            result = request.env['sport.club.reservation'].sudo()._api_filter_reservations_with_keyword(keyword)
            message = "success" if result else "No data found"
            return valid_response(code=200, message=message, body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/reservation/update/<int:reservation_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def update_reservation(self, reservation_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = reservation_id
            result = request.env['sport.club.reservation'].sudo()._api_update_reservation(data)
            return valid_response(code=200, message="Reservation updated successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/reservation/delete/<int:reservation_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key()
    def delete_reservation(self, reservation_id):
        try:
            result = request.env['sport.club.reservation'].sudo()._api_delete_reservation(reservation_id)
            return valid_response(code=200, message="Reservation deleted successfully", body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))