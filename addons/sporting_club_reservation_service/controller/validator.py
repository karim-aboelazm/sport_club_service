import jwt
import secrets
import datetime
import os
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

os.environ['ODOO_JWT_KEY'] = "MySuperSecretKey123"

class Validator:
    DEFAULT_KEY = "MySuperSecretKey123"

    def key(self):
        return os.environ.get('ODOO_JWT_KEY',self.DEFAULT_KEY)

    def create_token(self, user):
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        payload = {
            'sub': user['id'],
            'lgn': user['login'],
            'iat': datetime.datetime.utcnow(),
            'exp': exp
        }
        token = jwt.encode(payload, self.key(), algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        self.save_token(token, user['id'], exp)
        return token

    def save_token(self, token, uid, exp):
        request.env['jwt_provider.access_token'].sudo().create({
            'user_id': uid,
            'expires': exp.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'token': token,
        })

    def verify(self, token, env=None):
        env = env or request.env
        record = env['jwt_provider.access_token'].sudo().search([('token', '=', token)], limit=1)
        if not record or record.is_expired:
            return False
        return record.user_id

    def verify_token(self, token):
        result = {'status': False, 'message': None}
        try:
            # payload = jwt.decode(token, self.key(), algorithms=['HS256'])
            user = self.verify(token)
            if not user:
                result.update({'message': 'Token invalid or expired', 'code': 498})
                return result
            result.update({'status': True, 'user': user})
            return result
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            result.update({'message': 'Token invalid or expired', 'code': 498})
            return result

validator = Validator()
