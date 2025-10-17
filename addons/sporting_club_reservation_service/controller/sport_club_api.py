import json
from odoo import http
from odoo.http import request
from .utils import check_api_key
from .responses import valid_response, error_response,invalid_response

class SportClubAPI(http.Controller):

    @http.route('/api/create/club', type='http', auth='none', methods=['POST'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def create_club(self):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body",body={},code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            result = request.env['sport.club.model'].sudo()._api_create_club(data)
            return valid_response(code=200,message="Club created successfully",body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/search/all', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def list_clubs(self):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            domain = data.get("domain", [])
            limit = data.get("limit",100)
            offset = data.get("offset",0)

            clubs = request.env['sport.club.model'].sudo()._api_search_clubs(domain=domain,limit=limit,offset=offset)
            return valid_response(code=200,message="Success",body=clubs)
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/search/one/<int:club_id>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def get_club(self, club_id):
        try:
            result = request.env['sport.club.model'].sudo()._api_get_club(club_id)
            return valid_response(code=200,message="Success",body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/filter/clubs/<string:keyword>', type='http', auth='none', methods=['GET'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def filter_clubs(self, keyword):
        try:
            result = request.env['sport.club.model'].sudo()._filter_clubs_with_keywords(keyword)
            return valid_response(code=200,message="Success",body=result)
        except Exception as e:
            return error_response(code=404, message=str(e))

    @http.route('/api/update/club/<int:club_id>', type='http', auth='none', methods=['PUT'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def update_club(self, club_id):
        try:
            if not request.httprequest.data:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(request.httprequest.data.decode('utf-8'))
            data['id'] = club_id
            result = request.env['sport.club.model'].sudo()._api_update_club(data)
            return valid_response(
                code=200,
                message="Club updated successfully",
                body=result
            )
        except Exception as e:
            return error_response(code=400, message=str(e))

    @http.route('/api/delete/club/<int:club_id>', type='http', auth='none', methods=['DELETE'], csrf=False, save_session=False, cors="*")
    @check_api_key(scope='access_token')
    def delete_club(self, club_id):
        try:
            result = request.env['sport.club.model'].sudo()._api_delete_club(club_id)
            return valid_response(code=200,message="Club deleted successfully",body=result)
        except Exception as e:
            return error_response(code=400, message=str(e))
