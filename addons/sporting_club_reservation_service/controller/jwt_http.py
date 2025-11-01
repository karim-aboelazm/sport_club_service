from odoo.http import request, Response
import json
from .validator import validator

return_fields = ['id', 'login', 'name', 'company_id']

class JwtHttp:

    def response(self, success=True, message=None, data=None, code=200):
        payload = json.dumps({'success': success, 'message': message, 'data': data})
        return Response(payload, status=code, headers=[('Content-Type', 'application/json')])

    def errcode(self, code, message=None):
        return self.response(success=False, code=code, message=message)

    def do_login(self, login, password):
        credentials = {'login': login, 'password': password, 'type': 'password'}
        try:
            auth_info = request.session.authenticate(request.session.db, credentials)
            if not auth_info:
                return self.errcode(401, "Incorrect login")
        except:
            return self.errcode(401, "Incorrect login")

        user = request.env.user.read(return_fields)[0]
        token = validator.create_token(user)
        return self.response(data={'user': user, 'token': token})

    def do_logout(self, token):
        request.session.logout()
        request.env['jwt_provider.access_token'].sudo().search([('token', '=', token)]).unlink()

    def parse_request(self):
        http_method = request.httprequest.method
        body = request.params
        headers = dict(request.httprequest.headers)
        token = headers.get('Authorization', '').replace('Bearer ', '')
        return http_method, body, headers, token

jwt_http = JwtHttp()
