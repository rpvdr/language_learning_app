from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import SessionLocal

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
            "region": current_user.profile.region,
            "learning_speed": current_user.profile.learning_speed,
            "entry_test_result": current_user.profile.entry_test_result,
            "daily_minutes": current_user.profile.daily_minutes,
            "desired_level": current_user.profile.desired_level,
            "current_level": current_user.profile.current_level,
        }
    return schemas.UserResponse(
        email=current_user.email,
        roles=[role.role.name for role in current_user.roles],
        profile=profile_dict
    ) 