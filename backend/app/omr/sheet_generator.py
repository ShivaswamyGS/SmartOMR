import os
import random
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
from .templates import get_default_50q_template

def generate_blank_omr_sheet(template_config: Optional[Dict[str, Any]] = None, exam_title: str = "SmartOMR Standard Assessment") -> np.ndarray:
    """
    Generates a crisp, printable, standard A4-proportioned blank OMR sheet (1600 x 2200).
    """
    if template_config is None:
        template_config = get_default_50q_template()
        
    w = template_config.get("canvas_width", 1600)
    h = template_config.get("canvas_height", 2200)
    
    # White background canvas
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    # 1. Draw 4 solid corner fiducials (60x60 square markers)
    fids = template_config.get("fiducials", {})
    for pos, info in fids.items():
        fx, fy, fsize = info["x"], info["y"], info["size"]
        half = fsize // 2
        cv2.rectangle(canvas, (fx - half, fy - half), (fx + half, fy + half), (0, 0, 0), -1)
        
    # 2. Header & Branding
    cv2.putText(canvas, "SmartOMR Assessment System", (200, 110), cv2.FONT_HERSHEY_DUPLEX, 1.1, (15, 23, 42), 2, cv2.LINE_AA)
    cv2.putText(canvas, exam_title, (200, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (71, 85, 105), 2, cv2.LINE_AA)
    
    # Instructions Box
    cv2.rectangle(canvas, (200, 175), (1400, 240), (220, 225, 230), 1)
    cv2.putText(canvas, "INSTRUCTIONS: Use Black/Blue Ballpoint Pen or HB Pencil. Completely darken the oval corresponding to your choice.", 
                (215, 202), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 41, 59), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Do not fold, tear or make stray marks on this sheet. Darken only ONE oval per question.", 
                (215, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 116, 139), 1, cv2.LINE_AA)
                
    # 3. Student Identification Section
    # Student Name and Signature Box
    name_box = template_config.get("student_name_box", {"x1": 150, "y1": 280, "x2": 850, "y2": 450})
    cv2.rectangle(canvas, (name_box["x1"], name_box["y1"]), (name_box["x2"], name_box["y2"]), (30, 41, 59), 2)
    cv2.putText(canvas, "STUDENT NAME (IN CAPITAL LETTERS):", (name_box["x1"] + 20, name_box["y1"] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 23, 42), 2, cv2.LINE_AA)
    # Dotted line for name
    cv2.line(canvas, (name_box["x1"] + 20, name_box["y1"] + 80), (name_box["x2"] - 20, name_box["y1"] + 80), (180, 180, 180), 2)
    
    cv2.putText(canvas, "CLASS / SECTION:", (name_box["x1"] + 20, name_box["y1"] + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 2, cv2.LINE_AA)
    cv2.putText(canvas, "SIGNATURE:", (name_box["x1"] + 400, name_box["y1"] + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 2, cv2.LINE_AA)
    
    # 4. Roll Number Bubble Grid
    st_cfg = template_config.get("student_id", {})
    if st_cfg.get("type") == "bubble_grid":
        digits_count = st_cfg.get("digits_count", 6)
        values = st_cfg.get("values", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        sx = st_cfg["start_x"]
        sy = st_cfg["start_y"]
        cgap = st_cfg["col_gap"]
        rgap = st_cfg["row_gap"]
        rad = st_cfg.get("bubble_radius", 14)
        
        # Grid title and border
        grid_w = digits_count * cgap + 40
        grid_h = len(values) * rgap + 80
        cv2.rectangle(canvas, (sx - 35, sy - 60), (sx + grid_w - 35, sy + grid_h - 60), (30, 41, 59), 2)
        cv2.putText(canvas, "ROLL NUMBER / STUDENT ID", (sx - 20, sy - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 23, 42), 2, cv2.LINE_AA)
        
        for c in range(digits_count):
            cx = sx + c * cgap
            # Draw digit write-in box at top
            cv2.rectangle(canvas, (cx - rad - 2, sy - 20), (cx + rad + 2, sy + 5), (100, 100, 100), 1)
            for r, val in enumerate(values):
                cy = sy + 30 + r * rgap
                cv2.circle(canvas, (cx, cy), rad, (40, 40, 40), 1, cv2.LINE_AA)
                cv2.putText(canvas, str(val), (cx - 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1, cv2.LINE_AA)
                
    # 5. Question Columns
    options_list = template_config.get("options", ["A", "B", "C", "D"])
    for layout in template_config.get("questions_layout", []):
        sq = layout["start_q"]
        eq = layout["end_q"]
        start_x = layout["start_x"]
        fb_x = layout["first_bubble_x"]
        ogap = layout["option_gap"]
        start_y = layout["start_y"]
        rgap = layout["row_gap"]
        rad = layout.get("bubble_radius", 15)
        
        # Draw Column Header
        col_w = len(options_list) * ogap + 100
        col_h = (eq - sq + 1) * rgap + 60
        cv2.rectangle(canvas, (start_x - 30, start_y - 65), (start_x + col_w, start_y + col_h - 40), (220, 226, 235), 1)
        cv2.rectangle(canvas, (start_x - 30, start_y - 65), (start_x + col_w, start_y - 20), (235, 240, 248), -1)
        cv2.putText(canvas, "Q.NO", (start_x - 15, start_y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 2, cv2.LINE_AA)
        
        for idx, opt in enumerate(options_list):
            bx = fb_x + idx * ogap
            cv2.putText(canvas, opt, (bx - 7, start_y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 23, 42), 2, cv2.LINE_AA)
            
        # Draw Question Rows
        for q in range(sq, eq + 1):
            row_idx = q - sq
            cy = start_y + row_idx * rgap
            
            # Question number
            q_text = f"{q:02d}" if q < 100 else str(q)
            cv2.putText(canvas, q_text, (start_x - 10, cy + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 2, cv2.LINE_AA)
            
            # Options
            for idx, opt in enumerate(options_list):
                bx = fb_x + idx * ogap
                cv2.circle(canvas, (bx, cy), rad, (40, 40, 40), 1, cv2.LINE_AA)
                cv2.putText(canvas, opt, (bx - 5, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 100), 1, cv2.LINE_AA)
                
    return canvas

def fill_bubble_realistically(
    image: np.ndarray, 
    cx: int, 
    cy: int, 
    radius: int, 
    quality: str = "clean"
) -> None:
    """
    Simulates a pencil or pen mark inside the bubble with slight natural noise.
    """
    if quality == "clean":
        fill_r = int(radius * 0.90)
        cv2.circle(image, (cx, cy), fill_r, (25, 25, 25), -1, cv2.LINE_AA)
    elif quality == "faint":
        fill_r = int(radius * 0.70)
        cv2.circle(image, (cx, cy), fill_r, (160, 160, 160), -1, cv2.LINE_AA)
    elif quality == "sloppy":
        # Slight offset and irregular stroke
        ox = random.randint(-3, 3)
        oy = random.randint(-3, 3)
        cv2.ellipse(image, (cx + ox, cy + oy), (int(radius * 0.95), int(radius * 0.85)), 
                    random.randint(0, 180), 0, 360, (30, 30, 30), -1, cv2.LINE_AA)

def generate_filled_student_sheet(
    student_id: str,
    student_name: str,
    chosen_answers: Dict[str, str],
    template_config: Optional[Dict[str, Any]] = None,
    exam_title: str = "SmartOMR Standard Assessment",
    multi_mark_questions: Optional[List[int]] = None
) -> np.ndarray:
    """
    Generates a realistic filled student OMR sheet with student info, bubbled ID,
    and filled answer choices.
    """
    if template_config is None:
        template_config = get_default_50q_template()
        
    sheet = generate_blank_omr_sheet(template_config, exam_title)
    
    # 1. Fill student name text
    name_box = template_config.get("student_name_box", {"x1": 150, "y1": 280, "x2": 850, "y2": 450})
    cv2.putText(sheet, student_name.upper(), (name_box["x1"] + 25, name_box["y1"] + 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2, cv2.LINE_AA)
                
    # 2. Fill bubbled student ID / Roll Number
    st_cfg = template_config.get("student_id", {})
    if st_cfg.get("type") == "bubble_grid":
        digits_count = st_cfg.get("digits_count", 6)
        values = st_cfg.get("values", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        sx = st_cfg["start_x"]
        sy = st_cfg["start_y"]
        cgap = st_cfg["col_gap"]
        rgap = st_cfg["row_gap"]
        rad = st_cfg.get("bubble_radius", 14)
        
        # Ensure student_id is padded to digits_count
        padded_id = student_id.zfill(digits_count)
        for c, digit_char in enumerate(padded_id[:digits_count]):
            if digit_char.isdigit():
                digit_val = int(digit_char)
                cx = sx + c * cgap
                # Write digit in top box
                cv2.putText(sheet, str(digit_val), (cx - 6, sy - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10, 10, 10), 2, cv2.LINE_AA)
                # Darken the matching bubble
                if digit_val in values:
                    r_idx = values.index(digit_val)
                    cy = sy + 30 + r_idx * rgap
                    fill_bubble_realistically(sheet, cx, cy, rad, "clean")
                    
    # 3. Fill answers
    options_list = template_config.get("options", ["A", "B", "C", "D"])
    multi_mark_questions = multi_mark_questions or []
    
    for layout in template_config.get("questions_layout", []):
        sq = layout["start_q"]
        eq = layout["end_q"]
        fb_x = layout["first_bubble_x"]
        ogap = layout["option_gap"]
        start_y = layout["start_y"]
        rgap = layout["row_gap"]
        rad = layout.get("bubble_radius", 15)
        
        for q in range(sq, eq + 1):
            row_idx = q - sq
            cy = start_y + row_idx * rgap
            q_key = str(q)
            
            target_opt = chosen_answers.get(q_key)
            if target_opt and target_opt in options_list:
                opt_idx = options_list.index(target_opt)
                cx = fb_x + opt_idx * ogap
                fill_bubble_realistically(sheet, cx, cy, rad, "clean")
                
            # Simulate multi-mark for test cases
            if q in multi_mark_questions:
                # Mark an extra option
                other_opts = [o for o in options_list if o != target_opt]
                if other_opts:
                    extra_opt = other_opts[0]
                    extra_idx = options_list.index(extra_opt)
                    extra_cx = fb_x + extra_idx * ogap
                    fill_bubble_realistically(sheet, extra_cx, cy, rad, "sloppy")
                    
    return sheet
