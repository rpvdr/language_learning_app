from sqlalchemy.orm import Session
from .. import models

def search_semantic_groups_service(query, category, level, word_id, phrase_id, limit, offset, db: Session):
    q = db.query(models.SemanticGroup)
    if query:
        q = q.filter(models.SemanticGroup.name.ilike(f"%{query}%"))
    if category:
        q = q.filter(models.SemanticGroup.categories != None)
        q = q.filter(models.SemanticGroup.categories.any(category))
    if level:
        q = q.filter(models.SemanticGroup.level == level)
    if word_id:
        q = q.join(models.SemanticGroup.links).filter(models.SemanticGroupLink.word_id == word_id)
    if phrase_id:
        q = q.join(models.SemanticGroup.links).filter(models.SemanticGroupLink.phrase_id == phrase_id)
    total_count = q.count()
    groups = q.order_by(models.SemanticGroup.id.asc()).offset(offset).limit(limit + 1).all()
    return groups, total_count 