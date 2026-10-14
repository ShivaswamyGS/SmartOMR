import pytest
import numpy as np
import cv2
import os

from app.omr.evaluator import evaluate_exam_submission
from app.omr.templates import get_default_50q_template, get_default_20q_template
from app.omr.sheet_generator import generate_blank_omr_sheet, generate_filled_student_sheet
from app.omr.detector import detect_answers, extract_bubble_fill
from app.omr.student_id_detector import detect_bubbled_student_id, resolve_student_identity
from app.omr.preprocessor import preprocess_omr_sheet

def test_scoring_formula_and_negative_marking():
    """Tests score calculation with correct, incorrect, and unanswered questions."""
    answer_key = {
        "1": "A", "2": "B", "3": "C", "4": "D", "5": "A",
        "6": "B", "7": "C", "8": "D", "9": "A", "10": "B"
    }
    
    # 7 Correct, 2 Incorrect, 1 Unanswered
    # Score = (7 * 1.0) - (2 * 0.25) = 7.0 - 0.5 = 6.5
    detected_answers = {
        "1": {"detected": "A", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "2": {"detected": "B", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "3": {"detected": "C", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "4": {"detected": "D", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "5": {"detected": "A", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "6": {"detected": "B", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "7": {"detected": "C", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95},
        "8": {"detected": "A", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95}, # WRONG (Key is D)
        "9": {"detected": "C", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95}, # WRONG (Key is A)
        "10": {"detected": None, "is_multi_mark": False, "is_unanswered": True, "confidence": 0.99}, # UNANSWERED
    }
    
    res = evaluate_exam_submission(
        detected_answers=detected_answers,
        answer_key=answer_key,
        marks_per_correct=1.0,
        negative_marks_per_incorrect=0.25,
        max_marks=10.0
    )
    
    assert res["correct_count"] == 7
    assert res["incorrect_count"] == 2
    assert res["unanswered_count"] == 1
    assert res["raw_score"] == 6.5
    assert res["percentage"] == 65.0
    assert res["accuracy"] == round(7 / 9 * 100, 2)
    assert res["review_status"] == "automatically_evaluated"

def test_multiple_marks_and_ambiguity_flagging():
    """Tests that multiple marked questions are penalized and flagged for review."""
    answer_key = {"1": "A", "2": "B"}
    detected_answers = {
        "1": {"detected": "A", "is_multi_mark": True, "is_unanswered": False, "confidence": 0.40},
        "2": {"detected": "B", "is_multi_mark": False, "is_unanswered": False, "confidence": 0.95}
    }
    
    res = evaluate_exam_submission(
        detected_answers=detected_answers,
        answer_key=answer_key,
        marks_per_correct=1.0,
        negative_marks_per_incorrect=0.25,
        max_marks=2.0
    )
    
    assert res["multiple_marked_count"] == 1
    assert res["incorrect_count"] == 1
    assert res["correct_count"] == 1
    assert res["raw_score"] == 0.75  # 1.0 - 0.25
    assert res["review_status"] == "evaluated_with_warnings"

def test_sheet_generation_and_end_to_end_cv_detection(tmp_path):
    """Generates a synthetic OMR sheet and verifies detection of student ID and answers."""
    template = get_default_50q_template()
    student_id = "104523"
    student_name = "Jane Doe"
    
    # Fill 10 questions for testing
    chosen_answers = {
        "1": "A", "2": "C", "3": "B", "4": "D", "5": "A",
        "6": "B", "7": "D", "8": "C", "9": "A", "10": "B"
    }
    
    sheet_bgr = generate_filled_student_sheet(
        student_id=student_id,
        student_name=student_name,
        chosen_answers=chosen_answers,
        template_config=template,
        exam_title="Test Exam"
    )
    
    test_img_path = str(tmp_path / "test_omr.png")
    cv2.imwrite(test_img_path, sheet_bgr)
    
    # Preprocess
    canonical_bgr, thresh, align_conf = preprocess_omr_sheet(test_img_path)
    assert canonical_bgr.shape == (2200, 1600, 3)
    assert align_conf >= 0.8
    
    # Student ID detection
    det_id, id_conf, _ = detect_bubbled_student_id(thresh, template)
    assert det_id == student_id
    assert id_conf >= 0.75
    
    # Answer detection
    answers, avg_conf = detect_answers(canonical_bgr, thresh, template)
    
    for q_num in range(1, 11):
        q_str = str(q_num)
        expected = chosen_answers[q_str]
        actual = answers[q_str]["detected"]
        assert actual == expected, f"Question {q_num}: expected {expected}, got {actual}"
