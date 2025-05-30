

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from .. import models, schemas

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