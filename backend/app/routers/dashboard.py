from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from ..database import get_db
from ..models import Exam, EvaluationResult, OMRSheet, User
from ..security import get_current_user
from ..schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total exams created by user (or all if admin)
    exam_query = db.query(Exam)
    if current_user.role != "admin":
        exam_query = exam_query.filter(Exam.user_id == current_user.id)
    exams = exam_query.all()
    exam_ids = [e.id for e in exams]
    
    total_exams = len(exams)
    
    total_sheets = 0
    total_results = 0
    pending_reviews = 0
    avg_score = 0.0
    
    recent_exams_data = []
    recent_activity_data = []
    score_buckets = {"0-20%": 0, "21-40%": 0, "41-60%": 0, "61-80%": 0, "81-100%": 0}
    
    if exam_ids:
        total_sheets = db.query(OMRSheet).filter(OMRSheet.exam_id.in_(exam_ids)).count()
        results = db.query(EvaluationResult).filter(EvaluationResult.exam_id.in_(exam_ids)).all()
        total_results = len(results)
        
        pending_reviews = db.query(OMRSheet).filter(
            OMRSheet.exam_id.in_(exam_ids),
            OMRSheet.status.in_(["needs_review", "warning"])
        ).count()
        
        if results:
            avg_score = round(sum(r.percentage for r in results) / total_results, 1)
            for r in results:
                pct = r.percentage
                if pct <= 20: score_buckets["0-20%"] += 1
                elif pct <= 40: score_buckets["21-40%"] += 1
                elif pct <= 60: score_buckets["41-60%"] += 1
                elif pct <= 80: score_buckets["61-80%"] += 1
                else: score_buckets["81-100%"] += 1
                
        # Recent exams
        for ex in sorted(exams, key=lambda x: x.created_at, reverse=True)[:5]:
            sub_count = db.query(EvaluationResult).filter(EvaluationResult.exam_id == ex.id).count()
            ex_results = db.query(EvaluationResult).filter(EvaluationResult.exam_id == ex.id).all()
            ex_avg = round(sum(r.raw_score for r in ex_results) / len(ex_results), 1) if ex_results else 0.0
            recent_exams_data.append({
                "id": ex.id,
                "title": ex.title,
                "subject": ex.subject,
                "total_questions": ex.total_questions,
                "max_marks": ex.max_marks,
                "total_submissions": sub_count,
                "average_score": ex_avg,
                "status": ex.status,
                "created_at": ex.created_at.isoformat()
            })
            
        # Recent sheet evaluations
        recent_sheets = db.query(OMRSheet).filter(OMRSheet.exam_id.in_(exam_ids)).order_by(OMRSheet.created_at.desc()).limit(6).all()
        for s in recent_sheets:
            recent_activity_data.append({
                "id": s.id,
                "exam_id": s.exam_id,
                "student_name": s.student_name or "Unknown",
                "roll_number": s.roll_number or "N/A",
                "file_name": s.file_name,
                "status": s.status,
                "score": s.result.raw_score if s.result else 0.0,
                "created_at": s.created_at.isoformat()
            })

    distribution_list = [{"range": k, "count": v} for k, v in score_buckets.items()]

    return {
        "total_exams": total_exams,
        "total_sheets_processed": total_sheets,
        "total_students_evaluated": total_results,
        "overall_average_score": avg_score,
        "pending_reviews_count": pending_reviews,
        "score_distribution": distribution_list,
        "recent_exams": recent_exams_data,
        "recent_activity": recent_activity_data
    }
