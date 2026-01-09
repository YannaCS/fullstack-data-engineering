# User Endpoints (CRD - No Update)
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.models import User
from app.dependency import DBSession
from app.schemas import UserCreate, UserResponse


router = APIRouter(prefix='/users')

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DBSession):
    db_user = User(
        name = user.name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get('/', response_model=list[UserResponse])
def get_users(db: DBSession):
    """List all users."""
    users = db.exec(select(User)).all()
    return users

@router.get('/{user_id}', response_model=UserResponse)
def get_user(user_id: int, db: DBSession):
    """Get a specific user by ID."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DBSession):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return None 

