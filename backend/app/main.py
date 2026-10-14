import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine, Base, SessionLocal
from .models import User, Exam, AnswerKey, RosterEntry, OMRTemplate
from .security import init_default_users
from .routers.templates import ensure_built_in_templates
from .routers import auth, dashboard, exams, templates, omr, results, reports

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SmartOMR — High-Performance AI-Powered OMR Sheet Evaluation System"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directories for image previews
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/annotated", StaticFiles(directory=settings.ANNOTATED_DIR), name="annotated")

# Include Routers under /api
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(exams.router, prefix=settings.API_V1_STR)
app.include_router(templates.router, prefix=settings.API_V1_STR)
app.include_router(omr.router, prefix=settings.API_V1_STR)
app.include_router(results.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

def seed_demo_data():
    """Initializes demo exam with answer key and realistic synthetic sheets."""
    db = SessionLocal()
    try:
        init_default_users(db)
        ensure_built_in_templates(db)
        
        teacher = db.query(User).filter(User.email == "teacher@smartomr.com").first()
        t50 = db.query(OMRTemplate).filter(OMRTemplate.total_questions == 50).first()
        
        # Check if demo exam exists
        demo_exam = db.query(Exam).filter(Exam.title == "CSE Internal Assessment").first()
        if not demo_exam and teacher and t50:
            demo_exam = Exam(
                user_id=teacher.id,
                template_id=t50.id,
                title="CSE Internal Assessment",
                subject="Data Structures & Algorithms",
                code="CS301-2026",
                total_questions=50,
                marks_per_correct=1.0,
                negative_marks_per_incorrect=0.25,
                max_marks=50.0,
                allow_partial_marking=False,
                status="active"
            )
            db.add(demo_exam)
            db.commit()
            db.refresh(demo_exam)
            
            # 50 Questions Answer Key
            pattern = ["A", "B", "C", "D"]
            answers = {str(i): pattern[(i * 3 + 1) % 4] for i in range(1, 51)}
            key = AnswerKey(
                exam_id=demo_exam.id,
                total_questions=50,
                answers=answers
            )
            db.add(key)
            
            # Roster
            sample_roster = [
                ("10101", "Alex Johnson", "10101", "alex@univ.edu", "CSE-A"),
                ("10102", "Sophia Martinez", "10102", "sophia@univ.edu", "CSE-A"),
                ("10103", "Liam Chen", "10103", "liam@univ.edu", "CSE-B"),
                ("10104", "Emma Davis", "10104", "emma@univ.edu", "CSE-B"),
                ("10105", "Noah Patel", "10105", "noah@univ.edu", "CSE-A"),
            ]
            for sid, sname, roll, mail, sec in sample_roster:
                db.add(RosterEntry(
                    exam_id=demo_exam.id,
                    student_id=sid,
                    student_name=sname,
                    roll_number=roll,
                    email=mail,
                    class_section=sec
                ))
            db.commit()
            
            # Generate sample sheets for instant evaluation
            from .routers.omr import generate_sample_omr_sheets_for_exam
            try:
                generate_sample_omr_sheets_for_exam(demo_exam.id, count=5, db=db, current_user=teacher)
            except Exception as e:
                print(f"Sample generation notice: {e}")
                
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    seed_demo_data()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to SmartOMR API",
        "docs": "/docs",
        "health": "/health"
    }
