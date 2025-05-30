from sqlalchemy.orm import Session
from .. import models, schemas

def create_label_service(label: schemas.PhraseLabelCreate, db: Session):
    db_label = models.PhraseLabel(name=label.name)
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label

def get_labels_service(skip: int, limit: int, db: Session):
    labels = db.query(models.PhraseLabel).offset(skip).limit(limit).all()
    return labels
