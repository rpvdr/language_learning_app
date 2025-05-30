from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime, timezone
from fsrs import Scheduler, Card, Rating, ReviewLog
import json
from app.utils.gemini import analyze_error_with_gemini

def start_training_service(count, is_review, db, current_user):
    if is_review:
        reviews = db.query(models.UserCardReview).filter_by(user_id=current_user.id, is_review=True).all()
        due_cards = []
        for r in reviews:
            card = Card.from_dict(json.loads(r.card_json))
            if card.due <= datetime.now(timezone.utc):
                due_cards.append(r)
        selected = due_cards[:count]
        questions = []
        for r in selected:
            if r.item_type == "word":
                word = db.query(models.Word).get(r.item_id)
                if word is None:
                    continue
                meanings = []
                for m in word.meanings:
                    meanings.append({
                        "meaning": m.meaning,
                        "examples": [
                            {"example_text": ex.example_text} for ex in m.examples
                        ]
                    })
                if not meanings:
                    continue
                questions.append({
                    "item_type": "word",
                    "item_id": r.item_id,
                    "meanings": meanings,
                    "part_of_speech": word.part_of_speech,
                    "part_of_speech_obj": {"id": word.part_of_speech_obj.id, "name": word.part_of_speech_obj.name} if word.part_of_speech_obj else None,
                })
            elif r.item_type == "phrase":
                phrase = db.query(models.Phrase).get(r.item_id)
                if phrase is None:
                    continue
                meanings = []
                for m in phrase.meanings:
                    meanings.append({
                        "meaning": m.meaning,
                        "examples": [
                            {"example_text": ex.example_text} for ex in m.examples
                        ]
                    })
                if not meanings:
                    continue
                questions.append({
                    "item_type": "phrase",
                    "item_id": r.item_id,
                    "meanings": meanings
                })
        return {"questions": questions}
    else:
        study_set = db.query(models.UserStudySet).filter(models.UserStudySet.user_id == current_user.id).order_by(models.UserStudySet.created_at.desc()).first()
        if not study_set:
            return {"questions": []}
        reviewed_ids = set((r.item_type, r.item_id) for r in db.query(models.UserCardReview).filter_by(user_id=current_user.id, is_review=False))
        questions = []
        for wid in study_set.word_ids:
            if ("word", wid) not in reviewed_ids:
                word = db.query(models.Word).get(wid)
                if word is None:
                    continue
                meanings = []
                for m in word.meanings:
                    meanings.append({
                        "meaning": m.meaning,
                        "examples": [
                            {"example_text": ex.example_text} for ex in m.examples
                        ]
                    })
                if not meanings:
                    continue
                questions.append({
                    "item_type": "word",
                    "item_id": wid,
                    "meanings": meanings,
                    "part_of_speech": word.part_of_speech,
                    "part_of_speech_obj": {"id": word.part_of_speech_obj.id, "name": word.part_of_speech_obj.name} if word.part_of_speech_obj else None,
                })
                if len(questions) >= count:
                    break
        for pid in study_set.phrase_ids:
            if ("phrase", pid) not in reviewed_ids:
                phrase = db.query(models.Phrase).get(pid)
                if phrase is None:
                    continue
                meanings = []
                for m in phrase.meanings:
                    meanings.append({
                        "meaning": m.meaning,
                        "examples": [
                            {"example_text": ex.example_text} for ex in m.examples
                        ]
                    })
                if not meanings:
                    continue
                questions.append({
                    "item_type": "phrase",
                    "item_id": pid,
                    "meanings": meanings
                })
                if len(questions) >= count:
                    break
        return {"questions": questions}

async def submit_answer_service(data, db, current_user):
    if data.item_type == "word":
        item = db.query(models.Word).filter(models.Word.id == data.item_id).first()
        if not item:
            return None
        correct_answer = item.text
    else:
        item = db.query(models.Phrase).filter(models.Phrase.id == data.item_id).first()
        if not item:
            return None
        words = [db.query(models.Word).get(pc.word_id) for pc in sorted(item.components, key=lambda c: c.order)]
        correct_answer = " ".join([w.text for w in words if w and w.text])
    if not correct_answer:
        return None
    is_correct = data.answer.lower().strip() == correct_answer.lower().strip()
    error_analysis = None
    brief_explanation = None
    if not is_correct:
        try:
            analysis = await analyze_error_with_gemini(correct_answer, data.answer)
            error_analysis = analysis["error_analysis"]
            brief_explanation = analysis["brief_explanation"]
            error_record = models.UserAnswerError(
                user_id=current_user.id,
                item_type=data.item_type,
                item_id=data.item_id,
                correct_answer=correct_answer,
                user_answer=data.answer,
                error_analysis=error_analysis,
                brief_explanation=brief_explanation
            )
            db.add(error_record)
            db.commit()
        except Exception:
            pass
    attempt = models.UserCardReview(
        user_id=current_user.id,
        item_type=data.item_type,
        item_id=data.item_id,
        last_answer=data.answer,
        last_result=is_correct,
        is_review=False,
        card_json="{}",
        review_logs_json="[]"
    )
    db.add(attempt)
    db.commit()
    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "error_analysis": error_analysis,
        "brief_explanation": brief_explanation
    }

def rate_answer_service(data, db, current_user):
    if data.rating not in [1, 2, 3, 4]:
        return None
    scheduler = Scheduler()
    review = db.query(models.UserCardReview).filter_by(
        user_id=current_user.id,
        item_type=data.item_type,
        item_id=data.item_id,
        is_review=False
    ).first()
    if not review:
        return None
    if review.card_json and review.card_json != "{}":
        card = Card.from_dict(json.loads(review.card_json))
        review_logs = [ReviewLog.from_dict(log) for log in json.loads(review.review_logs_json)]
    else:
        card = Card()
        review_logs = []
    card, review_log = scheduler.review_card(card, Rating(data.rating))
    review_logs.append(review_log)
    review.card_json = json.dumps(card.to_dict())
    review.review_logs_json = json.dumps([log.to_dict() for log in review_logs])
    review.last_rating = data.rating
    review.last_result = (data.rating >= 3)
    db.commit()
    if not review.is_review and review.last_result:
        review.is_review = True
        db.commit()
    return review 