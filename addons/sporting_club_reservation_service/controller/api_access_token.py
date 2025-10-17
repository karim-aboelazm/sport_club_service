import json
from odoo import http, fields
from odoo.http import request
from datetime import timedelta
from .utils import check_api_key
from .responses import valid_response,invalid_response,error_response

class ApiTokenAuthController(http.Controller):
    @http.route('/user/authenticate', type='http', auth="none", methods=['POST'], csrf=False, save_session=False, cors="*")
    def get_token(self):
        try:
            # Parse request body
            byte_string = request.httprequest.data
            if not byte_string:
                return invalid_response(
                    message="Missing request body",
                    body={},
                    code=400
                )

            data = json.loads(byte_string.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return invalid_response(
                    message="Username and password are required",
                    body={"missing": ["username" if not username else None, "password" if not password else None]},
                    code=400
                )

            # Authenticate user
            credentials = {'login': username, 'password': password, 'type': 'password'}
            user_info = request.session.authenticate(request.db, credentials)

            if not user_info:
                return invalid_response(
                    message="Invalid username or password",
                    body={},
                    code=401
                )

            # Generate API key token
            env = request.env(user=request.env.user.browse(user_info['uid']))
            env['res.users.apikeys.description'].check_access_make_key()

            expiration_date = fields.Date.today() + timedelta(days=1)
            token = env['res.users.apikeys']._generate("access_token", username, expiration_date)

            payload = {
                "user_id": user_info['uid'],
                "username": username,
                "token": token
            }

            return valid_response(
                body=payload,
                message="User authenticated successfully",
                code=200
            )

        except Exception as e:
            # Catch any unexpected errors
            return error_response(
                message="Failed to authenticate user",
                body={"error": str(e)},
                code=500
            )

    @check_api_key(scope='access_token')
    @http.route('/api/contacts', type='http', auth="none", methods=['GET'], csrf=False, save_session=False, cors="*")
    def get_contacts(self):
        try:
            partners = request.env['res.partner'].sudo().search([])  # sudo ensures we bypass access error
            if not partners:
                return valid_response(
                    code=200,
                    message="No contacts found",
                    body={"count": 0, "contacts": []}
                )

            contacts_data = []
            for partner in partners:
                contacts_data.append({
                    "id": partner.id,
                    "name": partner.name,
                    "email": partner.email,
                    "phone": partner.phone,
                    "mobile": partner.mobile,
                    "is_company": partner.is_company,
                })

            return valid_response(
                code=200,
                message="Contacts retrieved successfully",
                body={
                    "count": len(contacts_data),
                    "contacts": contacts_data
                }
            )

        except Exception as e:
            return error_response(
                code=500,
                message="Failed to retrieve contacts",
                body={"error": str(e)}
            )
