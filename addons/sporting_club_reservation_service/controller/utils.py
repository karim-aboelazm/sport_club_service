import functools
from odoo import http
from odoo.http import request
from .responses import invalid_response, error_response


def check_api_key(scope=None):
    """
    Decorator to protect endpoints with Bearer API token authentication.
    Uses standardized response structure for all errors.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Extract Authorization header
                auth_header = request.httprequest.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return invalid_response(
                        code=401,
                        message="Missing or invalid Authorization header",
                        body={}
                    )

                # Extract token
                key = auth_header.split(' ')[1]
                user_id = request.env['res.users.apikeys']._check_credentials(scope=scope, key=key)

                if not user_id:
                    return invalid_response(
                        code=401,
                        message="Invalid or expired API token",
                        body={}
                    )

                # Attach authenticated user to the request environment
                user = request.env['res.users'].browse(user_id)
                request.update_env(user=user)

                # Proceed to actual route
                return func(*args, **kwargs)

            except Exception as e:
                return error_response(
                    code=500,
                    message="API Key validation failed",
                    body={"error": str(e)}
                )

        return wrapper
    return decorator
