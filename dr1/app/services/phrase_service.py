from sqlalchemy.orm import Session, joinedload
from .. import models, schemas

def create_phrase_service(phrase: schemas.PhraseCreate, db: Session):
    db_phrase = models.Phrase()
    db.add(db_phrase)
    db.commit()
    db.refresh(db_phrase)
    for order, word_id in enumerate(phrase.words):
        db_phrase_component = models.PhraseComponent(phrase_id=db_phrase.id, word_id=word_id, order=order)
        db.add(db_phrase_component)
    db.commit()
    words = db.query(models.Word).filter(models.Word.id.in_(phrase.words)).all()
    return db_phrase, words

def get_phrases_service(db: Session):
    db_phrases = db.query(models.Phrase).options(
        joinedload(models.Phrase.meanings).joinedload(models.PhraseMeaning.examples),
        joinedload(models.Phrase.components).joinedload(models.PhraseComponent.word).joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
        joinedload(models.Phrase.components).joinedload(models.PhraseComponent.word).joinedload(models.Word.components).joinedload(models.WordComponentLink.component).joinedload(models.WordComponent.meanings)
    ).all()
    return db_phrases

def get_phrase_service(phrase_id: int, db: Session):
    phrase = db.query(models.Phrase).options(
        joinedload(models.Phrase.meanings).joinedload(models.PhraseMeaning.examples),
        joinedload(models.Phrase.components).joinedload(models.PhraseComponent.word).joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
        joinedload(models.Phrase.components).joinedload(models.PhraseComponent.word).joinedload(models.Word.components).joinedload(models.WordComponentLink.component).joinedload(models.WordComponent.meanings)
    ).filter(models.Phrase.id == phrase_id).first()
    return phrase

def update_phrase_service(phrase_id: int, phrase_update: schemas.PhraseCreate, db: Session):
    phrase = db.query(models.Phrase).filter(models.Phrase.id == phrase_id).first()
    if not phrase:
        return None
    
    for key, value in phrase_update.dict(exclude_unset=True, exclude={"words"}).items():
        setattr(phrase, key, value)
    
    if "words" in phrase_update.dict(exclude_unset=True):
        
        db.query(models.PhraseComponent).filter(models.PhraseComponent.phrase_id == phrase_id).delete()
        db.commit()
        
        for order, word_id in enumerate(phrase_update.words):
            db_phrase_component = models.PhraseComponent(phrase_id=phrase.id, word_id=word_id, order=order)
            db.add(db_phrase_component)
        db.commit()
    db.commit()
    db.refresh(phrase)
    return phrase

def delete_phrase_service(phrase_id: int, db: Session):
    phrase = db.query(models.Phrase).filter(models.Phrase.id == phrase_id).first()
    if not phrase:
        return False
    db.query(models.UserPhraseNote).filter(models.UserPhraseNote.phrase_id == phrase_id).delete()
    db.query(models.PhraseMeaningExample).filter(
        models.PhraseMeaningExample.phrase_meaning_id.in_(
            db.query(models.PhraseMeaning.id).filter(models.PhraseMeaning.phrase_id == phrase_id)
        )
    ).delete()
    db.query(models.PhraseMeaning).filter(models.PhraseMeaning.phrase_id == phrase_id).delete()
    db.query(models.PhraseComponent).filter(models.PhraseComponent.phrase_id == phrase_id).delete()
    db.query(models.PhraseLabelLink).filter(models.PhraseLabelLink.phrase_id == phrase_id).delete()
    db.query(models.SemanticGroupLink).filter(models.SemanticGroupLink.phrase_id == phrase_id).delete()
    db.delete(phrase)
    db.commit()
    return True

def add_phrase_meaning_service(phrase_id: int, meaning: schemas.PhraseMeaningCreate, db: Session):
    db_meaning = models.PhraseMeaning(phrase_id=phrase_id, meaning=meaning.meaning)
    db.add(db_meaning)
    db.commit()
    db.refresh(db_meaning)
    return db_meaning

def add_phrase_example_service(phrase_id: int, example: schemas.PhraseMeaningExampleCreate, db: Session):
    db_example = models.PhraseMeaningExample(
        phrase_meaning_id=example.phrase_meaning_id,
        example_text=example.example_text,
        example_text_german=example.example_text_german
    )
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

def add_phrase_note_service(phrase_id: int, note: schemas.UserPhraseNoteCreate, user_id: int, db: Session):
    db_note = models.UserPhraseNote(user_id=user_id, phrase_id=phrase_id, note=note.note, flag=note.flag)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note
