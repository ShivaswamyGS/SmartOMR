from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[str] = "teacher"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Template Schemas ---
class OMRTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    total_questions: int = 50
    options_per_question: int = 4
    columns_count: int = 2
    questions_per_column: int = 25
    config_json: Dict[str, Any]

class OMRTemplateCreate(OMRTemplateBase):
    pass

class OMRTemplateResponse(OMRTemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Exam Schemas ---
class ExamBase(BaseModel):
    title: str
    subject: str
    code: Optional[str] = None
    total_questions: int = 50
    marks_per_correct: float = 1.0
    negative_marks_per_incorrect: float = 0.25
    max_marks: float = 50.0
    allow_partial_marking: bool = False
    template_id: Optional[int] = None

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    code: Optional[str] = None
    total_questions: Optional[int] = None
    marks_per_correct: Optional[float] = None
    negative_marks_per_incorrect: Optional[float] = None
    max_marks: Optional[float] = None
    status: Optional[str] = None
    template_id: Optional[int] = None

class ExamResponse(ExamBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    has_answer_key: Optional[bool] = False
    total_submissions: Optional[int] = 0
    average_score: Optional[float] = 0.0

    class Config:
        from_attributes = True

# --- Answer Key Schemas ---
class AnswerKeyCreate(BaseModel):
    total_questions: int
    answers: Dict[str, str]  # e.g. {"1": "A", "2": "C"}
    custom_weights: Optional[Dict[str, float]] = None

class AnswerKeyResponse(BaseModel):
    id: int
    exam_id: int
    total_questions: int
    answers: Dict[str, str]
    custom_weights: Optional[Dict[str, float]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Roster Schemas ---
class RosterItem(BaseModel):
    student_id: str
    student_name: str
    roll_number: Optional[str] = None
    email: Optional[str] = None
    class_section: Optional[str] = None

class RosterBulkCreate(BaseModel):
    entries: List[RosterItem]

# --- Batch & OMR Schemas ---
class BatchResponse(BaseModel):
    id: int
    exam_id: int
    batch_name: str
    total_files: int
    processed_files: int
    successful_count: int
    review_count: int
    failed_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DetectedAnswerDetail(BaseModel):
    question_number: int
    detected: Optional[str] = None
    confidence: float
    is_multi_mark: bool = False
    is_ambiguous: bool = False
    is_unanswered: bool = False
    raw_fill_ratios: Dict[str, float]

class ManualCorrectionRequest(BaseModel):
    question_number: int
    new_answer: Optional[str] = None
    notes: Optional[str] = None

class IdentityCorrectionRequest(BaseModel):
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    roll_number: Optional[str] = None

class EvaluationResultResponse(BaseModel):
    id: int
    sheet_id: int
    exam_id: int
    student_id: Optional[str]
    student_name: Optional[str]
    roll_number: Optional[str]
    total_questions: int
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    multiple_marked_count: int
    raw_score: float
    percentage: float
    accuracy: float
    rank: Optional[int]
    review_status: str
    created_at: datetime
    updated_at: datetime
    annotated_image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    detected_answers: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_exams: int
    total_sheets_processed: int
    total_students_evaluated: int
    overall_average_score: float
    pending_reviews_count: int
    score_distribution: List[Dict[str, Any]]
    recent_exams: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
