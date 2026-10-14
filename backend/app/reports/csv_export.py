import io
import csv
from typing import List, Dict, Any

def generate_csv_report(results_data: List[Dict[str, Any]], max_marks: float) -> str:
    """
    Generates standard comma-separated values (CSV) export for exam results.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "Rank", "Student ID", "Student Name", "Roll Number", 
        "Score", "Max Marks", "Percentage", "Accuracy", 
        "Correct Answers", "Incorrect Answers", "Unanswered Questions", 
        "Multiple Marked", "Review Status"
    ])
    
    # Sort results by score descending
    sorted_results = sorted(results_data, key=lambda x: x.get("raw_score", 0.0), reverse=True)
    
    for rank, r in enumerate(sorted_results, 1):
        writer.writerow([
            rank,
            r.get("student_id") or "",
            r.get("student_name") or "Unknown",
            r.get("roll_number") or "",
            r.get("raw_score", 0.0),
            max_marks,
            f"{r.get('percentage', 0.0)}%",
            f"{r.get('accuracy', 0.0)}%",
            r.get("correct_count", 0),
            r.get("incorrect_count", 0),
            r.get("unanswered_count", 0),
            r.get("multiple_marked_count", 0),
            r.get("review_status", "approved")
        ])
        
    return output.getvalue()
