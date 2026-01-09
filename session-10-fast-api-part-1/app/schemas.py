from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Note entity
# ... means required
class Notebase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    # title: str | None = Field(None, min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    
class NoteCreate(Notebase):
    pass

"""
if let NoteUpdate inheriting from Notebase,
which has title: str (required), 
and you're trying to override it with title: Optional[str] (optional)
this creates a type conflict.
"""
class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    pass

class NoteResponse(Notebase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class config: #adapt to Pydantic
        from_attribute = True