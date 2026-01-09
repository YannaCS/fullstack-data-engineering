from create_app import create_app
from flask import request
from sqlalchemy import select
from user_models import User, Password
from db import db
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

# Registration Endpoint
# register is like creating a new user, so use POST
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
    # Add to database
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
    
    return 'login'
    
    
    
 
if __name__ == '__main__':
    app.run(debug=True)
    

