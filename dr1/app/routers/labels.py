from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import SessionLocal
from app.services.label_service import *

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/labels", response_model=schemas.PhraseLabelResponse)
def create_label(label: schemas.PhraseLabelCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    return create_label_service(label, db)

@router.get("/labels", response_model=List[schemas.PhraseLabelResponse])
def read_labels(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_labels_service(skip, limit, db)

@router.get("/labels/by-phrase/{phrase_id}", response_model=List[schemas.PhraseLabelResponse])
def get_labels_by_phrase(phrase_id: int, db: Session = Depends(get_db)):
    links = db.query(models.PhraseLabelLink).filter(models.PhraseLabelLink.phrase_id == phrase_id).all()
    label_ids = [link.label_id for link in links]
    if not label_ids:
        return []
    labels = db.query(models.PhraseLabel).filter(models.PhraseLabel.id.in_(label_ids)).all()
    return [schemas.PhraseLabelResponse(id=l.id, name=l.name) for l in labels]
