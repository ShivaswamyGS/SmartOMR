from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import List, Optional, Dict, Any

from ..database import get_db
from ..models import EvaluationResult, OMRSheet, Exam, ManualCorrection, AuditLog, User
from ..schemas import (
    EvaluationResultResponse, 
    ManualCorrectionRequest, 
    IdentityCorrectionRequest
)
from ..security import get_current_user
from ..omr.evaluator import evaluate_exam_submission
from ..omr.annotator import annotate_omr_sheet
from ..storage import storage
import cv2
import os

router = APIRouter(tags=["Results and Manual Review"])

@router.get("/exams/{exam_id}/results")
def list_exam_results(
    exam_id: int,
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("rank", regex="^(rank|score|name|id)$"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$"),
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(EvaluationResult).filter(EvaluationResult.exam_id == exam_id)
    
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                EvaluationResult.student_name.ilike(search_fmt),
                EvaluationResult.student_id.ilike(search_fmt),
                EvaluationResult.roll_number.ilike(search_fmt)
            )
        )
        
    if status and status != "all":
        query = query.filter(EvaluationResult.review_status == status)
        
    # Sorting
    if sort_by == "score":
        order_col = EvaluationResult.raw_score
    elif sort_by == "name":
        order_col = EvaluationResult.student_name
    elif sort_by == "id":
        order_col = EvaluationResult.student_id
    else:
        order_col = EvaluationResult.rank
        
    if sort_dir == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))
        
    total_count = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    results_list = []
    for r in items:
        annotated_url = None
        if r.sheet and r.sheet.annotated_image_path:
            annotated_url = storage.get_public_url(r.sheet.annotated_image_path) or f"/api/results/{r.id}/annotated-image"

        results_list.append({
            "id": r.id,
            "sheet_id": r.sheet_id,
            "exam_id": r.exam_id,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "roll_number": r.roll_number,
            "total_questions": r.total_questions,
            "correct_count": r.correct_count,
            "incorrect_count": r.incorrect_count,
            "unanswered_count": r.unanswered_count,
            "multiple_marked_count": r.multiple_marked_count,
            "raw_score": r.raw_score,
            "percentage": r.percentage,
            "accuracy": r.accuracy,
            "rank": r.rank,
            "review_status": r.review_status,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
            "annotated_image_url": annotated_url
        })
        
    return {
        "items": results_list,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
    }

@router.get("/results/{result_id}")
def get_single_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Result not found")
        
    sheet = res.sheet
    exam = res.exam
    answer_key = exam.answer_key.answers if exam and exam.answer_key else {}
    
    # Calculate detailed question-by-question breakdown
    detected_answers = sheet.detected_answers_json or {}
    
    question_breakdown = []
    for q_num in range(1, exam.total_questions + 1):
        q_str = str(q_num)
        q_info = detected_answers.get(q_str, {})
        detected = q_info.get("detected")
        correct = answer_key.get(q_str)
        
        status = "unanswered"
        if q_info.get("is_multi_mark"):
            status = "multiple_marked"
        elif detected:
            if correct and detected.upper() == correct.upper():
                status = "correct"
            else:
                status = "incorrect"
                
        question_breakdown.append({
            "question_number": q_num,
            "detected_answer": detected,
            "correct_answer": correct,
            "status": status,
            "confidence": q_info.get("confidence", 1.0),
            "is_multi_mark": q_info.get("is_multi_mark", False),
            "is_ambiguous": q_info.get("is_ambiguous", False),
            "fill_ratios": q_info.get("fill_ratios", {})
        })
        
    corrections = [
        {
            "id": c.id,
            "question_number": c.question_number,
            "old_answer": c.old_answer,
            "new_answer": c.new_answer,
            "notes": c.notes,
            "corrected_by": c.corrected_by,
            "created_at": c.created_at.isoformat()
        } for c in res.corrections
    ]
        
    return {
        "id": res.id,
        "sheet_id": res.sheet_id,
        "exam_id": res.exam_id,
        "exam_title": exam.title,
        "exam_subject": exam.subject,
        "student_id": res.student_id,
        "student_name": res.student_name,
        "roll_number": res.roll_number,
        "total_questions": res.total_questions,
        "correct_count": res.correct_count,
        "incorrect_count": res.incorrect_count,
        "unanswered_count": res.unanswered_count,
        "multiple_marked_count": res.multiple_marked_count,
        "raw_score": res.raw_score,
        "max_marks": exam.max_marks,
        "percentage": res.percentage,
        "accuracy": res.accuracy,
        "rank": res.rank,
        "review_status": res.review_status,
        "file_name": sheet.file_name,
        "original_image_url": (storage.get_public_url(sheet.original_file_path) if sheet.original_file_path else None) or f"/api/results/{res.id}/original-image",
        "annotated_image_url": (storage.get_public_url(sheet.annotated_image_path) if sheet.annotated_image_path else None) or f"/api/results/{res.id}/annotated-image",
        "question_breakdown": question_breakdown,
        "corrections_history": corrections
    }

@router.put("/results/{result_id}/answers")
def manually_correct_answer(
    result_id: int,
    req: ManualCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Teacher overrides a detected bubble answer with instant recalculation.
    """
    res = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Result not found")
        
    sheet = res.sheet
    exam = res.exam
    q_str = str(req.question_number)
    
    detected_answers = dict(sheet.detected_answers_json or {})
    old_answer = detected_answers.get(q_str, {}).get("detected")
    
    # Update detected answers dict
    if q_str not in detected_answers:
        detected_answers[q_str] = {"question_number": req.question_number, "fill_ratios": {}, "coords": {}}
        
    detected_answers[q_str]["detected"] = req.new_answer
    detected_answers[q_str]["is_multi_mark"] = False
    detected_answers[q_str]["is_ambiguous"] = False
    detected_answers[q_str]["is_unanswered"] = (req.new_answer is None or req.new_answer == "")
    detected_answers[q_str]["confidence"] = 1.0
    sheet.detected_answers_json = detected_answers
    
    # Save manual correction record
    correction = ManualCorrection(
        result_id=res.id,
        question_number=req.question_number,
        old_answer=old_answer,
        new_answer=req.new_answer,
        notes=req.notes or f"Manual correction by {current_user.full_name}",
        corrected_by=current_user.full_name
    )
    db.add(correction)
    
    # Recalculate evaluation
    eval_metrics = evaluate_exam_submission(
        detected_answers=detected_answers,
        answer_key=exam.answer_key.answers,
        marks_per_correct=exam.marks_per_correct,
        negative_marks_per_incorrect=exam.negative_marks_per_incorrect,
        max_marks=exam.max_marks,
        custom_weights=exam.answer_key.custom_weights
    )
    
    res.correct_count = eval_metrics["correct_count"]
    res.incorrect_count = eval_metrics["incorrect_count"]
    res.unanswered_count = eval_metrics["unanswered_count"]
    res.multiple_marked_count = eval_metrics["multiple_marked_count"]
    res.raw_score = eval_metrics["raw_score"]
    res.percentage = eval_metrics["percentage"]
    res.accuracy = eval_metrics["accuracy"]
    res.review_status = "approved"  # Manual review approved by teacher
    sheet.status = "evaluated"
    
    # Update ranks
    db.commit()
    all_results = db.query(EvaluationResult).filter(EvaluationResult.exam_id == exam.id).order_by(EvaluationResult.raw_score.desc()).all()
    for idx, r in enumerate(all_results, 1):
        r.rank = idx
        
    # Re-render annotated image
    try:
        if sheet.processed_image_path:
            local_proc = storage.get_local_path_for_cv(sheet.processed_image_path)
            proc_bgr = cv2.imread(local_proc)
            if proc_bgr is not None:
                annotated_bgr = annotate_omr_sheet(
                    canonical_bgr=proc_bgr,
                    detected_answers=detected_answers,
                    answer_key=exam.answer_key.answers,
                    evaluation_result=eval_metrics,
                    student_name=res.student_name,
                    student_id=res.student_id
                )
                ret_ann, ann_enc = cv2.imencode(".png", annotated_bgr)
                if ret_ann:
                    ann_name = f"annotated_{sheet.id}_{os.path.basename(sheet.file_name)}.png"
                    sheet.annotated_image_path = storage.upload_file(
                        ann_enc.tobytes(), ann_name, folder="annotated"
                    )
    except Exception as e:
        print(f"[Warning] Error re-annotating: {e}")
        
    db.commit()
    return {"message": "Answer updated and score recalculated successfully", "result": res}

@router.put("/results/{result_id}/identity")
def manually_correct_identity(
    result_id: int,
    req: IdentityCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Result not found")
        
    sheet = res.sheet
    if req.student_id:
        res.student_id = req.student_id
        sheet.student_id = req.student_id
    if req.student_name:
        res.student_name = req.student_name
        sheet.student_name = req.student_name
    if req.roll_number:
        res.roll_number = req.roll_number
        sheet.roll_number = req.roll_number
        
    if res.review_status == "awaiting_review":
        res.review_status = "approved"
        sheet.status = "evaluated"
        
    db.commit()
    return {"message": "Student identity corrected successfully", "result": res}

@router.get("/results/{result_id}/original-image")
def get_original_image(result_id: int, db: Session = Depends(get_db)):
    from fastapi.responses import Response, RedirectResponse
    res = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not res or not res.sheet or not res.sheet.original_file_path:
        raise HTTPException(status_code=404, detail="Image file not found")
        
    pub_url = storage.get_public_url(res.sheet.original_file_path)
    if pub_url:
        return RedirectResponse(url=pub_url, status_code=307)
        
    try:
        file_bytes = storage.get_file_bytes(res.sheet.original_file_path)
        content_type = "image/png"
        fn = (res.sheet.file_name or "").lower()
        if fn.endswith(".jpg") or fn.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif fn.endswith(".pdf"):
            content_type = "application/pdf"
        return Response(content=file_bytes, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image could not be retrieved: {str(e)}")

@router.get("/results/{result_id}/annotated-image")
def get_annotated_image(result_id: int, db: Session = Depends(get_db)):
    from fastapi.responses import Response, RedirectResponse
    res = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not res or not res.sheet or not res.sheet.annotated_image_path:
        raise HTTPException(status_code=404, detail="Annotated image not found")
        
    pub_url = storage.get_public_url(res.sheet.annotated_image_path)
    if pub_url:
        return RedirectResponse(url=pub_url, status_code=307)
        
    try:
        file_bytes = storage.get_file_bytes(res.sheet.annotated_image_path)
        return Response(content=file_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Annotated image could not be retrieved: {str(e)}")
