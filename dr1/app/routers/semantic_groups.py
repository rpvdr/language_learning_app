from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, auth
from ..database import SessionLocal
from typing import List
from app.utils.gemini import analyze_error_with_gemini
import logging
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def phrase_to_text(phrase):
    
    words = [pc.word.text for pc in sorted(phrase.components, key=lambda c: c.order) if pc.word]
    return " ".join(words) if words else str(phrase.id)

async def generate_semantic_group_difference_explanation(group_id: int, db_session_factory):
    db = db_session_factory()
    try:
        group = db.query(models.SemanticGroup).filter(models.SemanticGroup.id == group_id).first()
        if not group:
            return
        words = [link.word.text for link in group.links if link.word]
        phrases = [phrase_to_text(link.phrase) for link in group.links if link.phrase]
        if not words and not phrases:
            group.difference_explanation = "NO WORDS OR PHRASES"
            db.commit()
            print("NO WORDS OR PHRASES")
            return
        prompt = (
            "Поясни дуже коротко українською мовою, у чому різниця між наступними словами та фразами: "
            f"{', '.join(words + phrases)}. "
            "Відповідь має бути максимально лаконічною, 1-2 речення."
        )
        try:
            explanation = await gemini_laconic_explanation(prompt)
            if not explanation:
                explanation = "NO RESPONSE FROM GEMINI"
        except Exception as e:
            logging.exception("Gemini error")
            explanation = f"ERROR: {e}"
        group.difference_explanation = explanation
        db.commit()
        print(f"Gemini prompt: {prompt}")
        print(f"Gemini explanation: {explanation}")
    finally:
        db.close()


async def gemini_laconic_explanation(prompt: str) -> str:
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "<YOUR_GEMINI_API_KEY>"
    GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key=" + GEMINI_API_KEY
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(GEMINI_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"ERROR: {e}"

@router.post("/semantic-groups", response_model=schemas.SemanticGroupResponse)
def create_semantic_group(
    group: schemas.SemanticGroupCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_group = models.SemanticGroup(
        name=group.name,
        categories=group.categories,
        level=group.level,
        frequency=group.frequency,
        explanation=group.explanation
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    
    for word_id in group.word_ids or []:
        link = models.SemanticGroupLink(group_id=db_group.id, word_id=word_id)
        db.add(link)
    for phrase_id in group.phrase_ids or []:
        link = models.SemanticGroupLink(group_id=db_group.id, phrase_id=phrase_id)
        db.add(link)
    db.commit()
    db.refresh(db_group)

    background_tasks.add_task(generate_semantic_group_difference_explanation, db_group.id, SessionLocal)
    return db_group

@router.get("/semantic-groups/{group_id}", response_model=schemas.SemanticGroupResponse)
def get_semantic_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    group = (
        db.query(models.SemanticGroup)
        .options(
            joinedload(models.SemanticGroup.links).joinedload(models.SemanticGroupLink.word).joinedload(models.Word.components).joinedload(models.WordComponentLink.component).joinedload(models.WordComponent.meanings),
            joinedload(models.SemanticGroup.links).joinedload(models.SemanticGroupLink.word).joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
            joinedload(models.SemanticGroup.links).joinedload(models.SemanticGroupLink.word).joinedload(models.Word.part_of_speech_obj),
            joinedload(models.SemanticGroup.links).joinedload(models.SemanticGroupLink.phrase).joinedload(models.Phrase.components).joinedload(models.PhraseComponent.word).joinedload(models.Word.meanings).joinedload(models.WordMeaning.examples),
            joinedload(models.SemanticGroup.links).joinedload(models.SemanticGroupLink.phrase).joinedload(models.Phrase.meanings).joinedload(models.PhraseMeaning.examples),
            joinedload(models.SemanticGroup.links).joinedload(models.SemanticGroupLink.phrase).joinedload(models.Phrase.labels).joinedload(models.PhraseLabelLink.label),
        )
        .filter(models.SemanticGroup.id == group_id)
        .first()
    )
    if not group:
        raise HTTPException(status_code=404, detail="Semantic group not found")

    
    word_objs = []
    for link in group.links:
        if link.word:
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
                )
                for clink in w.components
            ]
            word_objs.append(
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
                    semantic_groups=[]
                )
            )

    
    phrase_objs = []
    for link in group.links:
        if link.phrase:
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
                    semantic_groups=[]
                ))
            labels = [link.label.name for link in p.labels] if hasattr(p, 'labels') else []
            category_names = []
            if p.categories:
                cats = db.query(models.Category).filter(models.Category.id.in_(p.categories)).all()
                category_names = [c.name for c in cats]
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
                ]
            ))

    return schemas.SemanticGroupResponse(
        id=group.id,
        name=group.name,
        categories=group.categories,
        category_names=getattr(group, "category_names", None),
        level=group.level,
        frequency=group.frequency,
        words=word_objs,
        phrases=phrase_objs,
        explanation=group.explanation,
        difference_explanation=group.difference_explanation,
        word_ids=[link.word_id for link in group.links if link.word_id],
        phrase_ids=[link.phrase_id for link in group.links if link.phrase_id],
    )

@router.get("/semantic-groups", response_model=List[schemas.SemanticGroupResponse])
def list_semantic_groups(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    groups = db.query(models.SemanticGroup).all()
    return groups

@router.patch("/semantic-groups/{group_id}", response_model=schemas.SemanticGroupResponse)
async def update_semantic_group(
    group_id: int,
    data: dict = Body(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    print("PATCH endpoint called, data:", data)
    group = db.query(models.SemanticGroup).filter(models.SemanticGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Semantic group not found")
    regenerate = False
    if "word_ids" in data or "phrase_ids" in data:
        
        db.query(models.SemanticGroupLink).filter(models.SemanticGroupLink.group_id == group_id).delete()
        for word_id in data.get("word_ids", []):
            link = models.SemanticGroupLink(group_id=group_id, word_id=word_id)
            db.add(link)
        for phrase_id in data.get("phrase_ids", []):
            link = models.SemanticGroupLink(group_id=group_id, phrase_id=phrase_id)
            db.add(link)
        regenerate = True
    if "explanation" in data:
        group.explanation = data["explanation"]
    if "difference_explanation" in data:
        group.difference_explanation = data["difference_explanation"]
    db.commit()
    db.refresh(group)
    if data.get("regenerate_difference_explanation") or regenerate:
        await generate_semantic_group_difference_explanation(group.id, SessionLocal)
        print("generate_difference_explanation finished")
    return group

@router.delete("/semantic-groups/{group_id}", response_model=dict)
def delete_semantic_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    group = db.query(models.SemanticGroup).filter(models.SemanticGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Semantic group not found")
    db.query(models.SemanticGroupLink).filter(models.SemanticGroupLink.group_id == group_id).delete()
    db.delete(group)
    db.commit()
    return {"success": True} 