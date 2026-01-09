from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.schemas import UserCreate, UserResponse, Token
from app.models import User
from app.security_utils import hash_password, verify_password, create_access_token

from app.dependency import DBSession

router = APIRouter(prefix='/auth')

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: DBSession):
    stmt = select(User).where(User.email == user.email)
    existing_user = db.exec(stmt).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered"
        )
    
    db_user = User(
        email=user.email,
        username=user.username,
        hash_password=hash_password(user.password)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # refresh to get the auto generated id or anything updated in database
    
    return db_user

@router.post('/login', response_model=Token, status_code=status.HTTP_200_OK)
def login(db: DBSession, form_data: OAuth2PasswordRequestForm = Depends() ):
    print(form_data.username)
    print(form_data.password)
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    
    if not verify_password(form_data.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="incorrect password"
        )
    
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    
    access_token = create_access_token(user.id)
    
    return {'access_token': access_token}
    