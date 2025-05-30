from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class PartOfSpeechResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    roles: List[str]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    roles: List[str]
    profile: Optional[dict]


class ProfileUpdate(BaseModel):
    is_public: Optional[bool]
    target_level: Optional[str]
    categories: Optional[List[int]]
    region: Optional[str]
    learning_speed: Optional[float]
    entry_test_result: Optional[dict]
    daily_minutes: Optional[int]
    desired_level: Optional[str]
    current_level: Optional[str]
    category_names: Optional[List[str]] = None


class WordBase(BaseModel):
    text: str
    gender: Optional[str] = None
    plural_form: Optional[str] = None
    verb_form2: Optional[str] = None
    verb_form3: Optional[str] = None


class WordCreate(WordBase):
    reflexivity: Optional[bool] = False
    case: Optional[str]
    part_of_speech: Optional[int] = None
    categories: Optional[List[int]] = None


class WordComponentMeaningResponse(BaseModel):
    id: int
    meaning: str

    class Config:
        orm_mode = True
        from_attributes = True


class WordComponentResponse(BaseModel):
    id: int
    type: str
    text: str
    meanings: List[WordComponentMeaningResponse]
    value_count: int

    class Config:
        orm_mode = True
        from_attributes = True


class WordMeaningExampleResponse(BaseModel):
    id: int
    example_text: str
    example_text_german: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True


class WordMeaningResponse(BaseModel):
    id: int
    meaning: str
    examples: list[WordMeaningExampleResponse] = []
    class Config:
        orm_mode = True
        from_attributes = True


class WordMeaningTranslationSchema(BaseModel):
    id: int
    class Config:
        orm_mode = True


class WordMeaningSchema(BaseModel):
    id: int
    translations: list[WordMeaningTranslationSchema] = []
    class Config:
        orm_mode = True


class WordSchema(BaseModel):
    id: int
    meanings: list[WordMeaningSchema] = []
    class Config:
        orm_mode = True


class WordResponse(BaseModel):
    id: int
    text: str
    reflexivity: Optional[bool]
    case: Optional[str]
    part_of_speech: Optional[int] = None
    part_of_speech_obj: Optional[PartOfSpeechResponse] = None
    categories: Optional[List[int]] = None
    category_names: Optional[List[str]] = None
    level: Optional[str] = None
    frequency: Optional[float] = None
    components: List[WordComponentResponse]
    component_count: int
    value_count: int
    meanings: list[WordMeaningResponse] = []
    gender: Optional[str] = None
    plural_form: Optional[str] = None
    verb_form2: Optional[str] = None
    verb_form3: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class WordComponentCreate(BaseModel):
    type: str  
    text: str
    order: int 
    meanings: List[str] = []


class PhraseCreate(BaseModel):
    words: List[int]  


class PhraseMeaningExampleResponse(BaseModel):
    id: int
    example_text: str
    example_text_german: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True


class PhraseMeaningResponse(BaseModel):
    id: int
    meaning: str
    examples: list[PhraseMeaningExampleResponse] = []
    class Config:
        orm_mode = True
        from_attributes = True


class PhraseResponse(BaseModel):
    id: int
    categories: Optional[List[int]] = None
    category_names: Optional[List[str]] = None
    level: Optional[str] = None
    frequency: Optional[float] = None
    words: List[WordResponse]
    labels: List[str]
    word_count: int
    value_count: int
    meanings: list[PhraseMeaningResponse] = []

    class Config:
        orm_mode = True
        from_attributes = True


class PhraseLabelCreate(BaseModel):
    name: str


class PhraseLabelResponse(BaseModel):
    id: int
    name: str


class PhraseDetailResponse(PhraseResponse):
    translations: List[str]  
    components: List[str]  


class UserPhraseNoteCreate(BaseModel):
    note: str
    flag: Optional[str]


class UserPhraseNoteResponse(BaseModel):
    id: int
    user_id: int
    phrase_id: int
    note: str
    flag: Optional[str]


class SemanticGroupBase(BaseModel):
    name: str
    word_ids: Optional[List[int]] = []
    phrase_ids: Optional[List[int]] = []
    categories: Optional[List[int]] = None
    category_names: Optional[List[str]] = None
    level: Optional[str] = None
    frequency: Optional[float] = None
    explanation: Optional[str] = None
    difference_explanation: Optional[str] = None


class SemanticGroupCreate(SemanticGroupBase):
    pass


class SemanticGroupResponse(SemanticGroupBase):
    id: int
    words: List[WordResponse] = []
    phrases: List[PhraseResponse] = []
    class Config:
        orm_mode = True
        from_attributes = True


class UserStudySetCreate(BaseModel):
    word_ids: List[int]
    phrase_ids: List[int]


class UserStudySetResponse(BaseModel):
    id: int
    user_id: int
    word_ids: List[int]
    phrase_ids: List[int]
    semantic_group_ids: List[int]
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True


class UserCardReviewCreate(BaseModel):
    item_type: str
    item_id: int
    answer: str
    rating: int
    is_review: bool = False


class UserCardReviewResponse(BaseModel):
    id: int
    user_id: int
    item_type: str
    item_id: int
    last_rating: Optional[int]
    last_answer: Optional[str]
    last_result: Optional[bool]
    is_review: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class PartOfSpeechCreate(BaseModel):
    name: str


class WordMeaningExampleCreate(BaseModel):
    word_meaning_id: int
    example_text: str
    example_text_german: Optional[str] = None


class PhraseMeaningExampleCreate(BaseModel):
    phrase_meaning_id: int
    example_text: str
    example_text_german: Optional[str] = None


class WordMeaningCreate(BaseModel):
    meaning: str


class PhraseMeaningCreate(BaseModel):
    meaning: str


class Word(WordBase):
    id: int

    class Config:
        from_attributes = True


class UserAnswerErrorBase(BaseModel):
    item_type: str
    item_id: int
    correct_answer: str
    user_answer: str
    error_analysis: str
    brief_explanation: str


class UserAnswerErrorCreate(UserAnswerErrorBase):
    pass


class UserAnswerError(UserAnswerErrorBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingAnswerRequest(BaseModel):
    item_type: str
    item_id: int
    answer: str


class TrainingAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    error_analysis: Optional[str] = None
    brief_explanation: Optional[str] = None


class UserWordNoteCreate(BaseModel):
    note: str
    flag: Optional[str]


class UserWordNoteResponse(BaseModel):
    id: int
    user_id: int
    word_id: int
    note: str
    flag: Optional[str]

    class Config:
        from_attributes = True


class WordUpdate(BaseModel):
    text: Optional[str] = None
    gender: Optional[str] = None
    plural_form: Optional[str] = None
    verb_form2: Optional[str] = None
    verb_form3: Optional[str] = None
    reflexivity: Optional[bool] = None
    case: Optional[str] = None
    part_of_speech: Optional[int] = None
    categories: Optional[List[int]] = None
    level: Optional[str] = None
    frequency: Optional[float] = None
    


class SemanticGroupDetailResponse(BaseModel):
    id: int
    name: str
    categories: Optional[List[int]] = None
    category_names: Optional[List[str]] = None
    level: Optional[str] = None
    frequency: Optional[float] = None
    word_ids: List[int]
    phrase_ids: List[int]
    words: List[WordResponse]
    phrases: List[PhraseResponse]
    member_count: int
    explanation: Optional[str] = None
    difference_explanation: Optional[str] = None
    class Config:
        from_attributes = True


class PaginatedWordResponse(BaseModel):
    items: List[WordResponse]
    next_offset: Optional[int]
    total_count: int


class PaginatedPhraseResponse(BaseModel):
    items: List[PhraseResponse]
    next_offset: Optional[int]
    total_count: int


class PaginatedSemanticGroupResponse(BaseModel):
    items: List[SemanticGroupResponse]
    next_offset: Optional[int]
    total_count: int


class PaginatedUserAnswerErrorResponse(BaseModel):
    items: List[UserAnswerError]
    next_offset: Optional[int]
    total_count: int


class PaginatedWordComponentResponse(BaseModel):
    items: List[WordComponentResponse]
    next_offset: Optional[int]
    total_count: int


class TrainingRateAnswerRequest(BaseModel):
    item_type: str
    item_id: int
    rating: int
    is_review: bool  


class StudySetGenerateRequest(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    root: Optional[str] = None


class PhraseMeaningExampleUpdate(BaseModel):
    id: Optional[int] = None
    example_text: Optional[str] = None
    example_text_german: Optional[str] = None


class PhraseMeaningUpdate(BaseModel):
    id: Optional[int] = None
    meaning: Optional[str] = None
    examples: Optional[List[PhraseMeaningExampleUpdate]] = None


class PhraseUpdate(BaseModel):
    words: Optional[List[int]] = None
    categories: Optional[List[int]] = None
    category_names: Optional[List[str]] = None
    level: Optional[str] = None
    frequency: Optional[float] = None
    labels: Optional[List[str]] = None
    meanings: Optional[List[PhraseMeaningUpdate]] = None


class WordMeaningExampleUpdate(BaseModel):
    id: Optional[int] = None
    example_text: Optional[str] = None
    example_text_german: Optional[str] = None
