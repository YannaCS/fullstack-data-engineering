from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
from typing import Annotated

DBSession = Annotated[Session, Depends(get_session)]