from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime

#Note entity
class Notebase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    
class NoteCreate(Notebase):
    pass

class NoteUpdate(Notebase):
    title: str | None
    content: str | None
    pass

class NoteResponse(Notebase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class config: #adapte to Pydantic
        from_attribute = True
        
class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
        
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @field_validator('password')
    def validate_password(cls, v:str):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must include one digit')
        return v
    
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class config: #adapte to Pydantic
        from_attribute = True

class Token(BaseModel):
    access_token: str