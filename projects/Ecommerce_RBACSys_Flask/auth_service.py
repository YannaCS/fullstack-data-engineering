from flask import Blueprint, jsonify, request
from models import *
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import jwt
from config import SECRET_JWT_KEY
from werkzeug.security import generate_password_hash, check_password_hash
from auth_decorator import role_required, token_required
from db import db

auth_bp = Blueprint('authentication', __name__, url_prefix='/api')

def create_token(user: User):

    permission_names = [perm.name for perm in user.role.permissions]
    payload = {
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        'role_name': user.role.name,
        'permissions': permission_names,  # Include all permissions
        'exp': datetime.now() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.now()  # Issued at
    }

    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm='HS256')
    return token


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Public (no authentication required)
    Request: email, password
    """
    try:
        data = request.get_json()

        if not data:
            return {'error': 'No data provided'}, 400
        
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email and password are required'}, 400
        
        # find user by email
        user = db.session.query(User).filter_by(email=email).first()

        if not user:
            return {'error': 'No user found'}, 401
        
        if not check_password_hash(user.password.password_hash, password):
            return {'error': 'Invalid credentials'}, 401
        
        token = create_token(user)

        permission_names = [perm.name for perm in user.role.permissions]
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role.name,
                'permissions': permission_names
            }
        }), 200
    
    except Exception:
        return {'error': str(Exception)}, 500


                       
@auth_bp.route('/register', methods=['POST'])
@token_required
@role_required('Admin')
def register():
    """
    manage_users (admin only!)
    Request: email, password
    """
    try:
        data = request.get_json()

        if not data:
            return {'error': 'No data provided'}, 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role_name = data.get('role_name')

        if not all([username, email, password, role_name]):
            return {'error': 'username, email, password, and role_name are required'}, 400
        
        # Check if user already exists
        existing_user = db.session.query(User).filter_by(email=email).first()
        if existing_user:
            return {'error': 'User with this email already exists'}, 400
        
        # Validate role exists
        role = db.session.query(Role).filter_by(name=role_name).first()
        if not role:
            return {'error': f'Role "{role_name}" not found. Valid roles: Admin, Sales, Viewer'}, 400
        
        # Validate password
        if len(password) < 8:
            return {'error': 'Password must be at least 8 characters long'}, 400
        
        # Create new user
        new_user = User(
            username = username,
            email = email,
            role = role
        )
        user_password = Password(
            user = new_user,
            password_hash = generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.add(user_password)
        db.session.commit()

        return {'message': 'register successfully'}, 201
    except Exception:
        db.session.rollback()
        return {'error': str(Exception)}, 500
    
@auth_bp.route('/profile')  # default method get
@token_required  
def profile():
    payload = request.current_user
    return {
        'email': payload['email'],
        'name': payload['user_name'],
        'role': payload['user_role'],
    }