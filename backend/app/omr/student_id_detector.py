import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from .detector import extract_bubble_fill
from ..config import settings

def detect_bubbled_student_id(
    thresh_img: np.ndarray, 
    template_config: Dict[str, Any]
) -> Tuple[Optional[str], float, List[Dict[str, Any]]]:
    """
    Detects bubbled roll number/student ID from the bubbled matrix.
    
    Returns:
        (detected_id_string, confidence, debug_grid_data)
    """
    student_id_cfg = template_config.get("student_id", {})
    if not student_id_cfg or student_id_cfg.get("type") != "bubble_grid":
        return None, 0.0, []
        
    digits_count = student_id_cfg.get("digits_count", 6)
    values = student_id_cfg.get("values", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    start_x = student_id_cfg["start_x"]
    start_y = student_id_cfg["start_y"]
    col_gap = student_id_cfg["col_gap"]
    row_gap = student_id_cfg["row_gap"]
    radius = student_id_cfg.get("bubble_radius", 14)
    
    filled_thresh = settings.BUBBLE_FILLED_THRESHOLD
    empty_thresh = settings.BUBBLE_EMPTY_THRESHOLD
    
    detected_digits = []
    total_conf = 0.0
    debug_cols = []
    
    for col_idx in range(digits_count):
        cx = int(start_x + col_idx * col_gap)
        col_ratios = []
        
        for row_idx, val in enumerate(values):
            cy = int(start_y + 30 + row_idx * row_gap)
            fill = extract_bubble_fill(thresh_img, cx, cy, radius)
            col_ratios.append((val, fill, cx, cy))
            
        col_ratios.sort(key=lambda x: x[1], reverse=True)
        top_val, top_fill, top_cx, top_cy = col_ratios[0]
        runner_up_val, runner_up_fill = (col_ratios[1][0], col_ratios[1][1]) if len(col_ratios) > 1 else (None, 0.0)
        
        col_info = {
            "col_index": col_idx,
            "chosen_digit": None,
            "confidence": 0.0,
            "top_fill": round(top_fill, 4),
            "runner_up_fill": round(runner_up_fill, 4),
            "cx": top_cx,
            "cy": top_cy
        }
        
        if top_fill >= filled_thresh:
            if runner_up_fill >= filled_thresh or (top_fill - runner_up_fill) < 0.08:
                # Ambiguous or double bubbled
                col_info["chosen_digit"] = str(top_val)
                col_info["confidence"] = 0.5
                detected_digits.append(str(top_val))
                total_conf += 0.5
            else:
                col_info["chosen_digit"] = str(top_val)
                col_info["confidence"] = min(0.99, max(0.85, top_fill / 0.70))
                detected_digits.append(str(top_val))
                total_conf += col_info["confidence"]
        elif top_fill > empty_thresh:
            # Faint mark
            col_info["chosen_digit"] = str(top_val)
            col_info["confidence"] = 0.6
            detected_digits.append(str(top_val))
            total_conf += 0.6
        else:
            # Completely blank digit column
            col_info["chosen_digit"] = "?"
            col_info["confidence"] = 0.0
            detected_digits.append("?")
            total_conf += 0.0
            
        debug_cols.append(col_info)
        
    avg_conf = total_conf / digits_count if digits_count > 0 else 0.0
    detected_id = "".join(detected_digits)
    
    if "?" in detected_id or avg_conf < 0.65:
        return detected_id, round(avg_conf, 3), debug_cols
        
    return detected_id, round(avg_conf, 3), debug_cols

def detect_qr_or_barcode(canonical_bgr: np.ndarray) -> Optional[str]:
    """
    Attempts to read QR code or barcode from the canonical OMR sheet using OpenCV.
    """
    try:
        # Check for QR Code
        qr_detector = cv2.QRCodeDetector()
        val, pts, _ = qr_detector.detectAndDecode(canonical_bgr)
        if val and len(val.strip()) > 0:
            return val.strip()
    except Exception:
        pass
        
    try:
        # Check for 1D Barcode if OpenCV BarcodeDetector is available
        if hasattr(cv2, "barcode") and hasattr(cv2.barcode, "BarcodeDetector"):
            barcode_detector = cv2.barcode.BarcodeDetector()
            ret, decoded_info, decoded_type, points = barcode_detector.detectAndDecode(canonical_bgr)
            if ret and decoded_info and len(decoded_info) > 0 and decoded_info[0]:
                return decoded_info[0].strip()
    except Exception:
        pass
        
    return None

def resolve_student_identity(
    canonical_bgr: np.ndarray,
    thresh_img: np.ndarray,
    template_config: Dict[str, Any],
    roster_lookup: Optional[Dict[str, Dict[str, str]]] = None
) -> Tuple[Optional[str], Optional[str], Optional[str], float, bool]:
    """
    Comprehensive student identity resolution:
    1. Reads QR / Barcode if present.
    2. Reads bubbled student ID / roll number matrix.
    3. Cross-references with uploaded exam roster to obtain full student name and class.
    4. If unresolved or ambiguous, flags identity_review_required = True.
    
    Returns:
        (student_id, student_name, roll_number, confidence, review_required)
    """
    # 1. Check Barcode / QR Code
    code_val = detect_qr_or_barcode(canonical_bgr)
    if code_val:
        student_id = code_val
        roll_number = code_val
        student_name = None
        if roster_lookup and code_val in roster_lookup:
            student_name = roster_lookup[code_val].get("name")
        return student_id, student_name, roll_number, 0.99, False
        
    # 2. Check Bubbled Roll Number Grid
    detected_id, id_conf, _ = detect_bubbled_student_id(thresh_img, template_config)
    
    if detected_id and "?" not in detected_id and id_conf >= 0.70:
        student_id = detected_id
        roll_number = detected_id
        student_name = None
        
        # Check roster
        if roster_lookup:
            matched = roster_lookup.get(detected_id) or roster_lookup.get(detected_id.lstrip("0"))
            if matched:
                student_name = matched.get("name")
                return student_id, student_name, roll_number, id_conf, False
            
        # If roster exists but ID not in roster, flag for review
        if roster_lookup and len(roster_lookup) > 0:
            return student_id, f"Unregistered ({student_id})", roll_number, id_conf, True
            
        return student_id, f"Student {student_id}", roll_number, id_conf, False
        
    # If unreadable, partially missing, or low confidence
    partial_id = detected_id if detected_id else None
    return partial_id, "Identity Review Required", partial_id, id_conf, True
