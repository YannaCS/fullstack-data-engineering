from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.schemas import NoteCreate, NoteResponse, NoteUpdate
from app.models import Note
from app.database import get_session
from datetime import datetime
from app.ai_client import ai_client
 
from app.dependency import DBSession, CurrentUser, AsyncDBSession, AsyncCurrentUser

router = APIRouter(prefix='/notes')

@router.post('/', response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
# dependency injection
def create_note(
    note: NoteCreate,
    # db: Session = Depends(get_session)
    # db: Annotated[Session, Depends(get_session)]
    db: DBSession,
    current_user: CurrentUser
):
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    user_id = current_user.id
    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=user_id
    )
    
    db.add(db_note)
    db.commit()
    return db_note


# @router.get("/", response_model=list[NoteResponse])
# def list_notes(db: DBSession, current_user: CurrentUser, limit: int = 10, offset: int = 0):
#     """List all notes"""
#     statement = select(Note).where(Note.user_id == current_user.id).offset(offset).limit(limit)
#     notes = db.exec(statement).all()
#     return notes

@router.get("/", response_model=list[NoteResponse])
async def list_notes(db: AsyncDBSession, current_user: AsyncCurrentUser, limit: int = 10, offset: int = 0):
    """List all notes"""
    statement = select(Note).where(Note.user_id == current_user.id).offset(offset).limit(limit)
    notes = (await db.execute(statement)).scalars().all()
    return notes

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: DBSession):
    """Get a specific note"""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return note

@router.get('/summarize/{note_id}')
async def summarize_note(note_id: int, db: DBSession):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )

    result = await ai_client.summarize_content(note.content)
    return {'content': result}

@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_update: NoteUpdate, db: DBSession):
    """Update a note"""
    db_note = db.get(Note, note_id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    
    # Update fields
    update_data = note_update.model_dump(exclude_unset=True)
    
    # Update fields
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    db_note.updated_at = datetime.now()
    db.add(db_note)
    db.commit()
    
    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: DBSession):
    """Delete a note"""
    db_note = db.get(Note, note_id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    
    db.delete(db_note)
    db.commit()
    return None