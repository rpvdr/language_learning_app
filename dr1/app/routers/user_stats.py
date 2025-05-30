from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from .. import models, auth
from ..database import SessionLocal
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_stats_image(user, db):
    total_words = db.query(models.UserCardReview).filter_by(user_id=user.id, item_type='word').count()
    total_phrases = db.query(models.UserCardReview).filter_by(user_id=user.id, item_type='phrase').count()
    total_errors = db.query(models.UserAnswerError).filter_by(user_id=user.id).count()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Words', 'Phrases', 'Errors'], [total_words, total_phrases, total_errors])
    ax.set_title('Your Learning Stats')
    ax.set_ylabel('Count')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.read()

@router.get("/stats-image")
def get_stats_image(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    image_bytes = generate_stats_image(current_user, db)
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png", headers={"Content-Disposition": "inline; filename=stats.png"}) 