from sqlalchemy.orm import Session, joinedload
from .. import models

def search_words_service(query, category, level, part_of_speech, component_text, semantic_group_id, limit, offset, db: Session):
    q = db.query(models.Word).options(
        joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
        joinedload(models.Word.components).joinedload(models.WordComponentLink.component).joinedload(models.WordComponent.meanings),
        joinedload(models.Word.part_of_speech_obj)
    )
    if query:
        q = q.filter(models.Word.text.ilike(f"%{query}%"))
    if category:
        q = q.filter(models.Word.categories != None)
        q = q.filter(models.Word.categories.any(category))
    if level:
        q = q.filter(models.Word.level == level)
    if part_of_speech:
        q = q.filter(models.Word.part_of_speech == part_of_speech)
    if component_text:
        q = q.join(models.Word.components).join(models.WordComponentLink.component).filter(models.WordComponent.text.ilike(f"%{component_text}%"))
    if semantic_group_id:
        q = q.join(models.Word.semantic_links).filter(models.SemanticGroupLink.group_id == semantic_group_id)
    total_count = q.count()
    words = q.order_by(models.Word.text.asc(), models.Word.id.asc()).offset(offset).limit(limit + 1).all()
    return words, total_count 