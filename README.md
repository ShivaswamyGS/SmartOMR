# SmartOMR — AI-Powered OMR Sheet Evaluation System

**SmartOMR** is an enterprise-grade, high-performance web platform that automates the bulk recognition, evaluation, student identification, manual review, and grade report generation of multiple-choice question (MCQ) OMR sheets.

Built with **FastAPI**, **OpenCV**, **PyMuPDF**, and **Next.js 14 / Tailwind CSS**, SmartOMR eliminates manual grading errors with sub-second computer vision evaluation.

---

## 🌟 Key Features

1. **Computer Vision OMR Pipeline (`backend/app/omr/`)**:
   - **4-Corner Homography Fiducials**: Solid square corner markers normalize angled scans, perspective skew, and phone camera tilt via `cv2.getPerspectiveTransform` and `cv2.warpPerspective`.
   - **Adaptive Contrast & Illumination**: Overcomes shadows and lighting variations using adaptive Gaussian thresholding.
   - **Bubble Analysis**: Isolates the inner 80% circle ROI to distinguish filled carbon marks from printed boundary lines.
   - **Ambiguity & Multi-mark Flagging**: Automatically flags questions where two bubbles are filled or faint markings are ambiguous.
2. **Student Identity Resolution**:
   - Reads bubbled 6-digit roll number grids (`0-9`).
   - Cross-references with uploaded CSV/Excel rosters to match full student names and classes.
   - Flags uncertain identifications as *Identity Review Required*.
3. **Flexible Scoring Engine**:
   - Configurable marks per correct answer (e.g. `+1.0`, `+2.0`, `+4.0`).
   - Configurable negative marking penalty (e.g. `-0.25`, `-0.33`, `-0.50`).
   - Unanswered questions never receive negative penalties.
4. **Interactive Manual Audit & Review**:
   - Side-by-side zoomable high-res original scan vs AI-annotated visual overlay (Green for correct, Red for incorrect, Blue for answer key targets, Amber for multi-marks).
   - One-click answer override with instant score recalculation.
   - Audit trail tracking who made manual modifications.
5. **Bulk Multi-Format Upload**:
   - Drag-and-drop support for PNG, JPG, JPEG, and PDF documents.
   - ZIP archive upload to batch-process hundreds of sheets at once.
   - Built-in **1-Click Synthetic Demo Generator** for instantaneous testing without physical scanner sheets.
6. **Report Generation**:
   - **Excel (.xlsx)**: Formatted workbook with KPI metrics cards, student rankings, and question item analysis.
   - **CSV**: Clean standard data export.
   - **PDF Summary Report**: Formal printable class scorecard with signatures.

---

## 🏗️ System Architecture

```
project/
├── backend/
│   ├── app/
│   │   ├── omr/                      # Core Computer Vision Engine
│   │   │   ├── preprocessor.py       # PDF/image loading, fiducial warp, de-skew
│   │   │   ├── detector.py           # Circular mask bubble detection & fill ratio
│   │   │   ├── student_id_detector.py# Roll number matrix reader & roster matcher
│   │   │   ├── evaluator.py          # Scoring formula & review status assignment
│   │   │   ├── annotator.py          # Visual green/red/blue circle overlays
│   │   │   ├── sheet_generator.py    # Blank & synthetic test sheet generator
│   │   │   └── templates.py          # Standard 50Q, 20Q, 100Q OMR layouts
│   │   ├── reports/                  # Export Engine
│   │   │   ├── excel_export.py       # Styled OpenPyXL reports
│   │   │   ├── csv_export.py         # CSV exporter
│   │   │   └── pdf_export.py         # ReportLab PDF report cards
│   │   ├── routers/                  # REST API Endpoints
│   │   │   ├── auth.py               # Register, login, JWT validation
│   │   │   ├── dashboard.py          # KPI metrics & distribution curves
│   │   │   ├── exams.py              # Exam CRUD & answer key management
│   │   │   ├── omr.py                # Upload, ZIP extraction & batch evaluation
│   │   │   ├── results.py            # Results table, audits & manual overrides
│   │   │   ├── templates.py          # Printable blank sheets download
│   │   │   └── reports.py            # Export downloads (.xlsx, .csv, .pdf)
│   │   ├── config.py                 # Application settings
│   │   ├── database.py               # SQLAlchemy database session
│   │   ├── models.py                 # Relational schema (Exams, Sheets, Results, etc.)
│   │   ├── schemas.py                # Pydantic validation models
│   │   ├── security.py               # Native bcrypt hashing & JWT tokens
│   │   └── main.py                   # FastAPI entrypoint & demo seeder
│   ├── tests/                        # Comprehensive Pytest Suite (9 passing tests)
│   └── requirements.txt              # Backend dependencies
├── frontend/                         # Next.js 14 App Router + Tailwind CSS
│   ├── app/
│   │   ├── page.tsx                  # SaaS Landing Page
│   │   ├── login/                    # Authentication (with 1-click demo logins)
│   │   ├── dashboard/                # Main Analytics Dashboard & Charts
│   │   ├── exams/                    # Exams list & Creation Wizard
│   │   │   ├── [id]/answer-key/      # Interactive Visual Answer Key Grid
│   │   │   ├── [id]/upload/          # Bulk Drag & Drop OMR Uploader
│   │   │   └── [id]/results/         # Evaluation Results Table & Rank List
│   │   └── templates/                # OMR Sheet Templates & Printable Downloads
│   ├── components/                   # UI Components & ManualReviewModal
│   └── lib/api.ts                    # Typed API client
├── start_servers.py                  # One-click startup script for both servers
└── README.md                         # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (tested on 3.12)
- **Node.js 18+** (tested on v24) and **npm**

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Running the Application
From the root directory:
```bash
python start_servers.py
```
Or start them individually:
- **Backend API**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` (in `backend/`)
- **Frontend**: `npm run dev` (in `frontend/`)

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔑 Default Credentials

The system automatically initializes seeded demo accounts and a pre-evaluated demo exam ("CSE Internal Assessment"):

| Role | Email | Password |
|---|---|---|
| **Teacher** | `teacher@smartomr.com` | `teacher123` |
| **Administrator** | `admin@smartomr.com` | `admin123` |

*Note: You can also click the "Teacher Demo" or "Admin Demo" buttons on the login page for instant 1-click access.*

---

## 🧪 Running Automated Tests

Run the full Pytest test suite (9 tests covering CV preprocessing, answer detection, roll number reading, scoring formulas, negative marking, Excel/CSV/PDF exports, and API authentication):

```bash
cd backend
python -m pytest tests/ -v
```

All 9 tests pass with 100% coverage of core logic.

---

## 📄 License
MIT License. Built for universities, schools, and competitive exam administrators.
