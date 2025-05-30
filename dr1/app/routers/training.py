from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import SessionLocal
from datetime import datetime, timezone, timedelta
from fsrs import Scheduler, Card, Rating, ReviewLog
import json
from typing import Optional, List
from app.utils.gemini import analyze_error_with_gemini
from app.services.training_service import start_training_service, submit_answer_service, rate_answer_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/training/start")
def start_training(
    count: int = Query(...),
    is_review: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return start_training_service(count, is_review, db, current_user)

@router.post("/special-training/start")
def special_training_start(
    count: int = Query(...),
    is_review: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return start_training_service(count, is_review, db, current_user)

@router.post("/training/submit_answer", response_model=schemas.TrainingAnswerResponse)
async def submit_answer(
    data: schemas.TrainingAnswerRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = await submit_answer_service(data, db, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found or no text found for this item")
    return result

@router.post("/training/rate_answer", response_model=schemas.UserCardReviewResponse)
def rate_answer(
    data: schemas.TrainingRateAnswerRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = rate_answer_service(data, db, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="No answer submitted for this card or invalid rating")
    return result

@router.get("/training/error_stats", response_model=dict)
def get_error_stats(
    error_type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    is_admin = any(role.role.name == "admin" for role in current_user.roles)
    if user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view other users' stats")
    target_user_id = user_id if user_id else current_user.id
    query = db.query(models.UserAnswerError).filter(models.UserAnswerError.user_id == target_user_id)
    if error_type:
        query = query.filter(models.UserAnswerError.error_analysis == error_type)
    errors = query.all()
    error_types = {}
    for error in errors:
        error_types[error.error_analysis] = error_types.get(error.error_analysis, 0) + 1
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    three_months_ago = now - timedelta(days=90)
    year_ago = now - timedelta(days=365)
    reviews_query = db.query(models.UserCardReview).filter(
        models.UserCardReview.user_id == target_user_id,
        models.UserCardReview.is_review == True
    )
    monthly_reviews = reviews_query.filter(models.UserCardReview.created_at >= month_ago).count()
    three_monthly_reviews = reviews_query.filter(models.UserCardReview.created_at >= three_months_ago).count()
    yearly_reviews = reviews_query.filter(models.UserCardReview.created_at >= year_ago).count()
    return {
        "error_statistics": {
            "total_errors": len(errors),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        },
        "review_statistics": {
            "last_month": monthly_reviews,
            "last_three_months": three_monthly_reviews,
            "last_year": yearly_reviews
        }
    }

@router.get("/training/errors", response_model=List[schemas.UserAnswerError])
def get_user_errors(
    error_type: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    is_admin = any(role.role.name == "admin" for role in current_user.roles)
    if user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view other users' errors")
    target_user_id = user_id if user_id else current_user.id
    query = db.query(models.UserAnswerError).filter(models.UserAnswerError.user_id == target_user_id)
    if error_type:
        query = query.filter(models.UserAnswerError.error_analysis == error_type)
    return query.offset(skip).limit(limit).all()

@router.get("/training/confidence_stats", response_model=dict)
def get_confidence_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    is_admin = any(role.role.name == "admin" for role in current_user.roles)
    if user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view other users' stats")
    target_user_id = user_id if user_id else current_user.id
    errors_with_ratings = db.query(
        models.UserAnswerError,
        models.UserCardReview.last_rating
    ).join(
        models.UserCardReview,
        (models.UserAnswerError.user_id == models.UserCardReview.user_id) &
        (models.UserAnswerError.item_type == models.UserCardReview.item_type) &
        (models.UserAnswerError.item_id == models.UserCardReview.item_id)
    ).filter(
        models.UserAnswerError.user_id == target_user_id
    ).all()
    stats = {
        "by_error_type": {},
        "by_rating": {
            "1": {"count": 0, "error_types": {}},
            "2": {"count": 0, "error_types": {}},
            "3": {"count": 0, "error_types": {}},
            "4": {"count": 0, "error_types": {}}
        },
        "confidence_correlation": {
            "high_confidence_errors": 0,
            "low_confidence_errors": 0,
            "high_confidence_correct": 0,
            "low_confidence_correct": 0
        }
    }
    for error, rating in errors_with_ratings:
        if error.error_analysis not in stats["by_error_type"]:
            stats["by_error_type"][error.error_analysis] = {
                "total": 0,
                "by_rating": {"1": 0, "2": 0, "3": 0, "4": 0}
            }
        stats["by_error_type"][error.error_analysis]["total"] += 1
        if rating:
            stats["by_error_type"][error.error_analysis]["by_rating"][str(rating)] += 1
            stats["by_rating"][str(rating)]["count"] += 1
            if error.error_analysis not in stats["by_rating"][str(rating)]["error_types"]:
                stats["by_rating"][str(rating)]["error_types"][error.error_analysis] = 0
            stats["by_rating"][str(rating)]["error_types"][error.error_analysis] += 1
            if rating >= 3:
                stats["confidence_correlation"]["high_confidence_errors"] += 1
            else:
                stats["confidence_correlation"]["low_confidence_errors"] += 1
    correct_answers = db.query(models.UserCardReview).filter(
        models.UserCardReview.user_id == target_user_id,
        models.UserCardReview.last_result == True
    ).all()
    for review in correct_answers:
        if review.last_rating:
            if review.last_rating >= 3:
                stats["confidence_correlation"]["high_confidence_correct"] += 1
            else:
                stats["confidence_correlation"]["low_confidence_correct"] += 1
    for error_type in stats["by_error_type"]:
        stats["by_error_type"][error_type]["by_rating"] = dict(
            sorted(stats["by_error_type"][error_type]["by_rating"].items(),
                  key=lambda x: int(x[0]))
        )
    stats["by_error_type"] = dict(
        sorted(stats["by_error_type"].items(),
               key=lambda x: x[1]["total"],
               reverse=True)
    )
    return stats

@router.get("/training/error_stats/all", response_model=dict)
def get_error_stats_all(
    error_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    is_admin = any(role.role.name == "admin" for role in current_user.roles)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view all users' stats")
    query = db.query(models.UserAnswerError)
    if error_type:
        query = query.filter(models.UserAnswerError.error_analysis == error_type)
    errors = query.all()
    error_types = {}
    for error in errors:
        error_types[error.error_analysis] = error_types.get(error.error_analysis, 0) + 1
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    three_months_ago = now - timedelta(days=90)
    year_ago = now - timedelta(days=365)
    reviews_query = db.query(models.UserCardReview).filter(models.UserCardReview.is_review == True)
    monthly_reviews = reviews_query.filter(models.UserCardReview.created_at >= month_ago).count()
    three_monthly_reviews = reviews_query.filter(models.UserCardReview.created_at >= three_months_ago).count()
    yearly_reviews = reviews_query.filter(models.UserCardReview.created_at >= year_ago).count()
    return {
        "error_statistics": {
            "total_errors": len(errors),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        },
        "review_statistics": {
            "last_month": monthly_reviews,
            "last_three_months": three_monthly_reviews,
            "last_year": yearly_reviews
        }
    }

@router.get("/training/errors/all", response_model=List[schemas.UserAnswerError])
def get_all_errors(
    error_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    is_admin = any(role.role.name == "admin" for role in current_user.roles)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view all users' errors")
    query = db.query(models.UserAnswerError)
    if error_type:
        query = query.filter(models.UserAnswerError.error_analysis == error_type)
    return query.offset(skip).limit(limit).all() 