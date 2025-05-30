from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import PartOfSpeech

def add_parts_of_speech():
    db = SessionLocal()
    try:
        parts_of_speech = [
            "noun", "verb", "adjective", "adverb", "pronoun",
            "preposition", "conjunction", "article", "numeral", "interjection"
        ]
        
        for pos in parts_of_speech:
            db_pos = PartOfSpeech(name=pos)
            db.add(db_pos)
        
        db.commit()
        print("Parts of speech added successfully!")
    except Exception as e:
        print(f"Error adding parts of speech: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_parts_of_speech() 