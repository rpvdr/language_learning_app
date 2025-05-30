from sqlalchemy.orm import Session, joinedload
from .. import models, schemas
import logging, os

def create_word_service(word: schemas.WordCreate, db: Session) -> models.Word:
    db_word = models.Word(
        text=word.text,
        reflexivity=word.reflexivity,
        case=word.case,
        part_of_speech=word.part_of_speech,
        categories=word.categories
    )
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

def get_words_service(db: Session):
    words = db.query(models.Word).options(
        joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
        joinedload(models.Word.components).joinedload(models.WordComponentLink.component).joinedload(models.WordComponent.meanings),
        joinedload(models.Word.part_of_speech_obj)
    ).all()
    return words

def get_word_service(word_id: int, db: Session):
    word = db.query(models.Word).options(
        joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
        joinedload(models.Word.components).joinedload(models.WordComponentLink.component).joinedload(models.WordComponent.meanings),
        joinedload(models.Word.part_of_speech_obj)
    ).filter(models.Word.id == word_id).first()
    if word:
        logging.warning(f"GET_WORD_SERVICE: meanings={[m.id for m in word.meanings]}")
        for m in word.meanings:
            logging.warning(f"  meaning {m.id} examples={[e.id for e in m.examples]}")
        logging.warning(f"DB URL: {os.environ.get('DATABASE_URL')}")
    return word

def update_word_service(word_id: int, word_update: schemas.WordUpdate, db: Session):
    db_word = db.query(models.Word).options(
        joinedload(models.Word.part_of_speech_obj)
    ).filter(models.Word.id == word_id).first()
    if not db_word:
        return None
    for key, value in word_update.dict(exclude_unset=True).items():
        setattr(db_word, key, value)
    db.commit()
    db.refresh(db_word)
    return db_word

def delete_word_service(word_id: int, db: Session):
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    if not word:
        return False
    db.query(models.PhraseComponent).filter(models.PhraseComponent.word_id == word_id).delete()
    db.query(models.SemanticGroupLink).filter(models.SemanticGroupLink.word_id == word_id).delete()
    db.delete(word)
    db.commit()
    return True

def add_word_component_service(word_id: int, component: schemas.WordComponentCreate, db: Session):
    db_component = db.query(models.WordComponent).filter(models.WordComponent.text == component.text, models.WordComponent.type == component.type).first()
    if not db_component:
        db_component = models.WordComponent(type=component.type, text=component.text)
        db.add(db_component)
        db.commit()
        db.refresh(db_component)
        for meaning in component.meanings:
            db_meaning = models.WordComponentMeaning(component_id=db_component.id, meaning=meaning)
            db.add(db_meaning)
        db.commit()
    else:
        existing_meanings = {m.meaning for m in db_component.meanings}
        for meaning in component.meanings:
            if meaning not in existing_meanings:
                db_meaning = models.WordComponentMeaning(component_id=db_component.id, meaning=meaning)
                db.add(db_meaning)
        db.commit()
    db_word_component_link = models.WordComponentLink(word_id=word_id, component_id=db_component.id, order=component.order)
    db.add(db_word_component_link)
    db.commit()
    word = db.query(models.Word).options(
        joinedload(models.Word.part_of_speech_obj)
    ).filter(models.Word.id == word_id).first()
    return word

def add_word_meaning_service(word_id: int, meaning: schemas.WordMeaningCreate, db: Session):
    db_meaning = models.WordMeaning(word_id=word_id, meaning=meaning.meaning)
    db.add(db_meaning)
    db.commit()
    db.refresh(db_meaning)
    return db_meaning

def add_word_example_service(word_id: int, example: schemas.WordMeaningExampleCreate, db: Session):
    db_example = models.WordMeaningExample(
        word_meaning_id=example.word_meaning_id,
        example_text=example.example_text,
        example_text_german=example.example_text_german
    )
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

def search_words_by_component_service(component_text: str, component_type: str, db: Session):
    component = db.query(models.WordComponent).filter(models.WordComponent.text == component_text, models.WordComponent.type == component_type).first()
    if not component:
        return []
    word_links = db.query(models.WordComponentLink).filter(models.WordComponentLink.component_id == component.id).all()
    word_ids = [link.word_id for link in word_links]
    words = db.query(models.Word).filter(models.Word.id.in_(word_ids)).all()
    return words

def search_words_by_text_service(query: str, db: Session):
    words = db.query(models.Word).filter(models.Word.text.ilike(f"%{query}%")).all()
    return words 