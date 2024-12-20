from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from bustrackr_server import db
from bustrackr_server.models import AgreementLog, LoginLog, ReportLog, User, agreement_enum
from bustrackr_server import Config
from argon2 import PasswordHasher
import jwt
import datetime
from flask import Request, Response

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

def authenticate(email: str, password: str, ip: str) -> User:
    """Authenticate user details with database."""
    user_query = select(User).where(User.email == email)
    user = db.session.execute(user_query).scalars().first()
    if user and validate_password(user.password_hash, password):
        log_login(user.id, ip)
        return user
    return None

def getUserDetails(id: int) -> User:
    """Get user details from an user ID."""
    user_query = select(User).where(User.id == id)
    return db.session.execute(user_query).scalars().first()

def create_user(username: str, email: str, password: str, date_of_birth: str, ip: str) -> User:
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
    except IntegrityError as e:
        db.session.rollback()
        raise e
    
    log_agreement(new_user.id, "terms_of_service", ip)
    log_agreement(new_user.id, "data_policy", ip)
    log_login(new_user.id, ip)
    
    return new_user
    
def log_agreement(user_id: int, agreement_type: str, ip: str) -> None:
    """Log user agreement to the database."""
    try:
        new_log = AgreementLog(
            userID=user_id,
            type=agreement_type,
            ip=ip,
        )
        db.session.add(new_log)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise e
    
def get_latest_login(user_id: int) -> LoginLog:
    """Get the latest login log for a user."""
    login_query = select(LoginLog).where(LoginLog.userID == user_id).order_by(LoginLog.time.desc())
    return db.session.execute(login_query).scalars().first()

def get_latest_agreements(user_id: int) -> dict:
    """Get the latest terms_of_service and data_policy agreement logs for a user."""
    terms_query = select(AgreementLog).where(
        and_(AgreementLog.userID == user_id, AgreementLog.type == "terms_of_service")
    ).order_by(AgreementLog.time.desc()).limit(1)
    
    data_policy_query = select(AgreementLog).where(
        and_(AgreementLog.userID == user_id, AgreementLog.type == "data_policy")
    ).order_by(AgreementLog.time.desc()).limit(1)
    
    terms_log = db.session.execute(terms_query).scalars().first()
    data_policy_log = db.session.execute(data_policy_query).scalars().first()
    
    return {
        "terms_of_service": terms_log,
        "data_policy": data_policy_log
    }
    
def get_latest_report(user_id: int) -> ReportLog:
    """Get the latest report log for a user."""
    report_query = select(ReportLog).where(ReportLog.userID == user_id).order_by(ReportLog.generatedOn.desc())
    return db.session.execute(report_query).scalars().first()
    
def log_login(user_id: int, ip: str) -> None:
    """Log user login to the database."""
    try:
        new_log = LoginLog(
            userID=user_id,
            ip=ip,
        )
        db.session.add(new_log)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise e
    
def update_user(user_id: int, username: str , email: str, date_of_birth: str) -> User:
    """Update user details in the database."""
    user = getUserDetails(user_id)
    if not user:
        raise ValueError('User not found')

    existing_user = User.query.filter(and_(User.id != user_id, (User.username == username) | (User.email == email))).first()
    
    if existing_user:
        if existing_user.username == username:
            raise ValueError('Username is already taken')
        elif existing_user.email == email:
            raise ValueError('Email is already taken')

    try:
        if username:
            user.username = username
        if email:
            user.email = email
        if date_of_birth:
            user.date_of_birth = date_of_birth
            
        db.session.commit()
        return user
    except IntegrityError as e:
        db.session.rollback()
        raise e

def change_password(user_id: int, old_password: str, new_password: str) -> None:
    """Change the password for a user."""
    user = getUserDetails(user_id)
    if not user:
        raise ValueError('User not found')

    if not validate_password(user.password_hash, old_password):
        raise ValueError('Old password is incorrect')

    try:
        hashed_password = hash_password(new_password)
        user.password_hash = hashed_password.encode('utf-8')
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise e

def add_jwt_token(response: Response, userID: int, long_expire: bool) -> None:
    """
    Function for generating a JWT token.
    This function will create and return a JWT token for the authenticated user.
    """
    
    if not isinstance(userID, int):
        raise TypeError('userID must be an integer')
    if not isinstance(long_expire, bool):
        raise TypeError('long_expire must be a boolean')
    
    token_life = datetime.timedelta(days=30) if long_expire else datetime.timedelta(hours=1)
    
    payload = {
        'user_id': userID,
        'long_expire': long_expire,
        'exp': datetime.datetime.now(datetime.timezone.utc) + token_life
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    
    response.set_cookie(
        'authToken',
        token,
        httponly=True,
        secure=Config.ENV != "development",
        samesite='Strict',
        path='/',
        max_age=token_life.total_seconds(),
    )
    
def renew_jwt_token(response: Response, request: Request) -> None:
    """
    Function for renewing a JWT token.
    This function will create and return a JWT token for the authenticated user.
    """
    
    if not hasattr(request, 'tokenValidated') or not request.tokenValidated:
        raise jwt.InvalidTokenError()
    
    userID = request.user['id']
    long_expire = request.user['long_expire']
    
    if not isinstance(userID, int):
        raise TypeError('userID must be an integer')
    if not isinstance(long_expire, bool):
        raise TypeError('long_expire must be a boolean')
    
    token_life = datetime.timedelta(days=30) if long_expire else datetime.timedelta(hours=1)
    
    payload = {
        'user_id': userID,
        'long_expire': long_expire,
        'exp': datetime.datetime.now(datetime.timezone.utc) + token_life
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    
    response.set_cookie(
        'authToken',
        token,
        httponly=True,
        secure=Config.ENV != "development",
        samesite='Strict',
        path='/',
        max_age=token_life.total_seconds(),
    )
    
def clear_jwt_token(response: Response) -> None:
    """
    Function for clearing a JWT token.
    This function will create and return a JWT token for the authenticated user.
    """
    
    token = jwt.encode({}, Config.JWT_SECRET, algorithm='HS256')
    
    response.set_cookie(
        'authToken',
        token,
        httponly=True,
        secure=Config.ENV != "development",
        samesite='Strict',
        path='/',
        max_age=0,
    )

def validate_jwt_token(request: Request, token: str) -> None:
    secret_key = Config.JWT_SECRET
    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            
    # Attach user information to the request context
    request.user = { 'id': decoded_token['user_id'], 'long_expire': decoded_token['long_expire'] }
    request.tokenValidated = True