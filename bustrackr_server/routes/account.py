from flask import Blueprint, request
from functools import wraps
import orjson
from bustrackr_server.utils import orjson_default
from bustrackr_server.services.authentication_service import (
    authenticate,
    generate_jwt_token,
    validate_jwt_token,
    create_user
)
import jwt

account_bp = Blueprint('account', __name__)

def token_required(f):
    """
    A decorator function to ensure the JWT token is present and valid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Extract token from the 'Authorization' header
        auth_header = request.headers.get('Authorization')
        if auth_header and 'Bearer' in auth_header:
            token = auth_header.split(" ")[1]  # Extract token part
        
        if not token:
            return orjson.dumps({'status': 'error', 'message': 'Token is missing'}), 401

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
        validate_request(req, {'email', 'password'})
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    try:
        email = req['email']
        password = req['password']
        
        user = authenticate(email, password)
        
        if not user:
            return orjson.dumps({'status': 'error', 'message': 'Invalid email or password'}), 401
        
        token = generate_jwt_token(user)

        response = {
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'userData': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'registration_date': user.registration_date,
            },
        }
        return orjson.dumps(response, default=orjson_default), 200
    
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
        validate_request(req, {'username', 'email', 'password', 'date_of_birth'})
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    try:
        username = req['username']
        email = req['email']
        password = req['password']
        date_of_birth = req['date_of_birth']
        
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
                    
        token = generate_jwt_token(user)

        response = {
            'status': 'success',
            'message': 'Registration successful',
            'token': token,
            'userData': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'registration_date': user.registration_date,
            },
        }
        return orjson.dumps(response, default=orjson_default), 200
    
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
    
