# -*- coding: utf-8 -*-
from .utils import *
from odoo import http
from odoo.http import request
from .jwt_http import jwt_http
from .validator import validator
import json

class JwtController(http.Controller):

    @http.route('/api/login', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def login(self):
        data = json.loads(request.httprequest.data.decode('utf-8'))
        username = data.get('email')
        password = data.get('password')
        credential = {'login': username, 'password': password, 'type': 'password'}
        try:
            auth_info = request.session.authenticate(request.db, credential)
        except Exception:
            return error_response(code=400, message="Incorrect login")

        user = request.env.user
        token = validator.create_token(user)
        payload = {"user_id": user.id, "username": username, "token": token}
        return valid_response(body=payload)

    @http.route('/api/me', type='http', auth='public', csrf=False, cors='*')
    @check_api_key()
    def me(self):
        _, _, _, token = jwt_http.parse_request()
        payload = request.env.user.to_dict(single=True)
        return valid_response(body=payload)

    @http.route('/api/logout', type='http', auth='public', csrf=False, cors='*')
    def logout(self):
        _, _, _, token = jwt_http.parse_request()
        result = validator.verify_token(token)
        if not result['status']:
            return error_response(result['code'], result['message'])
        jwt_http.do_logout(token)
        return valid_response(message="Logged out successfully")
