import io
from typing import List, Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_summary_report(
    exam_title: str,
    subject: str,
    total_questions: int,
    max_marks: float,
    results_data: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a high-quality PDF summary report for the whole class.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )
    
    card_value_style = ParagraphStyle(
        'CardVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        alignment=1
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E293B'),
        alignment=0
    )
    
    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E293B'),
        alignment=1
    )

    story = []
    
    # Header Banner
    story.append(Paragraph("SmartOMR — Automated Evaluation System", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Official Exam Summary: <b>{exam_title}</b> | Subject: <b>{subject}</b>", subtitle_style))
    story.append(Spacer(1, 14))
    
    # KPI Stats
    total_evaluated = len(results_data)
    scores = [r.get("raw_score", 0.0) for r in results_data]
    avg_score = round(sum(scores) / total_evaluated, 2) if total_evaluated > 0 else 0.0
    highest_score = max(scores) if scores else 0.0
    lowest_score = min(scores) if scores else 0.0
    
    kpi_data = [
        [
            Paragraph("TOTAL STUDENTS", card_title_style),
            Paragraph("CLASS AVERAGE", card_title_style),
            Paragraph("HIGHEST SCORE", card_title_style),
            Paragraph("LOWEST SCORE", card_title_style),
        ],
        [
            Paragraph(f"{total_evaluated}", card_value_style),
            Paragraph(f"{avg_score} / {max_marks}", card_value_style),
            Paragraph(f"{highest_score}", card_value_style),
            Paragraph(f"{lowest_score}", card_value_style),
        ]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 16))
    
    # Results Table
    table_headers = [
        Paragraph("Rank", table_header_style),
        Paragraph("Student ID", table_header_style),
        Paragraph("Student Name", table_header_style),
        Paragraph("Correct", table_header_style),
        Paragraph("Wrong", table_header_style),
        Paragraph("Blank", table_header_style),
        Paragraph("Score", table_header_style),
        Paragraph("Pct", table_header_style),
        Paragraph("Status", table_header_style),
    ]
    
    rows = [table_headers]
    sorted_results = sorted(results_data, key=lambda x: x.get("raw_score", 0.0), reverse=True)
    
    for rank, r in enumerate(sorted_results, 1):
        status_lbl = r.get("review_status", "approved").replace("_", " ").title()
        rows.append([
            Paragraph(str(rank), table_cell_center),
            Paragraph(str(r.get("student_id") or "N/A"), table_cell_center),
            Paragraph(str(r.get("student_name") or "Unknown"), table_cell_style),
            Paragraph(str(r.get("correct_count", 0)), table_cell_center),
            Paragraph(str(r.get("incorrect_count", 0)), table_cell_center),
            Paragraph(str(r.get("unanswered_count", 0)), table_cell_center),
            Paragraph(f"<b>{r.get('raw_score', 0.0)}</b>", table_cell_center),
            Paragraph(f"{r.get('percentage', 0.0)}%", table_cell_center),
            Paragraph(status_lbl, table_cell_center),
        ])
        
    t = Table(rows, colWidths=[35, 65, 150, 45, 45, 45, 50, 45, 70], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#312E81')), # Indigo Header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 24))
    
    # Signature Footer
    sig_data = [
        ["", ""],
        ["Evaluated By: SmartOMR AI Engine", "Authorized Administrator / Teacher Signature"],
        ["Date: " + "Auto-generated", "_________________________________"]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#64748B')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(KeepTogether([sig_table]))
    
    doc.build(story)
    return buffer.getvalue()
