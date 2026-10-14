import numpy as np
import cv2
from typing import Dict, Any, List, Tuple, Optional
from ..config import settings

def extract_bubble_fill(
    thresh_img: np.ndarray, 
    cx: int, 
    cy: int, 
    radius: int
) -> float:
    """
    Extracts the percentage of filled pixels inside the circle at (cx, cy)
    with the given radius, using an inner circular mask to avoid boundary edge noise.
    """
    h, w = thresh_img.shape
    inner_r = max(4, int(radius * 0.80)) # evaluate inner 80% to avoid circular outline
    
    y1 = max(0, cy - inner_r)
    y2 = min(h, cy + inner_r + 1)
    x1 = max(0, cx - inner_r)
    x2 = min(w, cx + inner_r + 1)
    
    if y2 <= y1 or x2 <= x1:
        return 0.0
        
    roi = thresh_img[y1:y2, x1:x2]
    
    # Generate circular mask
    mask = np.zeros(roi.shape, dtype=np.uint8)
    mask_cy = cy - y1
    mask_cx = cx - x1
    cv2.circle(mask, (mask_cx, mask_cy), inner_r, 255, -1)
    
    total_mask_pixels = cv2.countNonZero(mask)
    if total_mask_pixels == 0:
        return 0.0
        
    filled_pixels = cv2.countNonZero(cv2.bitwise_and(roi, roi, mask=mask))
    return float(filled_pixels) / float(total_mask_pixels)

def detect_answers(
    canonical_bgr: np.ndarray, 
    thresh_img: np.ndarray, 
    template_config: Dict[str, Any]
) -> Tuple[Dict[str, Any], float]:
    """
    Detects answers for all questions specified in the template.
    
    Returns:
        (detected_answers_dict, average_confidence)
    """
    options_list = template_config.get("options", ["A", "B", "C", "D"])
    layouts = template_config.get("questions_layout", [])
    
    detected_answers: Dict[str, Any] = {}
    total_confidence = 0.0
    questions_count = 0
    
    filled_thresh = settings.BUBBLE_FILLED_THRESHOLD
    empty_thresh = settings.BUBBLE_EMPTY_THRESHOLD
    ambig_delta = settings.AMBIGUOUS_DELTA_THRESHOLD

    for layout in layouts:
        start_q = layout["start_q"]
        end_q = layout["end_q"]
        first_bubble_x = layout["first_bubble_x"]
        option_gap = layout["option_gap"]
        start_y = layout["start_y"]
        row_gap = layout["row_gap"]
        bubble_radius = layout.get("bubble_radius", 15)
        
        for q_num in range(start_q, end_q + 1):
            row_idx = q_num - start_q
            cy = int(start_y + row_idx * row_gap)
            
            fill_ratios: Dict[str, float] = {}
            coords: Dict[str, Tuple[int, int, int]] = {}
            
            for opt_idx, opt_char in enumerate(options_list):
                cx = int(first_bubble_x + opt_idx * option_gap)
                ratio = extract_bubble_fill(thresh_img, cx, cy, bubble_radius)
                fill_ratios[opt_char] = round(ratio, 4)
                coords[opt_char] = (cx, cy, bubble_radius)
                
            # Sort options by fill ratio descending
            sorted_opts = sorted(fill_ratios.items(), key=lambda item: item[1], reverse=True)
            top_opt, top_ratio = sorted_opts[0]
            runner_up_opt, runner_up_ratio = sorted_opts[1] if len(sorted_opts) > 1 else (None, 0.0)
            
            is_unanswered = False
            is_multi_mark = False
            is_ambiguous = False
            detected_choice: Optional[str] = None
            q_conf = 1.0
            
            if top_ratio < empty_thresh:
                # None of the bubbles are filled
                is_unanswered = True
                detected_choice = None
                q_conf = max(0.85, 1.0 - (top_ratio / max(0.01, empty_thresh)))
            elif top_ratio >= filled_thresh:
                # Top bubble is filled. Check if runner-up is also filled or ambiguous
                if runner_up_ratio >= filled_thresh:
                    # Clear multi-mark
                    is_multi_mark = True
                    detected_choice = top_opt  # or None, flagged for review
                    q_conf = 0.40
                elif (top_ratio - runner_up_ratio) < ambig_delta:
                    # Ambiguous / close marking
                    is_ambiguous = True
                    detected_choice = top_opt
                    q_conf = 0.55
                else:
                    # Crisp, confident single mark
                    detected_choice = top_opt
                    q_conf = min(0.99, max(0.85, top_ratio / 0.70))
            else:
                # Faint marking between empty and filled thresholds
                is_ambiguous = True
                detected_choice = top_opt
                q_conf = 0.60
                
            detected_answers[str(q_num)] = {
                "question_number": q_num,
                "detected": detected_choice,
                "confidence": round(q_conf, 3),
                "is_multi_mark": is_multi_mark,
                "is_ambiguous": is_ambiguous,
                "is_unanswered": is_unanswered,
                "fill_ratios": fill_ratios,
                "coords": coords
            }
            
            total_confidence += q_conf
            questions_count += 1
            
    avg_conf = (total_confidence / questions_count) if questions_count > 0 else 1.0
    return detected_answers, round(avg_conf, 3)
