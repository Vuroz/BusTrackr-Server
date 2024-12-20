from sqlalchemy.exc import IntegrityError
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
    update_user,
    getUserDetails,
    change_password
)
import jwt
from datetime import datetime, date
import re
from typing import Dict, Any, Union, Tuple


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

@account_bp.route('/login', methods=['POST'])
def authenticate_user():
    try:
        required_fields = {
            'email': (str, True),
            'password': str,
            'long_expire': bool
}
        req = request.get_json()
        validate_request(req, required_fields)
        
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    try:
        email = req['email'].lower()
        password = req['password'].lower()
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
    
@account_bp.route('/register', methods=['POST'])
def register_user():
    try:
        required_fields = {
            'username': (str, True),
            'email': (str, True),
            'password': str,
            'date_of_birth': str,
            'terms_of_service': bool,
            'data_policy': bool,
            'long_expire': int
        }

        req = request.get_json()
        validate_request(req, required_fields)
        
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
        username = req['username'].lower()
        email = req['email'].lower()
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

@account_bp.route('/update-account', methods=['POST'])
@token_required
def update_account():
    try:
        required_fields = {
            'username': (str, True),
            'email': (str, True),
            'date_of_birth': str,
        }

        req = request.get_json()
        validate_request(req, required_fields)
        
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
    
    # Validate age (13+ years)
    try:
        birth_date = datetime.strptime(req['date_of_birth'], '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 13:
            return orjson.dumps({'status': 'error', 'message': 'Must be at least 13 years old.'}), 400
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    try:
        userID = request.user['id']
        username = req['username'].lower()
        email = req['email'].lower()
        date_of_birth = req['date_of_birth']
        
        try:
            update_user(userID, username, email, date_of_birth)
        except ValueError as e:
            if 'Username is already taken' in str(e):
                return orjson.dumps({'status': 'error', 'message': 'Username is already taken'}), 400
            elif 'Email is already taken' in str(e):
                return orjson.dumps({'status': 'error', 'message': 'Email is already taken'}), 400
            else:
                return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
        except Exception as e:
            return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

        response = make_response(orjson.dumps({
            'status': 'success',
            'message': 'Updated account details successfully',
        }, default=orjson_default))

        renew_jwt_token(response, request)

        return response, 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
@account_bp.route('/update-password', methods=['POST'])
@token_required
def update_password():
    try:
        required_fields = {
            'old_password': str,
            'new_password': str,
        }

        req = request.get_json()
        validate_request(req, required_fields)
        
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    # Validate password length
    if len(req['new_password']) < 5:
        return orjson.dumps({'status': 'error', 'message': 'New password must be at least 5 characters.'}), 400 

    try:
        user_id = request.user['id']
        old_password = req['old_password']
        new_password = req['new_password']
        
        try:
            change_password(user_id, old_password, new_password)
        except ValueError as e:
            if 'User not found' in str(e):
                return orjson.dumps({'status': 'error', 'message': 'User not found'}), 404
            elif 'Old password is incorrect' in str(e):
                return orjson.dumps({'status': 'error', 'message': 'Old password is incorrect'}), 400
            else:
                return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
        except IntegrityError as e:
            return orjson.dumps({'status': 'error', 'message': 'Database error occurred'}), 500
        except Exception as e:
            return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

        response = make_response(orjson.dumps({
            'status': 'success',
            'message': 'Password was changed successfully',
        }, default=orjson_default))

        renew_jwt_token(response, request)

        return response, 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

@account_bp.route('/make-change', methods=['POST'])
@token_required
def make_change():
    try:
        response = {
            'status': 'success',
            'message': 'Change successful',
            'changeBy': request.user['id'],
        }
        
        renew_jwt_token(response, request)
        
        return orjson.dumps(response, default=orjson_default), 200
    
    except KeyError as e:
        return orjson.dumps({'status': 'error', 'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500

def validate_request(req: Dict[str, Any], required_fields: Dict[str, Union[type, Tuple[type, bool]]]) -> None:
    """
    Validates the request against the required fields.

    Args:
        req (Dict[str, Any]): The request data to validate.
        required_fields (Dict[str, Union[type, Tuple[type, bool]]]): A dictionary where the key is the field name 
            and the value is either the required data type or a tuple specifying the required data type 
            and whether the field should be converted to lowercase.
    
    Raises:
        TypeError: If req is None or if any of the fields are not of the expected type.
        ValueError: If any of the required fields are missing.
    """
    if req is None:
        raise TypeError("Content-Type is incorrect, JSON is malformed, or empty")
    
    if not required_fields.keys() <= req.keys():
        missing_fields = required_fields.keys() - req.keys()
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    for field, field_criteria in required_fields.items():
        expected_type, convert_to_lowercase = field_criteria if isinstance(field_criteria, tuple) else (field_criteria, False)
        
        if field not in req:
            raise ValueError(f"Missing required field: {field}")
        
        value = req[field]
        
        if not isinstance(value, expected_type):
            raise TypeError(f"Field '{field}' is expected to be of type {expected_type.__name__}, but got {type(value).__name__}")
        
        if convert_to_lowercase and isinstance(value, str):
            req[field] = value.lower()
