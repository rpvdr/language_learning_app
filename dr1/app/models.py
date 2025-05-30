from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import ARRAY


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    roles = relationship("UserRole", back_populates="user")
    profile = relationship("Profile", uselist=False, back_populates="user")
    answer_errors = relationship("UserAnswerError", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    user_roles = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    is_public = Column(Boolean, default=True)
    target_level = Column(String)
    categories = Column(ARRAY(Integer))  
    region = Column(String)
    learning_speed = Column(Float)
    entry_test_result = Column(JSON)
    daily_minutes = Column(Integer, nullable=True)  
    desired_level = Column(String, nullable=True)   
    current_level = Column(String, nullable=True)   
    user = relationship("User", back_populates="profile")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class PartOfSpeech(Base):
    __tablename__ = "parts_of_speech"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    gender = Column(String, nullable=True)  
    plural_form = Column(String, nullable=True)  
    verb_form2 = Column(String, nullable=True)  
    verb_form3 = Column(String, nullable=True)  
    reflexivity = Column(Boolean, default=False)
    case = Column(String)
    part_of_speech = Column(Integer, ForeignKey('parts_of_speech.id'), nullable=True)
    part_of_speech_obj = relationship("PartOfSpeech", foreign_keys=[part_of_speech])
    categories = Column(ARRAY(Integer), nullable=True)
    level = Column(String, nullable=True)
    frequency = Column(Float, nullable=True)
    components = relationship("WordComponentLink", back_populates="word")
    semantic_links = relationship("SemanticGroupLink", back_populates="word")
    meanings = relationship("WordMeaning", back_populates="word")

    @property
    def component_objs(self):
        return [link.component for link in self.components]

    @property
    def component_count(self):
        return len(self.components)

    @property
    def value_count(self):
        return len(self.meanings)


class WordComponent(Base):
    __tablename__ = "word_components"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  
    text = Column(String, nullable=False)
    links = relationship("WordComponentLink", back_populates="component")
    meanings = relationship("WordComponentMeaning", back_populates="component", cascade="all, delete-orphan")

    @property
    def component_objs(self):
        return [link.component for link in self.components]

    @property
    def component_count(self):
        return len(self.components)

    @property
    def value_count(self):
        return len(self.meanings)


class WordComponentLink(Base):
    __tablename__ = "word_component_links"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("word_components.id"), nullable=False)
    order = Column(Integer, nullable=False)
    word = relationship("Word", back_populates="components")
    component = relationship("WordComponent", back_populates="links")


class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    categories = Column(ARRAY(Integer), nullable=True) 
    level = Column(String, nullable=True)     
    frequency = Column(Float, nullable=True)  
    components = relationship("PhraseComponent", back_populates="phrase")
    labels = relationship("PhraseLabelLink", back_populates="phrase")
    semantic_links = relationship("SemanticGroupLink", back_populates="phrase")
    meanings = relationship("PhraseMeaning", backref="phrase", cascade="all, delete-orphan")

    @property
    def word_count(self):
        return len(self.components)

    @property
    def value_count(self):
        return len(self.meanings)


class PhraseComponent(Base):
    __tablename__ = "phrase_components"

    id = Column(Integer, primary_key=True, index=True)
    phrase_id = Column(Integer, ForeignKey("phrases.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    order = Column(Integer, nullable=False)
    phrase = relationship("Phrase", back_populates="components")
    word = relationship("Word")


class PhraseLabel(Base):
    __tablename__ = "phrase_labels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    links = relationship("PhraseLabelLink", back_populates="label")


class PhraseLabelLink(Base):
    __tablename__ = "phrase_label_links"

    id = Column(Integer, primary_key=True, index=True)
    phrase_id = Column(Integer, ForeignKey("phrases.id"), nullable=False)
    label_id = Column(Integer, ForeignKey("phrase_labels.id"), nullable=False)
    phrase = relationship("Phrase", back_populates="labels")
    label = relationship("PhraseLabel", back_populates="links")


class UserPhraseNote(Base):
    __tablename__ = "user_phrase_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phrase_id = Column(Integer, ForeignKey("phrases.id"), nullable=False)
    note = Column(String)
    flag = Column(String)  


class SemanticGroupLink(Base):
    __tablename__ = "semantic_group_links"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("semantic_groups.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=True)
    phrase_id = Column(Integer, ForeignKey("phrases.id"), nullable=True)
    word = relationship("Word", back_populates="semantic_links")
    phrase = relationship("Phrase", back_populates="semantic_links")
    group = relationship("SemanticGroup", back_populates="links")


class SemanticGroup(Base):
    __tablename__ = "semantic_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
   
    categories = Column(ARRAY(Integer), nullable=True)  
    level = Column(String, nullable=True)     
    frequency = Column(Float, nullable=True)  
    explanation = Column(String, nullable=True)  
    difference_explanation = Column(String, nullable=True)
    links = relationship("SemanticGroupLink", back_populates="group")

    @property
    def member_count(self):
        return len(self.links)


class WordComponentMeaning(Base):
    __tablename__ = "word_component_meanings"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("word_components.id"), nullable=False)
    meaning = Column(String, nullable=False)
    component = relationship("WordComponent", back_populates="meanings")


class UserStudySet(Base):
    __tablename__ = "user_study_sets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_ids = Column(ARRAY(Integer), nullable=False)
    phrase_ids = Column(ARRAY(Integer), nullable=False)
    semantic_group_ids = Column(ARRAY(Integer), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")


class UserCardReview(Base):
    __tablename__ = "user_card_reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String, nullable=False)  
    item_id = Column(Integer, nullable=False)
    card_json = Column(JSON, nullable=False)
    review_logs_json = Column(JSON, nullable=False)
    last_rating = Column(Integer, nullable=True)
    last_answer = Column(String, nullable=True)
    last_result = Column(Boolean, nullable=True)
    is_review = Column(Boolean, default=False) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WordMeaning(Base):
    __tablename__ = "word_meanings"
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    meaning = Column(String, nullable=False)
    examples = relationship("WordMeaningExample", back_populates="meaning", cascade="all, delete-orphan")
    word = relationship("Word", back_populates="meanings")
    translations = relationship("WordMeaningTranslation", back_populates="meaning")


class WordMeaningExample(Base):
    __tablename__ = "word_meaning_examples"
    id = Column(Integer, primary_key=True, index=True)
    word_meaning_id = Column(Integer, ForeignKey("word_meanings.id"), nullable=False)
    example_text = Column(String, nullable=False)
    example_text_german = Column(String, nullable=True)  
    meaning = relationship("WordMeaning", back_populates="examples")


class PhraseMeaning(Base):
    __tablename__ = "phrase_meanings"
    id = Column(Integer, primary_key=True, index=True)
    phrase_id = Column(Integer, ForeignKey("phrases.id"), nullable=False)
    meaning = Column(String, nullable=False)
    examples = relationship("PhraseMeaningExample", back_populates="meaning", cascade="all, delete-orphan")


class PhraseMeaningExample(Base):
    __tablename__ = "phrase_meaning_examples"
    id = Column(Integer, primary_key=True, index=True)
    phrase_meaning_id = Column(Integer, ForeignKey("phrase_meanings.id"), nullable=False)
    example_text = Column(String, nullable=False)
    example_text_german = Column(String, nullable=True) 
    meaning = relationship("PhraseMeaning", back_populates="examples")


class UserAnswerError(Base):
    __tablename__ = "user_answer_errors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_type = Column(String)  
    item_id = Column(Integer)  
    correct_answer = Column(String)
    user_answer = Column(String)
    error_analysis = Column(String)
    brief_explanation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="answer_errors")


class UserWordNote(Base):
    __tablename__ = "user_word_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    note = Column(String)
    flag = Column(String)  


class WordMeaningTranslation(Base):
    __tablename__ = "word_meaning_translations"
    id = Column(Integer, primary_key=True)
    meaning_id = Column(Integer, ForeignKey("word_meanings.id"))
    translation = Column(String, nullable=False)
    meaning = relationship("WordMeaning", back_populates="translations")


class SpecialUserStudySet(Base):
    __tablename__ = "special_user_study_sets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_ids = Column(ARRAY(Integer), nullable=False)
    phrase_ids = Column(ARRAY(Integer), nullable=False)
    semantic_group_ids = Column(ARRAY(Integer), nullable=False)
    root = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
