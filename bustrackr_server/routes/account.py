from flask import Blueprint, make_response, request
from functools import wraps
import orjson
from bustrackr_server.config import Config
from bustrackr_server.utils import orjson_default
from bustrackr_server.services.authentication_service import (
    add_jwt_token,
    renew_jwt_token,
    validate_jwt_token,
    clear_jwt_token,
    authenticate,
    create_user,
    getUserDetails,
)
import jwt
from datetime import datetime, date
import re

account_bp = Blueprint('account', __name__)

def token_required(f):
    """
    A decorator function to ensure the JWT token is present and valid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('authToken')
        
        silence_unauth = request.headers.get('X-Silence-Unauthorized', 'false').lower() == 'true'
        
        if not token:
            return orjson.dumps({'status': 'error', 'message': 'Token is missing'}), 200 if silence_unauth else 401

        try:
            validate_jwt_token(request, token)
        except jwt.ExpiredSignatureError:
            return orjson.dumps({'status': 'error', 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return orjson.dumps({'status': 'error', 'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    
    return decorated


# curl -X POST http://localhost:5251/api/login \      
#      -H "Content-Type: application/json" \
#      -d '{"email": "<EMAIL>", "password": "<PASSWORD>"}'

@account_bp.route('/login', methods=['POST'])
def authenticate_user():
    try:
        req = request.get_json()
        validate_request(req, {'email', 'password', 'long_expire'})
        
        # Validate data types
        if not all(isinstance(req[field], str) for field in ['email', 'password']):
            return orjson.dumps({'status': 'error', 'message': 'Email, and password must be strings'}), 400
        
        if not all(isinstance(req[field], bool) for field in [ 'long_expire']):
            return orjson.dumps({'status': 'error', 'message': 'Terms of service, data policy, and long_expire must be booleans'}), 400
    
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    try:
        email = req['email']
        password = req['password']
        long_expire = req['long_expire']
        
        user = authenticate(email, password)
        
        if not user:
            return orjson.dumps({'status': 'error', 'message': 'Invalid email or password'}), 401

        response = make_response(orjson.dumps({
            'status': 'success',
            'message': 'Login successful',
            'userData': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'registration_date': user.registration_date,
            },
        }, default=orjson_default))

        add_jwt_token(response, user.id, long_expire)

        return response, 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
# curl -X POST http://localhost:5251/api/register \
#      -H "Content-Type: application/json" \
#      -d '{"username": "testuser", "password": "password123", "email": "test@test.com", "date_of_birth": "2002-06-16"}'
    
@account_bp.route('/register', methods=['POST'])
def register_user():
    try:
        req = request.get_json()
        validate_request(req, {'username', 'email', 'password', 'date_of_birth', 'terms_of_service', 'data_policy', 'long_expire'})
        
        # Validate data types
        if not all(isinstance(req[field], str) for field in ['username', 'email', 'password', 'date_of_birth']):
            return orjson.dumps({'status': 'error', 'message': 'Username, email, password, and date_of_birth must be strings'}), 400
        
        if not all(isinstance(req[field], bool) for field in ['terms_of_service', 'data_policy', 'long_expire']):
            return orjson.dumps({'status': 'error', 'message': 'Terms of service, data policy, and long_expire must be booleans'}), 400
            
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    # Validate username length
    if len(req['username']) < 3:
        return orjson.dumps({'status': 'error', 'message': 'Username must be at least 3 characters.'}), 400
    
    # Validate email format using regex
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', req['email']):
        return orjson.dumps({'status': 'error', 'message': 'Invalid email format'}), 400
    
    # Validate password length
    if len(req['password']) < 5:
        return orjson.dumps({'status': 'error', 'message': 'Password must be at least 5 characters.'}), 400
    
    # Validate age (13+ years)
    try:
        birth_date = datetime.strptime(req['date_of_birth'], '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 13:
            return orjson.dumps({'status': 'error', 'message': 'Must be at least 13 years old.'}), 400
    except ValueError:
        return orjson.dumps({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    
    # Validate terms of service and data policy acceptance
    if not req['terms_of_service'] or not req['data_policy']:
        return orjson.dumps({'status': 'error', 'message': 'You must accept the Terms of Service and Data Policy.'}), 400
    
    try:
        username = req['username']
        email = req['email']
        password = req['password']
        date_of_birth = req['date_of_birth']
        long_expire = req['long_expire']
        
        try:
            user = create_user(username, email, password, date_of_birth)
        except ValueError as e:
            if 'Username is already taken' in str(e):
                return orjson.dumps({'status': 'error', 'message': 'Username is already taken'}), 400
            elif 'Email is already taken' in str(e):
                return orjson.dumps({'status': 'error', 'message': 'Email is already taken'}), 400
            else:
                return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
        except:
            return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

        response = make_response(orjson.dumps({
            'status': 'success',
            'message': 'Login successful',
            'userData': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'registration_date': user.registration_date,
            },
        }, default=orjson_default))

        # Add JWT token.
        add_jwt_token(response, user.id, long_expire)

        return response, 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500


@account_bp.route('/re-auth', methods=['POST'])
@token_required
def reauthenticate_user():
    try:
        user = getUserDetails(request.user['id'])
        
        if not user:
            return orjson.dumps({'status': 'error', 'message': 'Invalid user.'}), 401

        response = make_response(orjson.dumps({
            'status': 'success',
            'message': 'Reauthentication successful',
            'userData': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'registration_date': user.registration_date,
            },
        }, default=orjson_default))

        # Renew authToken.
        renew_jwt_token(response, request)

        return response, 200
    
    except KeyError as e:
        raise e
        #return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

@account_bp.route('/logout', methods=['POST'])
@token_required
def logout_user():
    try:
        response = make_response(orjson.dumps({
            'status': 'success',
            'message': 'Logout successful',
        }, default=orjson_default))

        # Clear the JWT token
        clear_jwt_token(response)

        return response, 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500


# curl -X POST http://localhost:5251/api/make-change \
#      -H "Content-Type: application/json" \
#      -H "Authorization: Bearer <TOKEN>" \

@account_bp.route('/make-change', methods=['POST'])
@token_required
def make_change():
    try:
        response = {
            'status': 'success',
            'message': 'Change successful',
            'changeBy': request.user['id'],
        }
        return orjson.dumps(response, default=orjson_default), 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

def validate_request(req: dict, required_fields: dict) -> None:
    if req is None:
        raise TypeError("Content-Type is incorrect, JSON is malformed, or empty")
    if not required_fields.issubset(req):
        raise ValueError("Missing required fields")
    
