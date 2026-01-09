#User
#id, email, username, password_hash

# Note
#id, title, content, user_id, tags

# Tag
#id, value
from sqlmodel import SQLModel, Field, Relationship, Session
# sqlmodel = sqlalchemy + pydantic
# can use sqlalchemy
# but sqlmodel is better for fastapi
from datetime import datetime
from app.database import engine

class User(SQLModel, table=True):
    __tablename__ = 'users' #type: ignore
    
    id: int | None = Field(default=None, primary_key=True)
    # when creating the class instance, but not input into db
    # there is no id value for the instance
    # so it could be none
    email: str = Field(unique=True, max_length=255, index=True)
    # the email column will be indexed and also must be unique
    username: str = Field(max_length=50)
    hash_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    
    notes: list['Note'] = Relationship(back_populates='user')
    
class Note(SQLModel, table=True):
    
    __tablename__ = 'notes' #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=50)
    content: str
    user_id: int = Field(foreign_key='users.id', index=True)
    # created_at: datetime = Field(default=datetime.now())
    # updated_at: datetime = Field(default=datetime.now())
    # that calls datetime.now() once, at the time when the class is defined (import time), and uses that single datetime object as the default for all instances
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # User 1-to-many Note
    user: User = Relationship(back_populates='notes')
    




