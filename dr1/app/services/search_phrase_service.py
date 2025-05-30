from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from .. import models

def search_phrases_service(query, category, level, label, word_id, semantic_group_id, limit, offset, db: Session):
    q = db.query(models.Phrase).options(
        joinedload(models.Phrase.meanings).joinedload(models.PhraseMeaning.examples),
        joinedload(models.Phrase.components).joinedload(models.PhraseComponent.word).joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
        joinedload(models.Phrase.labels).joinedload(models.PhraseLabelLink.label),
        joinedload(models.Phrase.semantic_links)
    )
    if query:
        q = q.join(models.Phrase.components).join(models.PhraseComponent.word)
        q = q.outerjoin(models.Phrase.meanings)
        q = q.filter(
            or_(
                models.PhraseMeaning.meaning.ilike(f"%{query}%"),
                models.Word.text.ilike(f"%{query}%")
            )
        )
    if category:
        q = q.filter(models.Phrase.categories != None)
        q = q.filter(models.Phrase.categories.any(category))
    if level:
        q = q.filter(models.Phrase.level == level)
    if label:
        q = q.join(models.Phrase.labels).join(models.PhraseLabelLink.label).filter(models.PhraseLabel.name.ilike(f"%{label}%"))
    if word_id:
        q = q.join(models.Phrase.components).filter(models.PhraseComponent.word_id == word_id)
    if semantic_group_id:
        q = q.join(models.Phrase.semantic_links).filter(models.SemanticGroupLink.group_id == semantic_group_id)
    total_count = q.count()
    phrases = q.order_by(models.Phrase.id.asc()).offset(offset).limit(limit + 1).all()
    return phrases, total_count 