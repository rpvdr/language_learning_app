from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from .. import models, schemas, auth
from ..database import SessionLocal
from app.services.word_service import *
import logging
import sqlalchemy
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/words", response_model=schemas.WordResponse)
def create_word(word: schemas.WordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    return create_word_service(word, db)

@router.get("/words", response_model=List[schemas.WordResponse])
def read_words(skip: int = 0, db: Session = Depends(get_db)):
    words = get_words_service(db)
    result = []
    for w in words:
        components = [
            schemas.WordComponentResponse(
                id=link.component.id,
                type=link.component.type,
                text=link.component.text,
                meanings=[
                    schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                    for m in link.component.meanings
                ],
                value_count=len(link.component.meanings)
            )
            for link in w.components
        ]
        category_names = []
        if w.categories:
            cats = db.query(models.Category).filter(models.Category.id.in_(w.categories)).all()
            category_names = [c.name for c in cats]
        result.append(schemas.WordResponse(
            id=w.id,
            text=w.text,
            gender=w.gender,
            plural_form=w.plural_form,
            verb_form2=w.verb_form2,
            verb_form3=w.verb_form3,
            reflexivity=w.reflexivity,
            case=w.case,
            part_of_speech=w.part_of_speech,
            part_of_speech_obj=w.part_of_speech_obj,
            categories=w.categories,
            category_names=category_names,
            level=w.level,
            frequency=w.frequency,
            components=components,
            component_count=w.component_count,
            value_count=w.value_count,
            meanings=[
                schemas.WordMeaningResponse(
                    id=m.id,
                    meaning=m.meaning,
                    examples=[
                        schemas.WordMeaningExampleResponse(
                            id=e.id,
                            example_text=e.example_text,
                            example_text_german=e.example_text_german
                        ) for e in m.examples
                    ]
                ) for m in w.meanings
            ]
        ))
    return result

@router.get("/words/{word_id}", response_model=schemas.WordResponse)
def read_word(word_id: int, db: Session = Depends(get_db)):
    w = get_word_service(word_id, db)
    if not w:
        raise HTTPException(status_code=404, detail="Word not found")
    
    logging.warning(f"GET /words/{word_id}: meanings={[m.id for m in w.meanings]}")
    for m in w.meanings:
        logging.warning(f"  meaning {m.id} examples={[e.id for e in m.examples]}")
    
    logging.warning(f"DB URL: {os.environ.get('DATABASE_URL')}")
    components = [
        schemas.WordComponentResponse(
            id=link.component.id,
            type=link.component.type,
            text=link.component.text,
            meanings=[
                schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                for m in link.component.meanings
            ],
            value_count=len(link.component.meanings)
        )
        for link in w.components
    ]
    category_names = []
    if w.categories:
        cats = db.query(models.Category).filter(models.Category.id.in_(w.categories)).all()
        category_names = [c.name for c in cats]
    return schemas.WordResponse(
        id=w.id,
        text=w.text,
        gender=w.gender,
        plural_form=w.plural_form,
        verb_form2=w.verb_form2,
        verb_form3=w.verb_form3,
        reflexivity=w.reflexivity,
        case=w.case,
        part_of_speech=w.part_of_speech,
        part_of_speech_obj=w.part_of_speech_obj,
        categories=w.categories,
        category_names=category_names,
        level=w.level,
        frequency=w.frequency,
        components=components,
        component_count=w.component_count,
        value_count=w.value_count,
        meanings=[
            schemas.WordMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.WordMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in w.meanings
        ]
    )

@router.put("/words/{word_id}", response_model=schemas.WordResponse)
def update_word(word_id: int, word_update: schemas.WordUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    w = db.query(models.Word).filter(models.Word.id == word_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Word not found")
    
    for key, value in word_update.dict(exclude_unset=True, exclude={"meanings"}).items():
        setattr(w, key, value)
    
    if word_update.meanings is not None:
        old_meanings = {m.id: m for m in w.meanings}
        new_meanings_data = word_update.meanings or []
        new_meaning_ids = set()
        for meaning_data in new_meanings_data:
            if meaning_data.id and meaning_data.id in old_meanings:
                m = old_meanings[meaning_data.id]
                if meaning_data.meaning is not None:
                    m.meaning = meaning_data.meaning
                old_examples = {e.id: e for e in m.examples}
                new_examples_data = meaning_data.examples or []
                new_example_ids = set()
                for ex_data in new_examples_data:
                    if ex_data.id and ex_data.id in old_examples:
                        e = old_examples[ex_data.id]
                        if ex_data.example_text is not None:
                            e.example_text = ex_data.example_text
                        if ex_data.example_text_german is not None:
                            e.example_text_german = ex_data.example_text_german
                        new_example_ids.add(e.id)
                    else:
                        e = models.WordMeaningExample(
                            word_meaning_id=m.id,
                            example_text=ex_data.example_text or "",
                            example_text_german=ex_data.example_text_german
                        )
                        db.add(e)
                        db.commit()
                        db.refresh(e)
                        new_example_ids.add(e.id)
                for ex_id, ex in old_examples.items():
                    if ex_id not in new_example_ids:
                        db.delete(ex)
                new_meaning_ids.add(m.id)
            else:
                m = models.WordMeaning(word_id=w.id, meaning=meaning_data.meaning or "")
                db.add(m)
                db.commit()
                db.refresh(m)
                if meaning_data.examples:
                    for ex_data in meaning_data.examples:
                        e = models.WordMeaningExample(
                            word_meaning_id=m.id,
                            example_text=ex_data.example_text or "",
                            example_text_german=ex_data.example_text_german
                        )
                        db.add(e)
                        db.commit()
                        db.refresh(e)
                new_meaning_ids.add(m.id)
        for old_id, old_m in old_meanings.items():
            if old_id not in new_meaning_ids:
                for ex in old_m.examples:
                    db.delete(ex)
                db.delete(old_m)
        db.commit()
    db.commit()
    db.refresh(w)
    w_full = get_word_service(w.id, db)
    components = [
        schemas.WordComponentResponse(
            id=link.component.id,
            type=link.component.type,
            text=link.component.text,
            meanings=[
                schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                for m in link.component.meanings
            ],
            value_count=len(link.component.meanings)
        )
        for link in w_full.components
    ]
    return schemas.WordResponse(
        id=w_full.id,
        text=w_full.text,
        gender=w_full.gender,
        plural_form=w_full.plural_form,
        verb_form2=w_full.verb_form2,
        verb_form3=w_full.verb_form3,
        reflexivity=w_full.reflexivity,
        case=w_full.case,
        part_of_speech=w_full.part_of_speech,
        part_of_speech_obj=w_full.part_of_speech_obj,
        categories=w_full.categories,
        category_names=[],
        level=w_full.level,
        frequency=w_full.frequency,
        components=components,
        component_count=w_full.component_count,
        value_count=w_full.value_count,
        meanings=[
            schemas.WordMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.WordMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in w_full.meanings
        ]
    )

@router.delete("/words/{word_id}", status_code=204)
def delete_word(word_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    success = delete_word_service(word_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Word not found")
    return

@router.post("/words/{word_id}/components", response_model=schemas.WordResponse)
def add_word_component(word_id: int, component: schemas.WordComponentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    w = add_word_component_service(word_id, component, db)
    components = [
        schemas.WordComponentResponse(
            id=link.component.id,
            type=link.component.type,
            text=link.component.text,
            meanings=[
                schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                for m in link.component.meanings
            ],
            value_count=len(link.component.meanings)
        )
        for link in w.components
    ]
    return schemas.WordResponse(
        id=w.id,
        text=w.text,
        gender=w.gender,
        plural_form=w.plural_form,
        verb_form2=w.verb_form2,
        verb_form3=w.verb_form3,
        reflexivity=w.reflexivity,
        case=w.case,
        part_of_speech=w.part_of_speech,
        part_of_speech_obj=w.part_of_speech_obj,
        categories=w.categories,
        category_names=[],
        level=w.level,
        frequency=w.frequency,
        components=components,
        component_count=w.component_count,
        value_count=w.value_count,
        meanings=[
            schemas.WordMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.WordMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in w.meanings
        ]
    )

@router.post("/words/{word_id}/meanings", response_model=schemas.WordMeaningResponse)
def add_word_meaning(word_id: int, meaning: schemas.WordMeaningCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    return add_word_meaning_service(word_id, meaning, db)

@router.post("/words/{word_id}/examples", response_model=schemas.WordMeaningExampleResponse)
def add_word_example(word_id: int, example: schemas.WordMeaningExampleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return add_word_example_service(word_id, example, db)

@router.get("/words/search", response_model=List[schemas.WordResponse])
def search_words_by_component(component_text: str, component_type: str, db: Session = Depends(get_db)):
    words = search_words_by_component_service(component_text, component_type, db)
    result = []
    for w in words:
        components = [
            schemas.WordComponentResponse(
                id=link.component.id,
                type=link.component.type,
                text=link.component.text,
                meanings=[
                    schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                    for m in link.component.meanings
                ],
                value_count=len(link.component.meanings)
            )
            for link in w.components
        ]
        result.append(schemas.WordResponse(
            id=w.id,
            text=w.text,
            gender=w.gender,
            plural_form=w.plural_form,
            verb_form2=w.verb_form2,
            verb_form3=w.verb_form3,
            reflexivity=w.reflexivity,
            case=w.case,
            part_of_speech=w.part_of_speech,
            part_of_speech_obj=w.part_of_speech_obj,
            categories=w.categories,
            category_names=[],
            level=w.level,
            frequency=w.frequency,
            components=components,
            component_count=w.component_count,
            value_count=w.value_count,
            meanings=[
                schemas.WordMeaningResponse(
                    id=m.id,
                    meaning=m.meaning,
                    examples=[
                        schemas.WordMeaningExampleResponse(
                            id=e.id,
                            example_text=e.example_text,
                            example_text_german=e.example_text_german
                        ) for e in m.examples
                    ]
                ) for m in w.meanings
            ]
        ))
    return result

@router.get("/words/search-by-text", response_model=List[schemas.WordResponse])
def search_words_by_text(query: str, db: Session = Depends(get_db)):
    return search_words_by_text_service(query, db)

@router.put("/words/meanings/{meaning_id}", response_model=schemas.WordMeaningResponse)
def update_word_meaning(meaning_id: int, meaning: schemas.WordMeaningCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    m = db.query(models.WordMeaning).filter(models.WordMeaning.id == meaning_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meaning not found")
    m.meaning = meaning.meaning
    db.commit()
    db.refresh(m)
    return schemas.WordMeaningResponse(
        id=m.id,
        meaning=m.meaning,
        examples=[
            schemas.WordMeaningExampleResponse(
                id=e.id,
                example_text=e.example_text,
                example_text_german=e.example_text_german
            ) for e in m.examples
        ]
    )

@router.delete("/words/meanings/{meaning_id}", status_code=204)
def delete_word_meaning(meaning_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    m = db.query(models.WordMeaning).filter(models.WordMeaning.id == meaning_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meaning not found")
    db.delete(m)
    db.commit()
    return

@router.post("/words/meanings/{meaning_id}/examples", response_model=schemas.WordMeaningExampleResponse)
def add_word_meaning_example(meaning_id: int, example: schemas.WordMeaningExampleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    db_example = models.WordMeaningExample(word_meaning_id=meaning_id, example_text=example.example_text, example_text_german=example.example_text_german)
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

@router.put("/words/examples/{example_id}", response_model=schemas.WordMeaningExampleResponse)
def update_word_meaning_example(example_id: int, example: schemas.WordMeaningExampleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    e = db.query(models.WordMeaningExample).filter(models.WordMeaningExample.id == example_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Example not found")
    e.example_text = example.example_text
    e.example_text_german = example.example_text_german
    db.commit()
    db.refresh(e)
    return e

@router.delete("/words/examples/{example_id}", status_code=204)
def delete_word_meaning_example(example_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    e = db.query(models.WordMeaningExample).filter(models.WordMeaningExample.id == example_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Example not found")
    db.delete(e)
    db.commit()
    return

@router.patch("/words/{word_id}/remove-category/{category_id}", response_model=schemas.WordResponse)
def remove_category_from_word(word_id: int, category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    if not word.categories:
        return word
    new_categories = [cat for cat in word.categories if cat != category_id]
    word.categories = new_categories
    db.commit()
    db.refresh(word)
    
    components = [
        schemas.WordComponentResponse(
            id=link.component.id,
            type=link.component.type,
            text=link.component.text,
            meanings=[
                schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                for m in link.component.meanings
            ],
            value_count=len(link.component.meanings)
        )
        for link in word.components
    ]
    return schemas.WordResponse(
        id=word.id,
        text=word.text,
        gender=word.gender,
        plural_form=word.plural_form,
        verb_form2=word.verb_form2,
        verb_form3=word.verb_form3,
        reflexivity=word.reflexivity,
        case=word.case,
        part_of_speech=word.part_of_speech,
        part_of_speech_obj=word.part_of_speech_obj,
        categories=word.categories,
        category_names=[],
        level=word.level,
        frequency=word.frequency,
        components=components,
        component_count=word.component_count,
        value_count=word.value_count,
        meanings=[
            schemas.WordMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.WordMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in word.meanings
        ]
    )

@router.patch("/words/meanings/{meaning_id}", response_model=schemas.WordMeaningResponse)
def patch_word_meaning(meaning_id: int, meaning: schemas.WordMeaningCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    m = db.query(models.WordMeaning).filter(models.WordMeaning.id == meaning_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meaning not found")
    if meaning.meaning is not None:
        m.meaning = meaning.meaning
    db.commit()
    db.refresh(m)
    return schemas.WordMeaningResponse(
        id=m.id,
        meaning=m.meaning,
        examples=[
            schemas.WordMeaningExampleResponse(
                id=e.id,
                example_text=e.example_text,
                example_text_german=e.example_text_german
            ) for e in m.examples
        ]
    )

@router.patch("/words/examples/{example_id}", response_model=schemas.WordMeaningExampleResponse)
def patch_word_meaning_example(example_id: int, example: schemas.WordMeaningExampleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    e = db.query(models.WordMeaningExample).filter(models.WordMeaningExample.id == example_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Example not found")
    if example.example_text is not None:
        e.example_text = example.example_text
    if example.example_text_german is not None:
        e.example_text_german = example.example_text_german
    db.commit()
    db.refresh(e)
    return schemas.WordMeaningExampleResponse(
        id=e.id,
        example_text=e.example_text,
        example_text_german=e.example_text_german
    )
