from pydantic import BaseModel, Field
# from datetime import datetime

# Note entity
# ... means required
class Notebase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    # title: str | None = Field(None, min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    
# class NoteCreate(Notebase):
#     pass

# class NoteUpdate(Notebase):
#     title: str | None
#     content: str | None
#     pass

# class NoteResponse(Notebase):
#     id: int
#     user_id: int
#     created_at: datetime
#     udpated_at: datetime
    
#     class config: #adapte to Pydantic
#         from_attribute = True