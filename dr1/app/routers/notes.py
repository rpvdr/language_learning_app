from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import SessionLocal
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/words/{word_id}/notes", response_model=schemas.UserWordNoteResponse)
def create_word_note(
    word_id: int,
    note: schemas.UserWordNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_note = models.UserWordNote(
        user_id=current_user.id,
        word_id=word_id,
        note=note.note,
        flag=note.flag
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/words/{word_id}/notes", response_model=List[schemas.UserWordNoteResponse])
def get_word_notes(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.UserWordNote).filter(models.UserWordNote.word_id == word_id).all()

@router.delete("/words/{word_id}/notes/{note_id}")
def delete_word_note(
    word_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    note = db.query(models.UserWordNote).filter(models.UserWordNote.id == note_id, models.UserWordNote.word_id == word_id, models.UserWordNote.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"ok": True} 