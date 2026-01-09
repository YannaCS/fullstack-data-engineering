from create_app import create_app
from flask import make_response, request, session
import random
import json

app = create_app()

app.secret_key = 'my-secret-key'  # Required for session encryption

# 'session_id=123456' + 'sjdfljself'
# ->base64 encode
# 'sefjilsdjflsdjljlxcv'

@app.route('/set-cookie')
def set_cookie():
    response = make_response('Cookie set')
    response.set_cookie('user_id', '123', max_age=3600)
    return response

@app.route('/get-cookie')
def get_cookie():
    cookie_value = request.cookies.get('user_id')
    return f"cookie value: {cookie_value}"

# assume there is a user
mock_users = [
    {"id": 1, "username": "alice", "email": "alice@example.com"},
    {"id": 2, "username": "Bob", "email": "bob@example.com"},
]

mock_redis_session_store = {
    # will store: '123455': {user_id: 1, session_id: 123455}
}


@app.route('/login-session')
def login_session():
    user = mock_users[0]
    session_id = random.randint(100000, 999999)

    # Store session data on server
    mock_redis_session_store[session_id] = {"user_id": user['id'], "session_id": session_id}
    
    # Store only session_id in encrypted cookie
    session['session_id'] = session_id
    print(json.dumps(mock_redis_session_store, indent=4))
    return 'Logged in'

@app.route('/profile-session')
def profile_session():
    session_id = session.get('session_id')
    if not session_id:
        return 'not logged in', 401
    
    # Look up session data on server
    session_data = mock_redis_session_store.get(session_id)
    if not session_data:
         return 'not logged in', 401

    user_id = session_data['user_id']
    return f"Session Id: {session_id} user_id: {user_id}"

@app.route('/logout-session')
def logout_session():
    session_id = session['session_id']
    if session_id:
        # Delete session from server store
        mock_redis_session_store.pop(session_id)
    
    # Clear session cookie
    session.pop(session_id, None)
    print(json.dumps(mock_redis_session_store, indent=4))
    return 'logged out'

if __name__ == '__main__':
    app.run(debug=True)