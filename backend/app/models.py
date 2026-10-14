import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="teacher")  # admin, teacher
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    exams = relationship("Exam", back_populates="creator", cascade="all, delete-orphan")


class OMRTemplate(Base):
    __tablename__ = "omr_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    total_questions = Column(Integer, nullable=False, default=50)
    options_per_question = Column(Integer, nullable=False, default=4)  # 4 for A-D, 5 for A-E
    columns_count = Column(Integer, default=2)
    questions_per_column = Column(Integer, default=25)
    
    # JSON containing coordinate definitions, bubble spacing, roll number grid, fiducial markers
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    exams = relationship("Exam", back_populates="template")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("omr_templates.id"), nullable=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    code = Column(String(100), nullable=True)
    total_questions = Column(Integer, nullable=False, default=50)
    marks_per_correct = Column(Float, nullable=False, default=1.0)
    negative_marks_per_incorrect = Column(Float, nullable=False, default=0.25)
    max_marks = Column(Float, nullable=False, default=50.0)
    allow_partial_marking = Column(Boolean, default=False)
    status = Column(String(50), default="active")  # active, completed, archived
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    creator = relationship("User", back_populates="exams")
    template = relationship("OMRTemplate", back_populates="exams")
    answer_key = relationship("AnswerKey", back_populates="exam", uselist=False, cascade="all, delete-orphan")
    roster_entries = relationship("RosterEntry", back_populates="exam", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="exam", cascade="all, delete-orphan")
    omr_sheets = relationship("OMRSheet", back_populates="exam", cascade="all, delete-orphan")
    results = relationship("EvaluationResult", back_populates="exam", cascade="all, delete-orphan")


class AnswerKey(Base):
    __tablename__ = "answer_keys"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, unique=True)
    total_questions = Column(Integer, nullable=False)
    # Stored as JSON: {"1": "A", "2": "C", ...}
    answers = Column(JSON, nullable=False)
    # Stored as JSON question-specific weights: {"1": 1.0, ...} or empty for uniform
    custom_weights = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    exam = relationship("Exam", back_populates="answer_key")


class RosterEntry(Base):
    __tablename__ = "roster_entries"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(String(100), nullable=False)
    student_name = Column(String(255), nullable=False)
    roll_number = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    class_section = Column(String(100), nullable=True)

    exam = relationship("Exam", back_populates="roster_entries")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    batch_name = Column(String(255), nullable=False)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    successful_count = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    exam = relationship("Exam", back_populates="batches")
    sheets = relationship("OMRSheet", back_populates="batch", cascade="all, delete-orphan")


class OMRSheet(Base):
    __tablename__ = "omr_sheets"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)
    original_file_path = Column(String(500), nullable=False)
    processed_image_path = Column(String(500), nullable=True)
    annotated_image_path = Column(String(500), nullable=True)
    
    student_id = Column(String(100), nullable=True)
    student_name = Column(String(255), nullable=True)
    roll_number = Column(String(100), nullable=True)
    
    # evaluated, warning, needs_review, failed
    status = Column(String(50), default="needs_review")
    confidence = Column(Float, default=1.0)
    error_details = Column(Text, nullable=True)
    
    # JSON containing detailed detected answers, fill ratios, multi-marks
    detected_answers_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    exam = relationship("Exam", back_populates="omr_sheets")
    batch = relationship("Batch", back_populates="sheets")
    result = relationship("EvaluationResult", back_populates="sheet", uselist=False, cascade="all, delete-orphan")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(Integer, ForeignKey("omr_sheets.id"), nullable=False, unique=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    
    student_id = Column(String(100), nullable=True)
    student_name = Column(String(255), nullable=True)
    roll_number = Column(String(100), nullable=True)
    
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    unanswered_count = Column(Integer, default=0)
    multiple_marked_count = Column(Integer, default=0)
    
    raw_score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)
    
    # approved, flagged, edited, pending_review
    review_status = Column(String(50), default="approved")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sheet = relationship("OMRSheet", back_populates="result")
    exam = relationship("Exam", back_populates="results")
    corrections = relationship("ManualCorrection", back_populates="result", cascade="all, delete-orphan")


class ManualCorrection(Base):
    __tablename__ = "manual_corrections"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("evaluation_results.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    old_answer = Column(String(10), nullable=True)
    new_answer = Column(String(10), nullable=True)
    notes = Column(String(255), nullable=True)
    corrected_by = Column(String(100), default="teacher")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    result = relationship("EvaluationResult", back_populates="corrections")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
