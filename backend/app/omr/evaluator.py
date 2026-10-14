from typing import Dict, Any, Tuple, Optional

def evaluate_exam_submission(
    detected_answers: Dict[str, Any],
    answer_key: Dict[str, str],
    marks_per_correct: float = 1.0,
    negative_marks_per_incorrect: float = 0.25,
    max_marks: float = 50.0,
    custom_weights: Optional[Dict[str, float]] = None,
    identity_review_required: bool = False,
    overall_confidence: float = 1.0
) -> Dict[str, Any]:
    """
    Evaluates detected answers against the official answer key using standard formula:
    Score = (Correct * marks_per_correct) - (Incorrect * negative_marks_per_incorrect)
    
    Returns evaluation metrics, question comparison breakdown, and status.
    """
    total_questions = len(answer_key)
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    multiple_marked_count = 0
    raw_score = 0.0
    
    has_ambiguity_warning = False
    
    question_breakdown: Dict[str, Any] = {}
    
    for q_str, key_val in answer_key.items():
        q_num = int(q_str)
        q_data = detected_answers.get(q_str, {})
        detected = q_data.get("detected")
        is_multi = q_data.get("is_multi_mark", False)
        is_ambig = q_data.get("is_ambiguous", False)
        is_unans = q_data.get("is_unanswered", False) or (detected is None)
        confidence = q_data.get("confidence", 1.0)
        
        weight = 1.0
        if custom_weights and q_str in custom_weights:
            weight = float(custom_weights[q_str])
            
        cur_correct_mark = marks_per_correct * weight
        cur_negative_mark = negative_marks_per_incorrect * weight
        
        status = "unanswered"
        mark_awarded = 0.0
        
        if is_multi:
            multiple_marked_count += 1
            incorrect_count += 1
            raw_score -= cur_negative_mark
            status = "multiple_marked"
            has_ambiguity_warning = True
        elif is_unans:
            unanswered_count += 1
            status = "unanswered"
            # Unanswered does not incur negative marks
            mark_awarded = 0.0
        else:
            if detected.upper() == key_val.upper():
                correct_count += 1
                raw_score += cur_correct_mark
                status = "correct"
                mark_awarded = cur_correct_mark
            else:
                incorrect_count += 1
                raw_score -= cur_negative_mark
                status = "incorrect"
                mark_awarded = -cur_negative_mark
                
        if is_ambig:
            has_ambiguity_warning = True
            
        question_breakdown[q_str] = {
            "question_number": q_num,
            "detected_answer": detected,
            "correct_answer": key_val,
            "status": status,
            "mark_awarded": round(mark_awarded, 2),
            "confidence": confidence,
            "is_multi_mark": is_multi,
            "is_ambiguous": is_ambig,
            "fill_ratios": q_data.get("fill_ratios", {})
        }
        
    raw_score = round(max(0.0, raw_score), 2)  # Floor at 0.0 or allow negative if configured
    percentage = round((raw_score / max(1.0, max_marks)) * 100.0, 2)
    attempted = correct_count + incorrect_count
    accuracy = round((correct_count / attempted * 100.0) if attempted > 0 else 0.0, 2)
    
    # Determine review status
    if identity_review_required:
        review_status = "awaiting_review"
    elif multiple_marked_count > 0 or has_ambiguity_warning or overall_confidence < 0.75:
        review_status = "evaluated_with_warnings"
    else:
        review_status = "automatically_evaluated"
        
    return {
        "total_questions": total_questions,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unanswered_count": unanswered_count,
        "multiple_marked_count": multiple_marked_count,
        "raw_score": raw_score,
        "max_marks": max_marks,
        "percentage": percentage,
        "accuracy": accuracy,
        "review_status": review_status,
        "question_breakdown": question_breakdown
    }
