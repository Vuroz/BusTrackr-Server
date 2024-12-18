from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from bustrackr_server import db
from bustrackr_server.models import User
from bustrackr_server import Config
from argon2 import PasswordHasher
import jwt
import datetime
from flask import Request

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)

def validate_password(stored_hash: str, password: str) -> bool:
    """Validate the password using Argon2."""
    try:
        ph.verify(stored_hash, password)
        return True
    except Exception:
        return False

def authenticate(email: str, password: str) -> User:
    """Authenticate user details with database."""
    user_query = select(User).where(User.email == email)
    user = db.session.execute(user_query).scalars().first()
    if user and validate_password(user.password_hash, password):
        return user
    return None

def create_user(username: str, email: str, password: str, date_of_birth: str) -> User:
    """Create a user in the database."""
    # Check if username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        if existing_user.username == username:
            raise ValueError('Username is already taken')
        elif existing_user.email == email:
            raise ValueError('Email is already taken')
    
    try:
        hashed_password = hash_password(password)
        new_user = User(username=username, email=email, password_hash=hashed_password.encode('utf-8'), date_of_birth=date_of_birth)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except IntegrityError as e:
        db.session.rollback()
        raise e

def generate_jwt_token(user: User) -> str:
    """
    Function for generating a JWT token.
    This function will create and return a JWT token for the authenticated user.
    """
    
    secret_key = Config.JWT_SECRET
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def validate_jwt_token(request: Request, token: str) -> None:
    secret_key = Config.JWT_SECRET
    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            
    # Attach user information to the request context
    request.user = { 'id': decoded_token['user_id'] }