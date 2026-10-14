from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Exam, EvaluationResult, User
from ..security import get_current_user
from ..reports.excel_export import generate_excel_report
from ..reports.csv_export import generate_csv_report
from ..reports.pdf_export import generate_pdf_summary_report

router = APIRouter(prefix="/exams", tags=["Export Reports"])

@router.get("/{exam_id}/export")
def export_exam_results(
    exam_id: int,
    format: str = Query("xlsx", regex="^(xlsx|csv|pdf)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    results = db.query(EvaluationResult).filter(EvaluationResult.exam_id == exam_id).order_by(EvaluationResult.rank.asc()).all()
    
    results_data = [
        {
            "rank": r.rank or idx,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "roll_number": r.roll_number,
            "raw_score": r.raw_score,
            "percentage": r.percentage,
            "accuracy": r.accuracy,
            "correct_count": r.correct_count,
            "incorrect_count": r.incorrect_count,
            "unanswered_count": r.unanswered_count,
            "multiple_marked_count": r.multiple_marked_count,
            "review_status": r.review_status
        }
        for idx, r in enumerate(results, 1)
    ]
    
    clean_title = "".join(c for c in exam.title if c.isalnum() or c in (' ', '_', '-')).strip()
    
    if format == "xlsx":
        xlsx_bytes = generate_excel_report(
            exam_title=exam.title,
            subject=exam.subject,
            total_questions=exam.total_questions,
            max_marks=exam.max_marks,
            results_data=results_data
        )
        return Response(
            content=xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={clean_title}_results.xlsx"}
        )
    elif format == "csv":
        csv_str = generate_csv_report(results_data, max_marks=exam.max_marks)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={clean_title}_results.csv"}
        )
    elif format == "pdf":
        pdf_bytes = generate_pdf_summary_report(
            exam_title=exam.title,
            subject=exam.subject,
            total_questions=exam.total_questions,
            max_marks=exam.max_marks,
            results_data=results_data
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={clean_title}_report.pdf"}
        )
