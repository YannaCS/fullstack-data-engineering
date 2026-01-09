from create_app import create_app
from flask import make_response, request, session
import random
import json
from sqlalchemy import select
from user_models import User, Password
from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from config import SECRET_JWT_KEY
from auth_decorator import token_required, role_required

app = create_app()

# Creating JWT Token
def create_token(email, user_role, user_name, user_id):
    payload = {
        'email': email,
        'user_role': user_role,
        'user_name': user_id,
        'user_id': user_id,
        'exp': datetime.now() + timedelta(hours=24),  # gonna expire in 24 hrs
        'iat': datetime.now()       # issured at: when does this token issured
    }
    
    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm='HS256')
    return token

@app.route('/')
def home():
    return 'JWT Server'

# Registration Endpoint
@app.route('/register', methods=['POST'])
def register():
    user_data = request.get_json()
    
    email = user_data.get('email')
    password = user_data.get('password')
    username = user_data.get('username')
    role = user_data.get('role')
    
    print(email, password, username, role)

    # Check if user already exists
    stmt = select(User).where(User.email == email)
    existing_user = db.session.scalar(stmt)
    if existing_user:
        return {"error": 'already registered'}, 400
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        role=role
    )
    # Hash password
    user_password = Password(
        user=new_user,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(new_user)
    db.session.add(user_password)
    db.session.commit()

    return {'message': 'register successfully'}, 201

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    
    email = user_data.get('email')
    password = user_data.get('password')
    print(email, password)
    
    # Find user in database
    stmt = select(User).where(User.email == email)
    user = db.session.scalar(stmt)
    print('user', user)
    
    # Verify password
    if not user or not user.password or not check_password_hash(user.password.password_hash, password):
        return {"error": 'invalid creditial'}, 401
    
    # Create JWT token
    token = create_token(email, user.role, user.username, user.id)
    
    print(token)
    
    return {
        'message': 'login success',
        'token': token,
        'user': {
            'email': email,
            'role': user.role
        }
    }
    
    
@app.route('/profile')  
@token_required  
def profile():
    payload = request.current_user
    return {
        'email': payload['email'],
        'name': payload['user_name'],
        'role': payload['user_role'],
    }
  

@app.route('/admin-dashboard')   
@role_required('admin')
def admin_dashboard():
    payload = request.current_user
    return {
        'message': 'admin only data',
        'admin': payload['email']
    }
    
@app.route('/moderator-dashboard')   
@role_required('admin', 'moderator')
def moderator_dashboard():
    payload = request.current_user
    return {
        'message': 'moderator data',
        'admin': payload['email']
    }
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)
    

