from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Password hashing
pwd_hash = PasswordHash.recommended()

# JWT settings
SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    """Create JWT access token"""
    to_encode = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    print('to_encode', to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[int]:
    """Decode JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print('payload', payload)
        user_id: str = payload.get("user_id")
        if user_id is None:
            return None
        return int(user_id)
    except Exception as e:
        print('error', e)
        return None