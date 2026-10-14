import io
import openpyxl
from fastapi.testclient import TestClient
from app.main import app, seed_demo_data
from app.reports.excel_export import generate_excel_report
from app.reports.csv_export import generate_csv_report
from app.reports.pdf_export import generate_pdf_summary_report

# Seed default database data for testing
seed_demo_data()
client = TestClient(app)

def test_health_and_root():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    
    root_res = client.get("/")
    assert root_res.status_code == 200

def test_auth_login_teacher():
    res = client.post("/api/auth/login", json={
        "email": "teacher@smartomr.com",
        "password": "teacher123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "teacher@smartomr.com"
    token = data["access_token"]
    
    # Test protected route
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "teacher@smartomr.com"

def test_excel_export_generation():
    results = [
        {"rank": 1, "student_id": "101", "student_name": "Student A", "raw_score": 48.0, "percentage": 96.0, "correct_count": 48, "incorrect_count": 1, "unanswered_count": 1, "review_status": "approved"},
        {"rank": 2, "student_id": "102", "student_name": "Student B", "raw_score": 42.5, "percentage": 85.0, "correct_count": 43, "incorrect_count": 2, "unanswered_count": 5, "review_status": "approved"}
    ]
    excel_bytes = generate_excel_report("Midterm Exam", "CS101", 50, 50.0, results)
    assert len(excel_bytes) > 1000
    
    # Verify openpyxl can parse the generated file
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    ws = wb.active
    assert "SmartOMR" in ws["A1"].value

def test_csv_export_generation():
    results = [
        {"student_id": "101", "student_name": "Alice", "roll_number": "101", "raw_score": 45.0, "percentage": 90.0, "accuracy": 95.0, "correct_count": 45, "incorrect_count": 2, "unanswered_count": 3, "multiple_marked_count": 0, "review_status": "approved"}
    ]
    csv_str = generate_csv_report(results, 50.0)
    assert "Alice" in csv_str
    assert "101" in csv_str

def test_pdf_export_generation():
    results = [
        {"rank": 1, "student_id": "101", "student_name": "Alice", "raw_score": 45.0, "percentage": 90.0, "accuracy": 95.0, "correct_count": 45, "incorrect_count": 2, "unanswered_count": 3, "review_status": "approved"}
    ]
    pdf_bytes = generate_pdf_summary_report("Midterm Exam", "CS101", 50, 50.0, results)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 2000

def test_dashboard_stats():
    login_res = client.post("/api/auth/login", json={
        "email": "teacher@smartomr.com",
        "password": "teacher123"
    })
    token = login_res.json()["access_token"]
    
    res = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_exams" in data
    assert "total_sheets_processed" in data
    assert "score_distribution" in data
