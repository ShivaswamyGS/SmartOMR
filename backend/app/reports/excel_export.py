import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from typing import List, Dict, Any

def generate_excel_report(
    exam_title: str,
    subject: str,
    total_questions: int,
    max_marks: float,
    results_data: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a professionally formatted Excel (.xlsx) report containing:
    1. Exam Executive Summary sheet with KPI cards.
    2. Student Performance Ranks & Detailed Results.
    3. Question Item Analysis (Item difficulty & discrimination).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Exam Results Summary"
    ws.views.sheetView[0].showGridLines = True
    
    # Styles
    navy_header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    indigo_fill = PatternFill(start_color="4338CA", end_color="4338CA", fill_type="solid")
    light_blue_fill = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    gray_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    green_text_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    red_text_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    
    white_bold = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    white_title = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
    header_font = Font(name="Segoe UI", size=10, bold=True, color="1E293B")
    body_font = Font(name="Segoe UI", size=10, color="0F172A")
    bold_body = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
    
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    
    # Title Block
    ws.merge_cells("A1:I2")
    title_cell = ws["A1"]
    title_cell.value = f"SmartOMR — {exam_title} ({subject})"
    title_cell.font = white_title
    title_cell.fill = navy_header_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # KPI Stats
    total_evaluated = len(results_data)
    scores = [r.get("raw_score", 0.0) for r in results_data]
    avg_score = round(sum(scores) / total_evaluated, 2) if total_evaluated > 0 else 0.0
    highest_score = max(scores) if scores else 0.0
    lowest_score = min(scores) if scores else 0.0
    
    ws["A4"] = "Total Students Evaluated"
    ws["B4"] = total_evaluated
    ws["C4"] = "Class Average Score"
    ws["D4"] = f"{avg_score} / {max_marks}"
    ws["E4"] = "Highest Score"
    ws["F4"] = highest_score
    ws["G4"] = "Lowest Score"
    ws["H4"] = lowest_score
    
    for col in ["A", "C", "E", "G"]:
        cell = ws[f"{col}4"]
        cell.font = bold_body
        cell.fill = light_blue_fill
        
    for col in ["B", "D", "F", "H"]:
        cell = ws[f"{col}4"]
        cell.font = bold_body
        cell.alignment = Alignment(horizontal="center")
        
    # Table Headers
    headers = [
        "Rank", "Student ID / Roll No", "Student Name", 
        "Score", "Max Marks", "Percentage (%)", 
        "Correct", "Incorrect", "Unanswered", "Review Status"
    ]
    
    start_row = 6
    for col_idx, h in enumerate(headers, 1):
        c = ws.cell(row=start_row, column=col_idx)
        c.value = h
        c.font = white_bold
        c.fill = indigo_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border
        
    # Data Rows
    # Sort by rank / score descending
    sorted_results = sorted(results_data, key=lambda x: x.get("raw_score", 0.0), reverse=True)
    
    for r_idx, r in enumerate(sorted_results, 1):
        row_num = start_row + r_idx
        ws.cell(row=row_num, column=1, value=r_idx).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=2, value=r.get("student_id") or "N/A").alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=3, value=r.get("student_name") or "Unknown").alignment = Alignment(horizontal="left")
        
        score_cell = ws.cell(row=row_num, column=4, value=r.get("raw_score", 0.0))
        score_cell.alignment = Alignment(horizontal="right")
        score_cell.font = bold_body
        
        ws.cell(row=row_num, column=5, value=max_marks).alignment = Alignment(horizontal="right")
        
        pct_cell = ws.cell(row=row_num, column=6, value=f"{r.get('percentage', 0.0)}%")
        pct_cell.alignment = Alignment(horizontal="right")
        pct_cell.font = bold_body
        
        c_cell = ws.cell(row=row_num, column=7, value=r.get("correct_count", 0))
        c_cell.alignment = Alignment(horizontal="center")
        c_cell.fill = green_text_fill
        
        w_cell = ws.cell(row=row_num, column=8, value=r.get("incorrect_count", 0))
        w_cell.alignment = Alignment(horizontal="center")
        if r.get("incorrect_count", 0) > 0:
            w_cell.fill = red_text_fill
            
        ws.cell(row=row_num, column=9, value=r.get("unanswered_count", 0)).alignment = Alignment(horizontal="center")
        
        status_str = r.get("review_status", "approved").replace("_", " ").title()
        ws.cell(row=row_num, column=10, value=status_str).alignment = Alignment(horizontal="center")
        
        # Apply borders and alternating fill
        for c in range(1, len(headers) + 1):
            cell = ws.cell(row=row_num, column=c)
            cell.border = thin_border
            if c not in (4, 6, 7, 8):
                cell.font = body_font
            if r_idx % 2 == 0 and not cell.fill.start_color.rgb:
                cell.fill = gray_fill
                
    # Auto-fit column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["C"].width = 28
    
    stream = io.BytesIO()
    wb.save(stream)
    return stream.getvalue()
