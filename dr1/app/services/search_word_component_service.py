from sqlalchemy.orm import Session
from .. import models

def search_word_components_service(query, type, word_id, limit, offset, db: Session):
    q = db.query(models.WordComponent)
    if query:
        q = q.filter(models.WordComponent.text.ilike(f"%{query}%"))
    if type:
        q = q.filter(models.WordComponent.type == type)
    if word_id:
        q = q.join(models.WordComponent.links).filter(models.WordComponentLink.word_id == word_id)
    total_count = q.count()
    components = q.order_by(models.WordComponent.id.asc()).offset(offset).limit(limit + 1).all()
    return components, total_count 