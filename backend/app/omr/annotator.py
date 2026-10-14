import cv2
import numpy as np
import os
from typing import Dict, Any, Optional

def annotate_omr_sheet(
    canonical_bgr: np.ndarray,
    detected_answers: Dict[str, Any],
    answer_key: Dict[str, str],
    evaluation_result: Dict[str, Any],
    student_name: Optional[str] = None,
    student_id: Optional[str] = None,
    output_path: Optional[str] = None
) -> np.ndarray:
    """
    Overlays detected bubbles, correctness, and evaluation stats onto the OMR sheet.
    Colors (BGR):
    - Green (46, 204, 113): Correct marked bubble
    - Red (46, 46, 231): Incorrect marked bubble
    - Blue (235, 140, 52): Official correct answer bubble when missed
    - Amber (0, 165, 255): Ambiguous / Multi-mark flag
    """
    annotated = canonical_bgr.copy()
    
    # 1. Annotate each question's bubbles
    for q_str, q_info in detected_answers.items():
        coords = q_info.get("coords", {})
        detected = q_info.get("detected")
        is_multi = q_info.get("is_multi_mark", False)
        is_ambig = q_info.get("is_ambiguous", False)
        correct_key = answer_key.get(q_str)
        
        # Draw all option bubbles faintly or highlight relevant ones
        for opt_char, (cx, cy, r) in coords.items():
            if is_multi:
                # Flag multi-marked bubble
                fill_ratio = q_info.get("fill_ratios", {}).get(opt_char, 0.0)
                if fill_ratio >= 0.25:
                    cv2.circle(annotated, (cx, cy), r + 4, (0, 165, 255), 3) # Amber
            elif opt_char == detected:
                if correct_key and detected.upper() == correct_key.upper():
                    # Correct choice -> Green filled ring + check
                    cv2.circle(annotated, (cx, cy), r + 3, (46, 204, 113), 3)
                else:
                    # Incorrect choice -> Red ring
                    cv2.circle(annotated, (cx, cy), r + 3, (46, 46, 231), 3)
            elif opt_char == correct_key and (detected != correct_key):
                # Highlight what the correct answer was -> Blue/Cyan ring
                cv2.circle(annotated, (cx, cy), r + 3, (235, 140, 52), 2)
                
    # 2. Draw modern Header Evaluation Summary Card at the top banner
    # Draw semi-transparent card overlay
    card_y1, card_y2 = 140, 240
    card_x1, card_x2 = 140, 1460
    
    overlay = annotated.copy()
    cv2.rectangle(overlay, (card_x1, card_y1), (card_x2, card_y2), (245, 247, 250), -1)
    cv2.rectangle(overlay, (card_x1, card_y1), (card_x2, card_y2), (200, 205, 215), 2)
    cv2.addWeighted(overlay, 0.88, annotated, 0.12, 0, annotated)
    
    # Draw summary text
    name_display = student_name or "Unknown Student"
    id_display = student_id or "N/A"
    score_display = f"Score: {evaluation_result.get('raw_score', 0)} / {evaluation_result.get('max_marks', 50)} ({evaluation_result.get('percentage', 0)}%)"
    stat_display = f"Correct: {evaluation_result.get('correct_count', 0)}  |  Wrong: {evaluation_result.get('incorrect_count', 0)}  |  Unanswered: {evaluation_result.get('unanswered_count', 0)}"
    status_label = evaluation_result.get('review_status', 'evaluated').replace('_', ' ').title()
    
    cv2.putText(annotated, f"Student: {name_display} (ID: {id_display})", (card_x1 + 25, card_y1 + 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 41, 59), 2, cv2.LINE_AA)
                
    cv2.putText(annotated, score_display, (card_x1 + 25, card_y1 + 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (15, 23, 42), 2, cv2.LINE_AA)
                
    cv2.putText(annotated, stat_display, (card_x1 + 650, card_y1 + 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (71, 85, 105), 2, cv2.LINE_AA)
                
    # Status badge
    badge_color = (46, 204, 113) if "evaluated" in evaluation_result.get('review_status', '') and "warning" not in evaluation_result.get('review_status', '') else (0, 165, 255)
    cv2.putText(annotated, f"[{status_label}]", (card_x2 - 320, card_y1 + 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, badge_color, 2, cv2.LINE_AA)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, annotated)
        
    return annotated
