from fastapi import APIRouter, Depends, HTTPException, status
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


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    
    for role_name in user.roles:
        role = db.query(models.Role).filter(models.Role.name == role_name).first()
        if role:
            user_role = models.UserRole(user_id=db_user.id, role_id=role.id)
            db.add(user_role)
    db.commit()

    return schemas.UserResponse(email=db_user.email, roles=user.roles, profile=None)


@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    
    access_token = auth.create_access_token(data={"sub": db_user.email})
    
    roles = [role.role.name for role in db_user.roles]
    return {"access_token": access_token, "token_type": "bearer", "roles": roles}


@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    profile_dict = None
    if current_user.profile:
        profile_dict = {
            "is_public": current_user.profile.is_public,
            "target_level": current_user.profile.target_level,
            "categories": current_user.profile.categories,
            "category_names": [c.name for c in db.query(models.Category).filter(models.Category.id.in_(current_user.profile.categories or [])).all()] if current_user.profile.categories else [],
            "region": current_user.profile.region,
            "learning_speed": current_user.profile.learning_speed,
            "entry_test_result": current_user.profile.entry_test_result,
        }

    return schemas.UserResponse(email=current_user.email, roles=[role.role.name for role in current_user.roles], profile=profile_dict)


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

    profile_dict = {
        "is_public": db_profile.is_public,
        "target_level": db_profile.target_level,
        "categories": db_profile.categories,
        "category_names": [c.name for c in db.query(models.Category).filter(models.Category.id.in_(db_profile.categories or [])).all()] if db_profile.categories else [],
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


@router.post("/categories", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories", response_model=List[schemas.CategoryResponse])
def read_categories(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Category).all()
