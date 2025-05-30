from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import SessionLocal
from datetime import datetime
from app.services.studyset_service import genetic_algorithm

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/studyset/generate", response_model=schemas.UserStudySetResponse)
def generate_study_set(
    req: schemas.StudySetGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    user = None
    if req.user_id is not None:
        user = db.query(models.User).filter(models.User.id == req.user_id).first()
    elif req.email is not None:
        user = db.query(models.User).filter(models.User.email == req.email).first()
    else:
        user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.profile is None:
        raise HTTPException(status_code=400, detail="User profile is not set. Please fill in your profile before generating a study set.")
    if req.root:
        words_with_root = db.query(models.Word).join(
            models.WordComponentLink
        ).join(
            models.WordComponent
        ).filter(
            models.WordComponent.type == 'root',
            models.WordComponent.text.ilike(f"%{req.root}%")
        ).all()
        if not words_with_root:
            raise HTTPException(status_code=404, detail=f"No words found with root '{req.root}'")
        word_ids = [w.id for w in words_with_root]
        phrase_ids = set()
        for word in words_with_root:
            phrases = db.query(models.Phrase).join(
                models.PhraseComponent
            ).filter(
                models.PhraseComponent.word_id == word.id
            ).all()
            phrase_ids.update(p.id for p in phrases)
        group_ids = set()
        for word in words_with_root:
            groups = db.query(models.SemanticGroup).join(
                models.SemanticGroupLink
            ).filter(
                models.SemanticGroupLink.word_id == word.id
            ).all()
            group_ids.update(g.id for g in groups)
        special_study_set = models.SpecialUserStudySet(
            user_id=user.id,
            word_ids=word_ids,
            phrase_ids=list(phrase_ids),
            semantic_group_ids=list(group_ids),
            root=req.root,
            created_at=datetime.utcnow()
        )
        db.add(special_study_set)
        db.commit()
        db.refresh(special_study_set)
        return {
            "id": special_study_set.id,
            "user_id": special_study_set.user_id,
            "word_ids": word_ids,
            "phrase_ids": list(phrase_ids),
            "semantic_group_ids": list(group_ids),
            "root": req.root,
            "created_at": special_study_set.created_at
        }
    else:
        word_ids, phrase_ids, group_ids = genetic_algorithm(user, db)
        study_set = models.UserStudySet(
            user_id=user.id,
            word_ids=word_ids,
            phrase_ids=phrase_ids,
            semantic_group_ids=group_ids if group_ids is not None else [],
            created_at=datetime.utcnow()
        )
    db.add(study_set)
    db.commit()
    db.refresh(study_set)
    return {
        "id": study_set.id,
        "user_id": study_set.user_id,
        "word_ids": word_ids,
        "phrase_ids": list(phrase_ids) if req.root else phrase_ids,
        "semantic_group_ids": list(group_ids) if req.root else (group_ids if group_ids is not None else []),
        "created_at": study_set.created_at
    }

@router.get("/studyset/latest", response_model=schemas.UserStudySetResponse)
def get_latest_study_set(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    study_set = db.query(models.UserStudySet).filter(models.UserStudySet.user_id == current_user.id).order_by(models.UserStudySet.created_at.desc()).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="No study set found")
    return study_set

@router.get("/special-studyset/latest", response_model=schemas.UserStudySetResponse)
def get_latest_special_study_set(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    study_set = db.query(models.SpecialUserStudySet).filter(models.SpecialUserStudySet.user_id == current_user.id).order_by(models.SpecialUserStudySet.created_at.desc()).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="No special study set found")
    return study_set 