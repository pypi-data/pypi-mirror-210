"""Authentication helper functions
"""
import os
import requests
from flask import request
from .jwt import jwt_manager
from flask_jwt_extended import jwt_required, get_jwt_identity


# Accept user name passed in Basic Auth header
# (password has to checkded before!)
ALLOW_BASIC_AUTH_USER = os.environ.get('ALLOW_BASIC_AUTH_USER', 'False') \
    .lower() in ('t', 'true')


def auth_manager(app, api=None):
    """Authentication setup for Flask app"""
    # Setup the Flask-JWT-Extended extension
    return jwt_manager(app, api)


def optional_auth(fn):
    """Authentication view decorator"""
    return jwt_required(optional=True)(fn)


def get_identity():
    geon_token = request.cookies.get('geon_token_cookie')
    pgrstheader = {}
    pgrstheader['Authorization'] = 'Bearer {}'.format(geon_token)
    pgrstresponse = requests.post("http://qwc-postgrest-server:3000/rpc/check_user", headers=pgrstheader)
    json_response=pgrstresponse.json()
    identity = json_response.get('username')
    return identity


def get_username(identity):
    """Get username"""
    if identity:
        if isinstance(identity, dict):
            username = identity.get('username')
        else:
            # identity is username
            username = identity
    else:
        username = None
    return username


def get_groups(identity):
    """Get user groups"""
    groups = []
    if identity:
        if isinstance(identity, dict):
            groups = identity.get('groups', [])
            group = identity.get('group')
            if group:
                groups.append(group)
    return groups


def get_auth_user():
    """Get identity or optional pre-authenticated basic auth user"""
    identity = get_identity()
    if not identity and ALLOW_BASIC_AUTH_USER:
        auth = request.authorization
        if auth:
            # We don't check password, already authenticated!
            identity = auth.username
    return identity
