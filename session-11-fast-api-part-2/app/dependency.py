from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.database import get_session
from app.database_async import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.security_utils import decode_access_token
from app.models import User


DBSession = Annotated[Session, Depends(get_session)]
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_session)]

password_oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(db: DBSession, token: str = Depends(password_oauth_scheme)):
    user_id = decode_access_token(token)
    print('user_id', user_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return user

async def get_current_user_async(db: AsyncDBSession, token: str = Depends(password_oauth_scheme)):
    user_id = decode_access_token(token)
    print('user_id', user_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
AsyncCurrentUser = Annotated[User, Depends(get_current_user_async)]