from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload
from typing import List
from .. import models, schemas, auth
from ..database import SessionLocal
from app.services.phrase_service import *

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/phrases", response_model=schemas.PhraseResponse)
def create_phrase(phrase: schemas.PhraseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    db_phrase, words = create_phrase_service(phrase, db)
    phrase_full = get_phrase_service(db_phrase.id, db)
    if not phrase_full:
        raise HTTPException(status_code=404, detail="Phrase not found after creation")
    words_resp = []
    for pc in sorted(phrase_full.components, key=lambda c: c.order):
        word = pc.word
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
            ) for link in word.components
        ]
        words_resp.append(schemas.WordResponse(
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
        ))
    labels = [link.label.name for link in phrase_full.labels]
    return schemas.PhraseResponse(
        id=phrase_full.id,
        categories=phrase_full.categories,
        category_names=[],
        level=phrase_full.level,
        frequency=phrase_full.frequency,
        words=words_resp,
        labels=labels,
        word_count=phrase_full.word_count,
        value_count=phrase_full.value_count,
        meanings=[
            schemas.PhraseMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.PhraseMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in phrase_full.meanings
        ]
    )

@router.get("/phrases", response_model=List[schemas.PhraseResponse])
def read_phrases(db: Session = Depends(get_db)):
    phrases = get_phrases_service(db)
    result = []
    for p in phrases:
        words = []
        for pc in sorted(p.components, key=lambda c: c.order):
            word = pc.word
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
                ) for link in word.components
            ]
            words.append(schemas.WordResponse(
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
            ))
        labels = [link.label.name for link in p.labels]
        category_names = []
        if p.categories:
            cats = db.query(models.Category).filter(models.Category.id.in_(p.categories)).all()
            category_names = [c.name for c in cats]
        result.append(schemas.PhraseResponse(
            id=p.id,
            categories=p.categories,
            category_names=category_names,
            level=p.level,
            frequency=p.frequency,
            words=words,
            labels=labels,
            word_count=p.word_count,
            value_count=p.value_count,
            meanings=[
                schemas.PhraseMeaningResponse(
                    id=m.id,
                    meaning=m.meaning,
                    examples=[
                        schemas.PhraseMeaningExampleResponse(
                            id=e.id,
                            example_text=e.example_text,
                            example_text_german=e.example_text_german
                        ) for e in m.examples
                    ]
                ) for m in p.meanings
            ]
        ))
    return result

@router.get("/phrases/{phrase_id}", response_model=schemas.PhraseDetailResponse)
def read_phrase(phrase_id: int, db: Session = Depends(get_db)):
    phrase = get_phrase_service(phrase_id, db)
    if not phrase:
        raise HTTPException(status_code=404, detail="Phrase not found")
    words = []
    for pc in sorted(phrase.components, key=lambda c: c.order):
        word = pc.word
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
            ) for link in word.components
        ]
        words.append(schemas.WordResponse(
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
        ))
    labels = [link.label.name for link in phrase.labels]
    category_names = []
    if phrase.categories:
        cats = db.query(models.Category).filter(models.Category.id.in_(phrase.categories)).all()
        category_names = [c.name for c in cats]
    return schemas.PhraseDetailResponse(
        id=phrase.id,
        categories=phrase.categories,
        category_names=category_names,
        level=phrase.level,
        frequency=phrase.frequency,
        words=words,
        labels=labels,
        word_count=phrase.word_count,
        value_count=phrase.value_count,
        meanings=[
            schemas.PhraseMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.PhraseMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in phrase.meanings
        ],
        translations=[],
        components=[]
    )

@router.put("/phrases/{phrase_id}", response_model=schemas.PhraseResponse)
def update_phrase(phrase_id: int, phrase_update: schemas.PhraseUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    phrase = db.query(models.Phrase).filter(models.Phrase.id == phrase_id).first()
    if not phrase:
        raise HTTPException(status_code=404, detail="Phrase not found")
    
    for key, value in phrase_update.dict(exclude_unset=True, exclude={"words", "labels", "meanings"}).items():
        setattr(phrase, key, value)
    
    if phrase_update.words is not None:
        db.query(models.PhraseComponent).filter(models.PhraseComponent.phrase_id == phrase_id).delete()
        db.commit()
        for order, word_id in enumerate(phrase_update.words):
            db_phrase_component = models.PhraseComponent(phrase_id=phrase.id, word_id=word_id, order=order)
            db.add(db_phrase_component)
        db.commit()
    
    if phrase_update.labels is not None:
        db.query(models.PhraseLabelLink).filter(models.PhraseLabelLink.phrase_id == phrase_id).delete()
        db.commit()
        for label_name in phrase_update.labels:
            label = db.query(models.PhraseLabel).filter(models.PhraseLabel.name == label_name).first()
            if not label:
                label = models.PhraseLabel(name=label_name)
                db.add(label)
                db.commit()
                db.refresh(label)
            link = models.PhraseLabelLink(phrase_id=phrase.id, label_id=label.id)
            db.add(link)
        db.commit()
    
    if phrase_update.meanings is not None:
        
        old_meanings = {m.id: m for m in phrase.meanings}
        new_meanings_data = phrase_update.meanings or []
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
                        e = models.PhraseMeaningExample(
                            phrase_meaning_id=m.id,
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
                
                m = models.PhraseMeaning(phrase_id=phrase.id, meaning=meaning_data.meaning or "")
                db.add(m)
                db.commit()
                db.refresh(m)
                if meaning_data.examples:
                    for ex_data in meaning_data.examples:
                        e = models.PhraseMeaningExample(
                            phrase_meaning_id=m.id,
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
    db.refresh(phrase)
    
    phrase_full = get_phrase_service(phrase.id, db)
    words_resp = []
    for pc in sorted(phrase_full.components, key=lambda c: c.order):
        word = pc.word
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
            ) for link in word.components
        ]
        words_resp.append(schemas.WordResponse(
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
        ))
    labels = [link.label.name for link in phrase_full.labels]
    return schemas.PhraseResponse(
        id=phrase_full.id,
        categories=phrase_full.categories,
        category_names=[],
        level=phrase_full.level,
        frequency=phrase_full.frequency,
        words=words_resp,
        labels=labels,
        word_count=phrase_full.word_count,
        value_count=phrase_full.value_count,
        meanings=[
            schemas.PhraseMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.PhraseMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in phrase_full.meanings
        ]
    )

@router.delete("/phrases/{phrase_id}", status_code=204)
def delete_phrase(phrase_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    success = delete_phrase_service(phrase_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Phrase not found")
    return

@router.post("/phrases/{phrase_id}/meanings", response_model=schemas.PhraseMeaningResponse)
def add_phrase_meaning(phrase_id: int, meaning: schemas.PhraseMeaningCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return add_phrase_meaning_service(phrase_id, meaning, db)

@router.post("/phrases/{phrase_id}/examples", response_model=schemas.PhraseMeaningExampleResponse)
def add_phrase_example(phrase_id: int, example: schemas.PhraseMeaningExampleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return add_phrase_example_service(phrase_id, example, db)

@router.post("/phrases/{phrase_id}/notes", response_model=schemas.UserPhraseNoteResponse)
def add_note(phrase_id: int, note: schemas.UserPhraseNoteCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return add_phrase_note_service(phrase_id, note, current_user.id, db)

@router.patch("/phrases/{phrase_id}/remove-category/{category_id}", response_model=schemas.PhraseResponse)
def remove_category_from_phrase(phrase_id: int, category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    phrase = db.query(models.Phrase).filter(models.Phrase.id == phrase_id).first()
    if not phrase:
        raise HTTPException(status_code=404, detail="Phrase not found")
    if not phrase.categories:
        return phrase
    new_categories = [cat for cat in phrase.categories if cat != category_id]
    phrase.categories = new_categories
    db.commit()
    db.refresh(phrase)
    
    phrase_full = get_phrase_service(phrase.id, db)
    words_resp = []
    for pc in sorted(phrase_full.components, key=lambda c: c.order):
        word = pc.word
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
            ) for link in word.components
        ]
        words_resp.append(schemas.WordResponse(
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
        ))
    labels = [link.label.name for link in phrase_full.labels]
    return schemas.PhraseResponse(
        id=phrase_full.id,
        categories=phrase_full.categories,
        category_names=[],
        level=phrase_full.level,
        frequency=phrase_full.frequency,
        words=words_resp,
        labels=labels,
        word_count=phrase_full.word_count,
        value_count=phrase_full.value_count,
        meanings=[
            schemas.PhraseMeaningResponse(
                id=m.id,
                meaning=m.meaning,
                examples=[
                    schemas.PhraseMeaningExampleResponse(
                        id=e.id,
                        example_text=e.example_text,
                        example_text_german=e.example_text_german
                    ) for e in m.examples
                ]
            ) for m in phrase_full.meanings
        ]
    )

@router.put("/meanings/{meaning_id}", response_model=schemas.PhraseMeaningResponse)
def update_phrase_meaning(meaning_id: int, meaning: schemas.PhraseMeaningCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    m = db.query(models.PhraseMeaning).filter(models.PhraseMeaning.id == meaning_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meaning not found")
    m.meaning = meaning.meaning
    db.commit()
    db.refresh(m)
    return schemas.PhraseMeaningResponse(
        id=m.id,
        meaning=m.meaning,
        examples=[
            schemas.PhraseMeaningExampleResponse(
                id=e.id,
                example_text=e.example_text,
                example_text_german=e.example_text_german
            ) for e in m.examples
        ]
    )

@router.delete("/meanings/{meaning_id}", status_code=204)
def delete_phrase_meaning(meaning_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    m = db.query(models.PhraseMeaning).filter(models.PhraseMeaning.id == meaning_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meaning not found")
    db.delete(m)
    db.commit()
    return

@router.patch("/meanings/{meaning_id}", response_model=schemas.PhraseMeaningResponse)
def patch_phrase_meaning(meaning_id: int, meaning: schemas.PhraseMeaningCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    m = db.query(models.PhraseMeaning).filter(models.PhraseMeaning.id == meaning_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meaning not found")
    if meaning.meaning is not None:
        m.meaning = meaning.meaning
    db.commit()
    db.refresh(m)
    return schemas.PhraseMeaningResponse(
        id=m.id,
        meaning=m.meaning,
        examples=[
            schemas.PhraseMeaningExampleResponse(
                id=e.id,
                example_text=e.example_text,
                example_text_german=e.example_text_german
            ) for e in m.examples
        ]
    )

@router.put("/examples/{example_id}", response_model=schemas.PhraseMeaningExampleResponse)
def update_phrase_meaning_example(example_id: int, example: schemas.PhraseMeaningExampleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    e = db.query(models.PhraseMeaningExample).filter(models.PhraseMeaningExample.id == example_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Example not found")
    e.example_text = example.example_text
    e.example_text_german = example.example_text_german
    db.commit()
    db.refresh(e)
    return schemas.PhraseMeaningExampleResponse(
        id=e.id,
        example_text=e.example_text,
        example_text_german=e.example_text_german
    )

@router.delete("/examples/{example_id}", status_code=204)
def delete_phrase_meaning_example(example_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    e = db.query(models.PhraseMeaningExample).filter(models.PhraseMeaningExample.id == example_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Example not found")
    db.delete(e)
    db.commit()
    return

@router.patch("/examples/{example_id}", response_model=schemas.PhraseMeaningExampleResponse)
def patch_phrase_meaning_example(example_id: int, example: schemas.PhraseMeaningExampleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    e = db.query(models.PhraseMeaningExample).filter(models.PhraseMeaningExample.id == example_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Example not found")
    if example.example_text is not None:
        e.example_text = example.example_text
    if example.example_text_german is not None:
        e.example_text_german = example.example_text_german
    db.commit()
    db.refresh(e)
    return schemas.PhraseMeaningExampleResponse(
        id=e.id,
        example_text=e.example_text,
        example_text_german=e.example_text_german
    )