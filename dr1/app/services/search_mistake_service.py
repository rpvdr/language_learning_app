from sqlalchemy.orm import Session
from .. import models

def search_mistakes_service(query, category, level, error_type, user_id, item_type, limit, offset, db: Session):
    q = db.query(models.UserAnswerError)
    if query:
        q = q.filter(models.UserAnswerError.user_answer.ilike(f"%{query}%"))
    if error_type:
        q = q.filter(models.UserAnswerError.error_analysis == error_type)
    if user_id:
        q = q.filter(models.UserAnswerError.user_id == user_id)
    if item_type:
        q = q.filter(models.UserAnswerError.item_type == item_type)
    total_count = q.count()
    mistakes = q.order_by(models.UserAnswerError.id.asc()).offset(offset).limit(limit + 1).all()
    return mistakes, total_count 