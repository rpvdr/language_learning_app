from fastapi import APIRouter, Depends, HTTPException
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

@router.put("/me/profile", response_model=schemas.UserResponse)
def update_profile(profile: schemas.ProfileUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not db_profile:
        db_profile = models.Profile(user_id=current_user.id)
        db.add(db_profile)
    for key, value in profile.dict(exclude_unset=True).items():
        setattr(db_profile, key, value)
    db.commit()
    db.refresh(db_profile)
    word_ids, phrase_ids, group_ids = genetic_algorithm(current_user, db)
    study_set = models.UserStudySet(
        user_id=current_user.id,
        word_ids=word_ids,
        phrase_ids=phrase_ids,
        semantic_group_ids=group_ids if group_ids is not None else [],
        created_at=datetime.utcnow()
    )
    db.add(study_set)
    db.commit()
    db.refresh(study_set)
    profile_dict = {
        "is_public": db_profile.is_public,
        "target_level": db_profile.target_level,
        "categories": db_profile.categories,
        "region": db_profile.region,
        "learning_speed": db_profile.learning_speed,
        "entry_test_result": db_profile.entry_test_result,
        "daily_minutes": db_profile.daily_minutes,
        "desired_level": db_profile.desired_level,
        "current_level": db_profile.current_level,
    }
    return schemas.UserResponse(
        email=current_user.email,
        roles=[role.role.name for role in current_user.roles],
        profile=profile_dict
    ) 