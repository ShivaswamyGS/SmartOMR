import os
import io
import zipfile
import hashlib
import shutil
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db, SessionLocal
from ..config import settings
from ..models import Exam, Batch, OMRSheet, EvaluationResult, RosterEntry, User, AuditLog
from ..security import get_current_user
from ..omr.preprocessor import preprocess_omr_sheet
from ..omr.detector import detect_answers
from ..omr.student_id_detector import resolve_student_identity
from ..omr.evaluator import evaluate_exam_submission
from ..omr.annotator import annotate_omr_sheet
from ..omr.sheet_generator import generate_filled_student_sheet
from ..omr.templates import get_template_by_id_or_default
from ..storage import storage

router = APIRouter(prefix="/exams", tags=["OMR Processing"])

def compute_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def process_single_sheet_core(sheet_id: int, db: Session):
    """
    Executes the complete CV pipeline on a single OMR sheet record:
    1. Preprocess & warp to canonical canvas
    2. Read Student ID & match roster
    3. Detect all question bubbles & calculate fill ratios
    4. Score against answer key
    5. Render annotated visual review sheet
    6. Persist result and status
    """
    sheet = db.query(OMRSheet).filter(OMRSheet.id == sheet_id).first()
    if not sheet:
        return
        
    exam = db.query(Exam).filter(Exam.id == sheet.exam_id).first()
    if not exam or not exam.answer_key:
        sheet.status = "failed"
        sheet.error_details = "Exam or answer key missing."
        db.commit()
        return

    template_cfg = get_template_by_id_or_default(exam.template.config_json if exam.template else None)
    
    # Build roster lookup dict {student_id: {"name": ..., "roll": ...}}
    roster_lookup = {}
    for r in exam.roster_entries:
        sid_raw = str(r.student_id).strip()
        info = {"name": r.student_name, "roll": r.roll_number}
        roster_lookup[sid_raw] = info
        roster_lookup[sid_raw.lstrip("0")] = info
        roster_lookup[sid_raw.zfill(6)] = info
        if r.roll_number:
            r_raw = str(r.roll_number).strip()
            roster_lookup[r_raw] = info
            roster_lookup[r_raw.lstrip("0")] = info
            roster_lookup[r_raw.zfill(6)] = info

    try:
        # Step 1: Preprocess, detect fiducials & warp using local path from storage
        local_input_path = storage.get_local_path_for_cv(sheet.original_file_path)
        canonical_bgr, thresh_img, align_conf = preprocess_omr_sheet(local_input_path)
        
        # Save canonical image via storage
        proc_img_name = f"proc_{sheet.id}_{os.path.basename(sheet.file_name)}.png"
        ret_proc, proc_enc = cv2.imencode(".png", canonical_bgr)
        if ret_proc:
            sheet.processed_image_path = storage.upload_file(proc_enc.tobytes(), proc_img_name, folder="processed")
        
        # Step 2: Resolve Student Identity
        sid, sname, roll, id_conf, id_review_req = resolve_student_identity(
            canonical_bgr, thresh_img, template_cfg, roster_lookup
        )
        sheet.student_id = sid
        sheet.student_name = sname
        sheet.roll_number = roll
        
        # Step 3: Detect answers
        detected_answers, answers_conf = detect_answers(canonical_bgr, thresh_img, template_cfg)
        sheet.detected_answers_json = detected_answers
        
        # Step 4: Evaluate against answer key
        overall_conf = round((align_conf * 0.3) + (id_conf * 0.3) + (answers_conf * 0.4), 3)
        sheet.confidence = overall_conf
        
        eval_metrics = evaluate_exam_submission(
            detected_answers=detected_answers,
            answer_key=exam.answer_key.answers,
            marks_per_correct=exam.marks_per_correct,
            negative_marks_per_incorrect=exam.negative_marks_per_incorrect,
            max_marks=exam.max_marks,
            custom_weights=exam.answer_key.custom_weights,
            identity_review_required=id_review_req,
            overall_confidence=overall_conf
        )
        
        # Step 5: Annotate sheet with visual feedback and save via storage
        annotated_name = f"annotated_{sheet.id}_{os.path.basename(sheet.file_name)}.png"
        annotated_bgr = annotate_omr_sheet(
            canonical_bgr=canonical_bgr,
            detected_answers=detected_answers,
            answer_key=exam.answer_key.answers,
            evaluation_result=eval_metrics,
            student_name=sname,
            student_id=sid
        )
        ret_ann, ann_enc = cv2.imencode(".png", annotated_bgr)
        if ret_ann:
            sheet.annotated_image_path = storage.upload_file(ann_enc.tobytes(), annotated_name, folder="annotated")
            
        sheet.status = eval_metrics["review_status"]
        
        # Step 6: Upsert EvaluationResult
        res = db.query(EvaluationResult).filter(EvaluationResult.sheet_id == sheet.id).first()
        if not res:
            res = EvaluationResult(
                sheet_id=sheet.id,
                exam_id=exam.id,
                student_id=sid,
                student_name=sname,
                roll_number=roll,
                total_questions=eval_metrics["total_questions"],
                correct_count=eval_metrics["correct_count"],
                incorrect_count=eval_metrics["incorrect_count"],
                unanswered_count=eval_metrics["unanswered_count"],
                multiple_marked_count=eval_metrics["multiple_marked_count"],
                raw_score=eval_metrics["raw_score"],
                percentage=eval_metrics["percentage"],
                accuracy=eval_metrics["accuracy"],
                review_status=eval_metrics["review_status"]
            )
            db.add(res)
        else:
            res.student_id = sid
            res.student_name = sname
            res.roll_number = roll
            res.correct_count = eval_metrics["correct_count"]
            res.incorrect_count = eval_metrics["incorrect_count"]
            res.unanswered_count = eval_metrics["unanswered_count"]
            res.multiple_marked_count = eval_metrics["multiple_marked_count"]
            res.raw_score = eval_metrics["raw_score"]
            res.percentage = eval_metrics["percentage"]
            res.accuracy = eval_metrics["accuracy"]
            res.review_status = eval_metrics["review_status"]
            
        db.commit()
    except Exception as e:
        sheet.status = "failed"
        sheet.error_details = str(e)
        db.commit()

def update_exam_ranks(exam_id: int, db: Session):
    """Calculates and updates ranks for all evaluated students in the exam."""
    results = db.query(EvaluationResult).filter(EvaluationResult.exam_id == exam_id).order_by(EvaluationResult.raw_score.desc()).all()
    for idx, r in enumerate(results, 1):
        r.rank = idx
    db.commit()

def run_batch_evaluation_task(batch_id: int):
    """Background task to process a batch of sheets."""
    db = SessionLocal()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            return
            
        batch.status = "processing"
        db.commit()
        
        sheets = db.query(OMRSheet).filter(OMRSheet.batch_id == batch_id).all()
        for s in sheets:
            process_single_sheet_core(s.id, db)
            batch.processed_files += 1
            if s.status in ["automatically_evaluated", "evaluated"]:
                batch.successful_count += 1
            elif s.status in ["evaluated_with_warnings", "awaiting_review", "needs_review"]:
                batch.review_count += 1
            else:
                batch.failed_count += 1
            db.commit()
            
        update_exam_ranks(batch.exam_id, db)
        batch.status = "completed"
        db.commit()
    finally:
        db.close()

@router.post("/{exam_id}/upload")
async def upload_omr_files(
    exam_id: int,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    auto_evaluate: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not exam.answer_key:
        raise HTTPException(status_code=400, detail="Please configure the Answer Key before uploading OMR sheets.")
        
    batch = Batch(
        exam_id=exam_id,
        batch_name=f"Batch {len(exam.batches) + 1} ({len(files)} files)",
        total_files=0,
        status="pending"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    extracted_sheets = []
    supported_extensions = {".png", ".jpg", ".jpeg", ".pdf"}
    
    for f in files:
        contents = await f.read()
        f_name = f.filename
        ext = os.path.splitext(f_name)[1].lower()
        
        # Check ZIP
        if ext == ".zip":
            zip_buffer = io.BytesIO(contents)
            with zipfile.ZipFile(zip_buffer, "r") as zf:
                for member in zf.namelist():
                    m_ext = os.path.splitext(member)[1].lower()
                    if m_ext in supported_extensions and not member.startswith("__MACOSX") and not member.startswith("/"):
                        member_bytes = zf.read(member)
                        f_hash = compute_file_hash(member_bytes)
                        
                        # Prevent duplicate file injection
                        existing = db.query(OMRSheet).filter(OMRSheet.exam_id == exam_id, OMRSheet.file_hash == f_hash).first()
                        if existing:
                            continue
                            
                        save_name = f"{batch.id}_{os.path.basename(member)}"
                        save_ref = storage.upload_file(member_bytes, save_name, folder="uploads")
                            
                        sheet = OMRSheet(
                            batch_id=batch.id,
                            exam_id=exam_id,
                            file_name=os.path.basename(member),
                            file_hash=f_hash,
                            original_file_path=save_ref,
                            status="needs_review"
                        )
                        db.add(sheet)
                        extracted_sheets.append(sheet)
        elif ext in supported_extensions:
            f_hash = compute_file_hash(contents)
            existing = db.query(OMRSheet).filter(OMRSheet.exam_id == exam_id, OMRSheet.file_hash == f_hash).first()
            if existing:
                continue
                
            save_name = f"{batch.id}_{f_name}"
            save_ref = storage.upload_file(contents, save_name, folder="uploads")
                
            sheet = OMRSheet(
                batch_id=batch.id,
                exam_id=exam_id,
                file_name=f_name,
                file_hash=f_hash,
                original_file_path=save_ref,
                status="needs_review"
            )
            db.add(sheet)
            extracted_sheets.append(sheet)

    db.commit()
    batch.total_files = len(extracted_sheets)
    db.commit()
    
    if auto_evaluate and extracted_sheets:
        background_tasks.add_task(run_batch_evaluation_task, batch.id)
        
    return {
        "batch_id": batch.id,
        "batch_name": batch.batch_name,
        "total_files": batch.total_files,
        "status": "processing" if auto_evaluate else "pending",
        "message": f"Successfully queued {batch.total_files} OMR sheets for evaluation."
    }

@router.post("/{exam_id}/generate-samples")
def generate_sample_omr_sheets_for_exam(
    exam_id: int,
    count: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates realistic synthetic student OMR sheets using the exam's answer key and roster.
    Allows instant one-click demonstration of bulk processing, bubble detection, and scoring.
    """
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not exam.answer_key:
        raise HTTPException(status_code=400, detail="Please save an Answer Key first.")
        
    template_cfg = get_template_by_id_or_default(exam.template.config_json if exam.template else None)
    key_answers = exam.answer_key.answers
    
    # Sample students pool
    sample_students = [
        ("10101", "Alex Johnson"),
        ("10102", "Sophia Martinez"),
        ("10103", "Liam Chen"),
        ("10104", "Emma Davis"),
        ("10105", "Noah Patel"),
        ("10106", "Olivia Wilson"),
        ("10107", "Ethan Brown"),
        ("10108", "Ava Taylor"),
    ]
    
    batch = Batch(
        exam_id=exam_id,
        batch_name=f"Synthetic Demo Batch ({count} sheets)",
        total_files=count,
        status="processing"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    options = template_cfg.get("options", ["A", "B", "C", "D"])
    
    for i in range(min(count, len(sample_students))):
        sid, sname = sample_students[i]
        
        # Simulate varied accuracy (some high performers, some moderate, some with unanswered)
        accuracy_target = 0.95 - (i * 0.08)  # 95%, 87%, 79%, etc.
        student_answers = {}
        multi_mark_qs = []
        
        for q_str, correct_val in key_answers.items():
            q_num = int(q_str)
            import random
            rand_val = random.random()
            if rand_val < accuracy_target:
                student_answers[q_str] = correct_val
            elif rand_val < (accuracy_target + 0.15):
                # Pick a wrong option
                wrong_opts = [o for o in options if o != correct_val]
                student_answers[q_str] = random.choice(wrong_opts) if wrong_opts else correct_val
            else:
                # Leave unanswered
                student_answers[q_str] = None
                
        # For student 4, add a multiple-mark for realistic demo
        if i == 3:
            multi_mark_qs.append(5)
            
        sheet_img = generate_filled_student_sheet(
            student_id=sid,
            student_name=sname,
            chosen_answers=student_answers,
            template_config=template_cfg,
            exam_title=f"{exam.title} ({exam.subject})",
            multi_mark_questions=multi_mark_qs
        )
        
        save_filename = f"sample_{sid}_{sname.replace(' ', '_')}.png"
        ret_s, s_enc = cv2.imencode(".png", sheet_img)
        s_bytes = s_enc.tobytes() if ret_s else b""
        save_ref = storage.upload_file(s_bytes, f"{batch.id}_{save_filename}", folder="uploads")
        f_hash = compute_file_hash(s_bytes)
            
        sheet = OMRSheet(
            batch_id=batch.id,
            exam_id=exam_id,
            file_name=save_filename,
            file_hash=f_hash,
            original_file_path=save_ref,
            status="needs_review"
        )
        db.add(sheet)
        db.commit()
        db.refresh(sheet)
        
        # Process sheet immediately
        process_single_sheet_core(sheet.id, db)
        batch.processed_files += 1
        if sheet.status in ["automatically_evaluated", "evaluated"]:
            batch.successful_count += 1
        elif sheet.status in ["evaluated_with_warnings", "awaiting_review", "needs_review"]:
            batch.review_count += 1
        else:
            batch.failed_count += 1
        db.commit()

    update_exam_ranks(exam_id, db)
    batch.status = "completed"
    db.commit()
    
    return {
        "message": f"Successfully generated and evaluated {count} realistic student OMR sheets!",
        "batch_id": batch.id,
        "exam_id": exam_id
    }

@router.get("/batches/{batch_id}/status")
def get_batch_status(
    batch_id: int,
    db: Session = Depends(get_db)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    return {
        "batch_id": batch.id,
        "batch_name": batch.batch_name,
        "total_files": batch.total_files,
        "processed_files": batch.processed_files,
        "successful_count": batch.successful_count,
        "review_count": batch.review_count,
        "failed_count": batch.failed_count,
        "status": batch.status,
        "progress_percentage": round((batch.processed_files / max(1, batch.total_files)) * 100, 1)
    }
