from sqlalchemy.orm import Session
from .. import models, schemas

def search_words_by_component_service(component_text: str, component_type: str, db: Session):
    component = db.query(models.WordComponent).filter(models.WordComponent.text == component_text, models.WordComponent.type == component_type).first()
    if not component:
        return []
    word_links = db.query(models.WordComponentLink).filter(models.WordComponentLink.component_id == component.id).all()
    word_ids = [link.word_id for link in word_links]
    words = db.query(models.Word).filter(models.Word.id.in_(word_ids)).all()
    return words

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
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    return word
