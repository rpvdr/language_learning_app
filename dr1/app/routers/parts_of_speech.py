from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/parts-of-speech", response_model=schemas.PartOfSpeechResponse)
def create_part_of_speech(part_of_speech: schemas.PartOfSpeechCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    db_part_of_speech = models.PartOfSpeech(name=part_of_speech.name)
    db.add(db_part_of_speech)
    db.commit()
    db.refresh(db_part_of_speech)
    return db_part_of_speech

@router.get("/parts-of-speech", response_model=List[schemas.PartOfSpeechResponse])
def read_parts_of_speech(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.PartOfSpeech).all()

@router.get("/parts-of-speech/{part_of_speech_id}", response_model=schemas.PartOfSpeechResponse)
def read_part_of_speech(part_of_speech_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    part_of_speech = db.query(models.PartOfSpeech).filter(models.PartOfSpeech.id == part_of_speech_id).first()
    if not part_of_speech:
        raise HTTPException(status_code=404, detail="Part of speech not found")
    return part_of_speech

@router.delete("/parts-of-speech/{part_of_speech_id}", status_code=204)
def delete_part_of_speech(part_of_speech_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    part_of_speech = db.query(models.PartOfSpeech).filter(models.PartOfSpeech.id == part_of_speech_id).first()
    if not part_of_speech:
        raise HTTPException(status_code=404, detail="Part of speech not found")
    db.delete(part_of_speech)
    db.commit()
    return 