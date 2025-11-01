# -*- coding: utf-8 -*-
import json
import functools
import traceback
import odoo
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError, MissingError
import random
import string
import os
from dateutil.parser import parse
from .validator import Validator

class Util:
    addons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self):
        self.addons_path = self.addons_path.replace('jwt_provider', '')

    def generate_verification_code(self, len=8):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len))

    def toDate(self, pgTimeStr):
        return parse(pgTimeStr)

    def path(self, *paths):
        return os.path.join(self.addons_path, *paths)

    def add_branch(self, tree, vector, value):
        key = vector[0]
        tree[key] = value if len(vector) == 1 else self.add_branch(tree[key] if key in tree else {}, vector[1:], value)
        return tree

    def create_dict(self, d):
        res = {}
        for k, v in d.items():
            ar = k.split('.')
            filter(None, ar)
            self.add_branch(res, ar, v)
        return res


util = Util()

# ============================================================
# HELPER: UNEXPECTED ERROR TRACEBACK
# ============================================================
def unexpected_error(e):
    body = {"error": str(e)}
    try:
        if odoo.tools.config.get('dev_mode'):
            body["traceback"] = traceback.format_exc()
    except Exception:
        body["traceback"] = traceback.format_exc()
    return body


# ============================================================
# CENTRALIZED ERROR HANDLER
# ============================================================
def handle_odoo_exception(e):
    code = 500
    message = "Internal Server Error"
    body = {"error": str(e)}

    if isinstance(e, AccessDenied):
        code = 401
        message = "Access denied"
    elif isinstance(e, AccessError):
        code = 403
        message = "Access error"
    elif isinstance(e, UserError):
        code = 400
        message = "User error"
    elif isinstance(e, ValidationError):
        code = 422
        message = "Validation error"
    elif isinstance(e, MissingError):
        code = 404
        message = "Record not found"
    else:
        body = unexpected_error(e)

    return error_response(
        code=code,
        message=message,
        body=body,
        status=code
    )


# ============================================================
# DECORATOR FOR API KEY VALIDATION
# ============================================================
def check_api_key():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                auth_header = request.httprequest.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return invalid_response(
                        code=401,
                        message="Missing or invalid Authorization header",
                        body={}
                    )
                key = auth_header.split(' ')[1].strip()
                validator = Validator()
                result = validator.verify_token(key)
                if not result['status']:
                    return invalid_response(code=result['code'], message=result['message'], body={})

                user = result['user']
                request.update_env(user=user)
                return func(*args, **kwargs)

            except Exception as e:
                return handle_odoo_exception(e)

        return wrapper
    return decorator


# ============================================================
# STANDARD VALID RESPONSE
# ============================================================
def valid_response(body=None, message="Success", code=200, status=200):
    if body is None:
        body = {}
    return Response(
        json.dumps({
            "code": code,
            "message": message,
            "body": body
        }),
        status=status,
        content_type='application/json'
    )


# ============================================================
# STANDARD INVALID RESPONSE
# ============================================================
def invalid_response(message="Invalid request", body=None, code=400, status=400):
    if body is None:
        body = {}
    return Response(
        json.dumps({"code": code, "message": message, "body": body}),
        status=status,
        content_type='application/json'
    )


# ============================================================
# STANDARD ERROR RESPONSE
# ============================================================
def error_response(message="An unexpected error occurred", body=None, code=500, status=500):
    if body is None:
        body = {}
    return Response(
        json.dumps({"code": code, "message": message, "body": body}),
        status=status,
        content_type='application/json'
    )


def get_all_models():
    models_used = [
        'sport.club.calendar.exception',
        'sport.club.calendar.line',
        'sport.club.calendar',
        'sport.club.equipment.booking',
        'sport.club.facility',
        'sport.club.model',
        'sport.club.policy',
        'sport.club.pricing.rule',
        'sport.club.promotion',
        'sport.club.reservation',
        'sport.club.sports',
        'sport.club.trainer',
        'sport.club.training.session',
    ]
    return models_used