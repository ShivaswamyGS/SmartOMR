"""
OMR Templates Definition and Configuration Manager.
All templates define regions in normalized coordinates (0.0 to 1.0) relative to
the standard warped canvas (width: 1600, height: 2200).
"""

from typing import Dict, Any, List

def get_default_50q_template() -> Dict[str, Any]:
    """
    Standard 50-Question Template:
    - Canonical dimensions: 1600 x 2200 pixels
    - Corner fiducials at 4 corners
    - Roll number grid: 6 digits (columns), values 0 to 9 (rows)
    - Question grid: 2 columns of 25 questions each (Cols: 1-25, 26-50)
    - 4 options per question: A, B, C, D
    """
    return {
        "name": "Standard 50-Question Form (A-D)",
        "description": "50 MCQ questions across 2 columns with 6-digit bubbled Roll Number",
        "canvas_width": 1600,
        "canvas_height": 2200,
        "total_questions": 50,
        "options": ["A", "B", "C", "D"],
        "columns_count": 2,
        "questions_per_column": 25,
        "fiducials": {
            "top_left": {"x": 80, "y": 80, "size": 60},
            "top_right": {"x": 1520, "y": 80, "size": 60},
            "bottom_left": {"x": 80, "y": 2120, "size": 60},
            "bottom_right": {"x": 1520, "y": 2120, "size": 60},
        },
        "student_id": {
            "type": "bubble_grid",
            "digits_count": 6,
            "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            # Roll number grid bounds in canonical coordinates
            "start_x": 950,
            "start_y": 280,
            "col_gap": 50,
            "row_gap": 32,
            "bubble_radius": 14
        },
        "student_name_box": {
            "x1": 150,
            "y1": 280,
            "x2": 800,
            "y2": 420
        },
        "questions_layout": [
            {
                "column_index": 0,
                "start_q": 1,
                "end_q": 25,
                "start_x": 160,      # X coordinate of question number
                "first_bubble_x": 280, # X coordinate of 'A' bubble
                "option_gap": 68,     # Gap between A, B, C, D
                "start_y": 720,       # Y coordinate of Q1
                "row_gap": 54,        # Gap between Q1, Q2, etc.
                "bubble_radius": 15
            },
            {
                "column_index": 1,
                "start_q": 26,
                "end_q": 50,
                "start_x": 880,
                "first_bubble_x": 1000,
                "option_gap": 68,
                "start_y": 720,
                "row_gap": 54,
                "bubble_radius": 15
            }
        ]
    }

def get_default_20q_template() -> Dict[str, Any]:
    """Standard 20-Question Quick Quiz Template."""
    return {
        "name": "Quick Quiz 20-Question Form (A-D)",
        "description": "20 MCQ questions in 1 column with 4-digit bubbled Student ID",
        "canvas_width": 1600,
        "canvas_height": 2200,
        "total_questions": 20,
        "options": ["A", "B", "C", "D"],
        "columns_count": 1,
        "questions_per_column": 20,
        "fiducials": {
            "top_left": {"x": 80, "y": 80, "size": 60},
            "top_right": {"x": 1520, "y": 80, "size": 60},
            "bottom_left": {"x": 80, "y": 2120, "size": 60},
            "bottom_right": {"x": 1520, "y": 2120, "size": 60},
        },
        "student_id": {
            "type": "bubble_grid",
            "digits_count": 4,
            "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "start_x": 1050,
            "start_y": 300,
            "col_gap": 60,
            "row_gap": 36,
            "bubble_radius": 15
        },
        "student_name_box": {
            "x1": 150,
            "y1": 300,
            "x2": 850,
            "y2": 440
        },
        "questions_layout": [
            {
                "column_index": 0,
                "start_q": 1,
                "end_q": 20,
                "start_x": 420,
                "first_bubble_x": 580,
                "option_gap": 95,
                "start_y": 750,
                "row_gap": 65,
                "bubble_radius": 17
            }
        ]
    }

def get_default_100q_template() -> Dict[str, Any]:
    """Standard 100-Question Comprehensive Exam Template (4 Columns x 25 Qs)."""
    return {
        "name": "Comprehensive 100-Question Form (A-D)",
        "description": "100 MCQ questions across 4 columns with 6-digit Roll Number",
        "canvas_width": 1600,
        "canvas_height": 2200,
        "total_questions": 100,
        "options": ["A", "B", "C", "D"],
        "columns_count": 4,
        "questions_per_column": 25,
        "fiducials": {
            "top_left": {"x": 80, "y": 80, "size": 60},
            "top_right": {"x": 1520, "y": 80, "size": 60},
            "bottom_left": {"x": 80, "y": 2120, "size": 60},
            "bottom_right": {"x": 1520, "y": 2120, "size": 60},
        },
        "student_id": {
            "type": "bubble_grid",
            "digits_count": 6,
            "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "start_x": 1100,
            "start_y": 250,
            "col_gap": 42,
            "row_gap": 28,
            "bubble_radius": 12
        },
        "student_name_box": {
            "x1": 150,
            "y1": 250,
            "x2": 900,
            "y2": 380
        },
        "questions_layout": [
            {"column_index": 0, "start_q": 1, "end_q": 25, "start_x": 120, "first_bubble_x": 190, "option_gap": 42, "start_y": 680, "row_gap": 55, "bubble_radius": 13},
            {"column_index": 1, "start_q": 26, "end_q": 50, "start_x": 480, "first_bubble_x": 550, "option_gap": 42, "start_y": 680, "row_gap": 55, "bubble_radius": 13},
            {"column_index": 2, "start_q": 51, "end_q": 75, "start_x": 840, "first_bubble_x": 910, "option_gap": 42, "start_y": 680, "row_gap": 55, "bubble_radius": 13},
            {"column_index": 3, "start_q": 76, "end_q": 100, "start_x": 1200, "first_bubble_x": 1270, "option_gap": 42, "start_y": 680, "row_gap": 55, "bubble_radius": 13},
        ]
    }

def get_template_by_id_or_default(template_config: Dict[str, Any] = None) -> Dict[str, Any]:
    if template_config and isinstance(template_config, dict) and "questions_layout" in template_config:
        return template_config
    return get_default_50q_template()
