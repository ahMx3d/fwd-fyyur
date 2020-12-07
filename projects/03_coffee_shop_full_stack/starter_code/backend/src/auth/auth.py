import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fwd-uda-fsnd.us.auth0.com'
ALGORITHMS   = ['RS256']
API_AUDIENCE = 'drinks'

## AuthError Exception
class AuthError(Exception):
    '''
    AuthError Exception
    A standardized way to communicate auth failure modes
    '''
    def __init__(self, error, status_code):
        self.error       = error
        self.status_code = status_code

## Auth Header
def get_token_auth_header():
    """
    attempts to get the header from the request
    attempts to split bearer and the token
    Obtains the Access Token from the Authorization Header
    raises an AuthError if no header is present
    raises an AuthError if the header is malformed
    returns the token part of the header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code'       : 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code'       : 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code'       : 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code'       : 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

# Auth Permissions
def check_permissions(permission, payload):
    '''
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    raises an AuthError if permissions are not included in the payload
    raises an AuthError if the requested permission string is not in the payload permissions array
    returns true otherwise
    '''
    if 'permissions' not in payload:
        raise AuthError({
            'code'       : 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code'       : 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True

# Verify the JWT signature
def verify_decode_jwt(token):
    '''
    @INPUTS
        token: a json web token (string)

    has an Auth0 token with key id (kid)
    verifies the token using Auth0 /.well-known/jwks.json
    decodes the payload from the token
    validates the claims
    returns the decoded payload
    '''
    jsonurl           = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks              = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key           = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code'       : 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n'  : key['n'],
                'e'  : key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms = ALGORITHMS,
                audience   = API_AUDIENCE,
                issuer     = 'https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code'       : 'token_expired',
                'description': 'Token expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code'       : 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code'       : 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
                'code'       : 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

# Authentication decorator
def requires_auth(permission=''):
    '''
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    uses the get_token_auth_header method to get the token
    uses the verify_decode_jwt method to decode the jwt
    uses the check_permissions method validate claims and check the requested permission
    returns the decorator which passes the decoded payload to the decorated method
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                raise AuthError({
                    'code'       : 'invalid_header',
                    'description': 'Authorization malformed.'
                }, 401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator