# -*- coding: utf-8 -*-
from odoo.http import Response
import json

def valid_response(body=None, message="Success", code=200, status=200):
    """
    Return a standardized success JSON response.
    """
    if body is None:
        body = {}
    return Response(
        json.dumps({
            "code": code,
            "message": message,
            "body": body or {}
        }),
        status=status,
        content_type='application/json'
    )

def invalid_response(message="Invalid request", body=None, code=400, status=400):
    """
    Return a standardized invalid request response (e.g. validation errors).
    """
    if body is None:
        body = {}
    return Response(
        json.dumps({
            "code": code,
            "message": message,
            "body": body or {}
        }),
        status=status,
        content_type='application/json'
    )

def error_response(message="An unexpected error occurred", body=None, code=500, status=500):
    """
    Return a standardized error response (e.g. server error, exceptions).
    """
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
