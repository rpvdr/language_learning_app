from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import SessionLocal
from app.services.component_service import *
from app.services.search_word_component_service import search_word_components_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/components", response_model=schemas.PaginatedWordComponentResponse)
def list_word_components(query: str = "", type: str = "", word_id: int = None, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    components, total_count = search_word_components_service(query, type, word_id, limit, offset, db)
    items = [
        schemas.WordComponentResponse(
            id=c.id,
            type=c.type,
            text=c.text,
            meanings=[schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning) for m in c.meanings],
            value_count=len(c.meanings)
        ) for c in components[:limit]
    ]
    next_offset = offset + limit if len(components) > limit else None
    return schemas.PaginatedWordComponentResponse(items=items, next_offset=next_offset, total_count=total_count)

@router.get("/components/{component_id}", response_model=schemas.WordComponentResponse)
def get_word_component(component_id: int, db: Session = Depends(get_db)):
    c = db.query(models.WordComponent).filter(models.WordComponent.id == component_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Component not found")
    return schemas.WordComponentResponse(
        id=c.id,
        type=c.type,
        text=c.text,
        meanings=[schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning) for m in c.meanings],
        value_count=len(c.meanings)
    )

@router.put("/components/{component_id}", response_model=schemas.WordComponentResponse)
def update_word_component(component_id: int, component: schemas.WordComponentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    c = db.query(models.WordComponent).filter(models.WordComponent.id == component_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Component not found")
    c.type = component.type
    c.text = component.text
    
    existing_meanings = {m.meaning for m in c.meanings}
    for meaning in component.meanings:
        if meaning not in existing_meanings:
            db_meaning = models.WordComponentMeaning(component_id=c.id, meaning=meaning)
            db.add(db_meaning)
    
    for m in list(c.meanings):
        if m.meaning not in component.meanings:
            db.delete(m)
    db.commit()
    db.refresh(c)
    return schemas.WordComponentResponse(
        id=c.id,
        type=c.type,
        text=c.text,
        meanings=[schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning) for m in c.meanings],
        value_count=len(c.meanings)
    )

@router.delete("/components/{component_id}", status_code=204)
def delete_word_component(component_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    c = db.query(models.WordComponent).filter(models.WordComponent.id == component_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Component not found")
    db.delete(c)
    db.commit()
    return

@router.delete("/words/{word_id}/components/{component_id}", status_code=204)
def delete_word_component_link(word_id: int, component_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized")
    link = db.query(models.WordComponentLink).filter(models.WordComponentLink.word_id == word_id, models.WordComponentLink.component_id == component_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return
