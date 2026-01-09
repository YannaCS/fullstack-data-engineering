from typing import Optional
from pydantic import BaseModel, Field

# user schema
class UserBase(BaseModel):
    name: str = Field(..., min_length=1)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    name: str
    class Config:
        from_attributes = True

# task schema
class TaskBase(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    user_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3)
    content: Optional[str] = Field(None, min_length=1)
    city: Optional[str] = Field(None, min_length=1)
    user_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True

# weather Schemas
class WeatherData(BaseModel):
    temperature: float
    windspeed: float
    weathercode: int
    time: str

class TaskWithWeather(TaskResponse):
    weather: WeatherData