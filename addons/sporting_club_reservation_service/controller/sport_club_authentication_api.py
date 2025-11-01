# -*- coding: utf-8 -*-
from .utils import *
from datetime import timedelta
from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import AccessDenied


class ApiTokenAuthController(http.Controller):

    @http.route('/user/authenticate', type='http', auth="none", methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self):
        try:
            byte_string = request.httprequest.data
            if not byte_string:
                return invalid_response(message="Missing request body", body={}, code=400)

            data = json.loads(byte_string.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            token_expiration_days = data.get('days',1)

            if not username or not password:
                body = {"missing": ["username" if not username else None, "password" if not password else None]}
                return invalid_response(message="Username and password are required", body=body, code=400)

            # 1. Check if the user exists in the database
            User = request.env['res.users']
            user_record = User.sudo().search([('login', '=', username)], limit=1)

            if not user_record:
                return invalid_response(message="Invalid username", body={}, code=401)

            # 2. Authenticate user using credentials
            credentials = {'login': username, 'password': password, 'type': 'password'}
            user_info = request.session.authenticate(request.db, credentials)

            if not user_info:
                return invalid_response(message="Invalid password for this username", body={}, code=401)

            env = request.env(user=request.env.user.browse(user_info['uid']))
            env['res.users.apikeys.description'].check_access_make_key()
            expiration_date = fields.Date.today() + timedelta(days=int(token_expiration_days))
            token = env['res.users.apikeys']._generate("access_token", username, expiration_date)
            payload = {"user_id": user_info['uid'], "username": username, "token": token}
            return valid_response(body=payload, message="User authenticated successfully", code=200)

        except Exception as e:
            return error_response(message="Failed to authenticate user", body={"error": str(e)}, code=500)