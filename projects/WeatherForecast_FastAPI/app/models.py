from sqlmodel import SQLModel, Field, Relationship,Session
from app.database import engine

class User(SQLModel, table=True):
    __tablename__ = 'users' # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(...)

    tasks: list['Task'] = Relationship(back_populates='user')

class Task(SQLModel, table=True):
    __tablename__ = 'tasks' # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=3)
    content: str = Field(...)
    city: str = Field(...)
    user_id: int = Field(foreign_key='users.id', index=True)

    user: User = Relationship(back_populates='tasks')