from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from .. import models, schemas, auth
from ..database import SessionLocal
from sqlalchemy import or_
from app.services.search_word_service import search_words_service
from app.services.search_phrase_service import search_phrases_service
from app.services.search_semantic_group_service import search_semantic_groups_service
from app.services.search_mistake_service import search_mistakes_service
from app.services.search_word_component_service import search_word_components_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/search/words", response_model=schemas.PaginatedWordResponse)
def search_words(
    query: Optional[str] = Query(None),
    category: Optional[str] = None,
    level: Optional[str] = None,
    part_of_speech: Optional[int] = None,
    component_text: Optional[str] = None,
    semantic_group_id: Optional[int] = None,
    frequency: Optional[str] = None,
    word: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if query == "": query = None
    if category == "": category = None
    if level == "": level = None
    if frequency == "": frequency = None
    if word == "": word = None
    if not any([query, category, level, frequency, word]):
        return {"items": [], "next_offset": None, "total_count": 0}
    cat = int(category) if category else None
    freq = float(frequency) if frequency else None
    words, total_count = search_words_service(query, cat, level, part_of_speech, component_text, semantic_group_id, limit, offset, db)
    items = []
    for w in words[:limit]:
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
        semantic_groups = [
            {
                "id": link.group.id,
                "name": link.group.name,
                "level": link.group.level,
                "frequency": link.group.frequency,
                "categories": link.group.categories,
                "category_names": [],
                "explanation": link.group.explanation
            }
            for link in getattr(w, "semantic_links", []) if link.group is not None
        ]
        items.append(
            schemas.WordResponse(
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
                ],
                semantic_groups=semantic_groups
            )
        )
    next_offset = offset + limit if len(words) > limit else None
    return {"items": items, "next_offset": next_offset, "total_count": total_count}

@router.get("/search/phrases", response_model=schemas.PaginatedPhraseResponse)
def search_phrases(
    query: Optional[str] = Query(None),
    category: Optional[str] = None,
    level: Optional[str] = None,
    label: Optional[str] = None,
    word_id: Optional[str] = None,
    semantic_group_id: Optional[int] = None,
    part_of_speech: Optional[str] = None,
    component_text: Optional[str] = None,
    frequency: Optional[str] = None,
    word: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if query == "": query = None
    if category == "": category = None
    if level == "": level = None
    if frequency == "": frequency = None
    if word == "": word = None
    if word_id == "": word_id = None
    if part_of_speech == "": part_of_speech = None
    if component_text == "": component_text = None
    if not any([query, category, level, frequency, word]):
        return {"items": [], "next_offset": None, "total_count": 0}
    cat = int(category) if category else None
    freq = float(frequency) if frequency else None
    part_of_speech_int = int(part_of_speech) if part_of_speech else None
    phrases, total_count = search_phrases_service(query, cat, level, label, word_id, semantic_group_id, limit, offset, db)
    items = []
    for p in phrases[:limit]:
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
            semantic_groups = [
                {
                    "id": link.group.id,
                    "name": link.group.name,
                    "level": link.group.level,
                    "frequency": link.group.frequency,
                    "categories": link.group.categories,
                    "category_names": [],
                    "explanation": link.group.explanation
                }
                for link in getattr(word, "semantic_links", []) if link.group is not None
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
                ],
                semantic_groups=semantic_groups
            ))
        labels = [link.label.name for link in p.labels]
        category_names = []
        if p.categories:
            cats = db.query(models.Category).filter(models.Category.id.in_(p.categories)).all()
            category_names = [c.name for c in cats]
        phrase_semantic_groups = [
            {
                "id": link.group.id,
                "name": link.group.name,
                "level": link.group.level,
                "frequency": link.group.frequency,
                "categories": link.group.categories,
                "category_names": [],
                "explanation": link.group.explanation
            }
            for link in getattr(p, "semantic_links", []) if link.group is not None
        ]
        items.append(schemas.PhraseResponse(
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
            ],
            semantic_groups=phrase_semantic_groups
        ))
    next_offset = offset + limit if len(phrases) > limit else None
    return {"items": items, "next_offset": next_offset, "total_count": total_count}

@router.get("/search/semantic-groups", response_model=schemas.PaginatedSemanticGroupResponse)
def search_semantic_groups(
    query: Optional[str] = Query(None),
    category: Optional[str] = None,
    level: Optional[str] = None,
    word_id: Optional[str] = None,
    phrase_id: Optional[str] = None,
    frequency: Optional[str] = None,
    word: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if query == "": query = None
    if category == "": category = None
    if level == "": level = None
    if frequency == "": frequency = None
    if word == "": word = None
    if word_id == "": word_id = None
    if phrase_id == "": phrase_id = None
    if not any([query, category, level, frequency, word]):
        return {"items": [], "next_offset": None, "total_count": 0}
    cat = int(category) if category else None
    freq = float(frequency) if frequency else None
    wid = int(word_id) if word_id else None
    pid = int(phrase_id) if phrase_id else None
    groups, total_count = search_semantic_groups_service(query, cat, level, wid, pid, limit, offset, db)
    items = []
    for g in groups[:limit]:
        word_objs = []
        phrase_objs = []
        for link in g.links:
            if link.word is not None:
                w = link.word
                components = [
                    schemas.WordComponentResponse(
                        id=clink.component.id,
                        type=clink.component.type,
                        text=clink.component.text,
                        meanings=[
                            schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                            for m in clink.component.meanings
                        ],
                        value_count=len(clink.component.meanings)
                    ) for clink in w.components
                ]
                semantic_groups = [
                    {
                        "id": l.group.id,
                        "name": l.group.name,
                        "level": l.group.level,
                        "frequency": l.group.frequency,
                        "categories": l.group.categories,
                        "category_names": [],
                        "explanation": l.group.explanation
                    }
                    for l in getattr(w, "semantic_links", []) if l.group is not None
                ]
                word_objs.append(schemas.WordResponse(
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
                    ],
                    semantic_groups=semantic_groups
                ))
            if link.phrase is not None:
                p = link.phrase
                words = []
                for pc in sorted(p.components, key=lambda c: c.order):
                    word = pc.word
                    components = [
                        schemas.WordComponentResponse(
                            id=clink.component.id,
                            type=clink.component.type,
                            text=clink.component.text,
                            meanings=[
                                schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                                for m in clink.component.meanings
                            ],
                            value_count=len(clink.component.meanings)
                        ) for clink in word.components
                    ]
                    semantic_groups = [
                        {
                            "id": l.group.id,
                            "name": l.group.name,
                            "level": l.group.level,
                            "frequency": l.group.frequency,
                            "categories": l.group.categories,
                            "category_names": [],
                            "explanation": l.group.explanation
                        }
                        for l in getattr(word, "semantic_links", []) if l.group is not None
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
                        ],
                        semantic_groups=semantic_groups
                    ))
                labels = [link.label.name for link in p.labels] if hasattr(p, 'labels') else []
                category_names = []
                if p.categories:
                    cats = db.query(models.Category).filter(models.Category.id.in_(p.categories)).all()
                    category_names = [c.name for c in cats]
                phrase_semantic_groups = [
                    {
                        "id": l.group.id,
                        "name": l.group.name,
                        "level": l.group.level,
                        "frequency": l.group.frequency,
                        "categories": l.group.categories,
                        "category_names": [],
                        "explanation": l.group.explanation
                    }
                    for l in getattr(p, "semantic_links", []) if l.group is not None
                ]
                phrase_objs.append(schemas.PhraseResponse(
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
                    ],
                    semantic_groups=phrase_semantic_groups
                ))
        category_names = []
        if g.categories:
            cats = db.query(models.Category).filter(models.Category.id.in_(g.categories)).all()
            category_names = [c.name for c in cats]
        items.append(schemas.SemanticGroupResponse(
            id=g.id,
            name=g.name,
            categories=g.categories,
            category_names=category_names,
            level=g.level,
            frequency=g.frequency,
            words=word_objs,
            phrases=phrase_objs,
            explanation=g.explanation,
            difference_explanation=g.difference_explanation
        ))
    next_offset = offset + limit if len(groups) > limit else None
    return {"items": items, "next_offset": next_offset, "total_count": total_count}

@router.get("/search/mistakes", response_model=schemas.PaginatedUserAnswerErrorResponse)
def search_mistakes(
    query: Optional[str] = Query(None, min_length=2),
    category: Optional[int] = None,
    level: Optional[str] = None,
    error_type: Optional[str] = None,
    user_id: Optional[int] = None,
    item_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    mistakes, total_count = search_mistakes_service(query, category, level, error_type, user_id, item_type, limit, offset, db)
    items = [
        schemas.UserAnswerError(
            id=e.id,
            user_id=e.user_id,
            item_type=e.item_type,
            item_id=e.item_id,
            correct_answer=e.correct_answer,
            user_answer=e.user_answer,
            error_analysis=e.error_analysis,
            brief_explanation=e.brief_explanation,
            created_at=e.created_at
        ) for e in mistakes[:limit]
    ]
    next_offset = offset + limit if len(mistakes) > limit else None
    return {"items": items, "next_offset": next_offset, "total_count": total_count}

@router.get("/search/word-components", response_model=schemas.PaginatedWordComponentResponse)
def search_word_components(
    query: Optional[str] = Query(None, min_length=2),
    category: Optional[int] = None,
    level: Optional[str] = None,
    type: Optional[str] = None,
    word_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    components, total_count = search_word_components_service(query, type, word_id, limit, offset, db)
    items = [
        schemas.WordComponentResponse(
            id=c.id,
            type=c.type,
            text=c.text,
            meanings=[
                schemas.WordComponentMeaningResponse(id=m.id, meaning=m.meaning)
                for m in c.meanings
            ],
            value_count=len(c.meanings)
        ) for c in components[:limit]
    ]
    next_offset = offset + limit if len(components) > limit else None
    return {"items": items, "next_offset": next_offset, "total_count": total_count}

@router.get("/levels", response_model=List[str])
def get_levels(current_user: models.User = Depends(auth.get_current_user)):
    return ["A1", "A2", "B1", "B2", "C1", "C2"] 