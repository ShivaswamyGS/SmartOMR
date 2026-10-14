# SmartOMR — Production Deployment Guide (100% Free Tier)

This guide provides step-by-step instructions to deploy the **SmartOMR Evaluation System** completely free using:
- **Vercel** for the Next.js Frontend
- **Render** for the FastAPI Backend (Free Web Service)
- **Supabase** for PostgreSQL Database (`DATABASE_URL`)
- **Supabase Storage** for preserving uploaded OMR scans & annotated review sheets across backend restarts

---

## Architecture Overview

```
+-------------------------------------------------------------+
|                     Next.js Frontend                        |
|                    (Hosted on Vercel)                       |
+------------------------------+------------------------------+
                               |
                REST API calls | NEXT_PUBLIC_API_URL
                               v
+-------------------------------------------------------------+
|                     FastAPI Backend                         |
|                    (Hosted on Render)                       |
+---------------+-----------------------------+---------------+
                |                             |
      SQLAlchemy| Pooled Connections          | REST API / Signed URLs
                v                             v
+-------------------------------+  +--------------------------+
|      Supabase PostgreSQL      |  |     Supabase Storage     |
|          (Database)           |  |    (Bucket: omr-sheets)  |
+-------------------------------+  +--------------------------+
```

---

## Step 1: Set Up Supabase (Free Database & Storage)

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign in (or create a free account).
2. Click **New Project**.
3. Choose an organization, enter a name (e.g., `smartomr-prod`), set a secure **Database Password** (save this password!), and select the region closest to you.
4. Click **Create new project** and wait 1-2 minutes for provisioning.

### 1.2 Get PostgreSQL Connection String
1. In your Supabase project dashboard, navigate to **Project Settings** (gear icon) -> **Database**.
2. Scroll to **Connection string** and select the **URI** tab.
3. Switch from "Direct connection" to **"Transaction pooler"** (Port `6543`) or **"Session pooler"** (Port `5432`).
   - The connection string looks like:
     ```
     postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
     ```
4. Replace `[YOUR-PASSWORD]` with your actual database password. This is your `DATABASE_URL`.

### 1.3 Create the Storage Bucket for OMR Scans
1. In the Supabase left sidebar, click **Storage**.
2. Click **New Bucket**.
3. Set the bucket name to: `omr-sheets`
4. Toggle **Public bucket** to **ON** (this enables low-latency image delivery via Supabase's global CDN for student review scans and annotations).
5. Click **Save bucket**.

### 1.4 Get Supabase API URL and Key
1. Go to **Project Settings** -> **API**.
2. Copy the **Project URL** (e.g. `https://xxxx.supabase.co`). This is your `SUPABASE_URL`.
3. Under **Project API keys**, copy the `service_role` secret key (or the `anon` public key). This is your `SUPABASE_KEY`.

---

## Step 2: Push Your Code to GitHub

Ensure your project does not contain secrets or local database files. A production `.gitignore` is already provided at the repository root.

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit your changes
git commit -m "feat: prepare SmartOMR for Render, Vercel, and Supabase free deployment"

# Link to your GitHub repository
git remote add origin https://github.com/<your-username>/smartomr.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy FastAPI Backend on Render (Free Web Service)

### Method A: Automatic Deployment using Render Blueprint (`render.yaml`)
1. Log in to [render.com](https://render.com).
2. Click **New +** -> **Blueprint**.
3. Connect your `smartomr` GitHub repository.
4. Render will read `render.yaml` and discover the `smartomr-backend` service.
5. In the configuration prompt, enter your secret variables:
   - `DATABASE_URL`: Your Supabase PostgreSQL URI (from Step 1.2).
   - `SUPABASE_URL`: Your Supabase URL (from Step 1.4).
   - `SUPABASE_KEY`: Your Supabase key (from Step 1.4).
   - `CORS_ORIGINS`: Temporary value `*` (we will restrict this after deploying Vercel).
6. Click **Apply**.

### Method B: Manual Web Service Setup
1. On the Render Dashboard, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `smartomr-backend`
   - **Region**: Select the region closest to your Supabase database region.
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Expand **Advanced** and set:
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: `Yes`
5. Under **Environment Variables**, add:
   | Key | Value | Description |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.8` | Recommended stable Python version |
   | `SECRET_KEY` | *(Click "Generate" or use 64 hex chars)* | JWT signing key |
   | `DATABASE_URL` | `postgresql://postgres.[REF]:[PASS]@...:6543/postgres?sslmode=require` | Supabase DB connection string |
   | `SUPABASE_URL` | `https://[REF].supabase.co` | Supabase API endpoint |
   | `SUPABASE_KEY` | `eyJhbGciOi...` | Supabase service/anon key |
   | `SUPABASE_STORAGE_BUCKET` | `omr-sheets` | Object storage bucket name |
   | `CORS_ORIGINS` | `*` *(update after Step 4)* | Allowed frontend origins |
   | `BACKEND_URL` | `https://smartomr-backend.onrender.com` | Backend public URL |
6. Click **Create Web Service**.
7. Wait for the build to finish. Once live, test:
   `https://your-service-name.onrender.com/health` -> should return `{"status":"healthy",...}`.

---

## Step 4: Deploy Next.js Frontend on Vercel

1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository (`smartomr`).
4. In the configuration screen:
   - **Project Name**: `smartomr`
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click **Edit** and choose `frontend`.
5. Under **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://your-service-name.onrender.com` |
   *(Note: Do not include a trailing slash!)*
6. Click **Deploy**.
7. Vercel will build and deploy the Next.js app in ~1 minute. You will receive a URL such as:
   `https://smartomr-xxxx.vercel.app`

---

## Step 5: Lock Down CORS & Connect Frontend/Backend

1. Return to **Render** -> your `smartomr-backend` service -> **Environment**.
2. Update `CORS_ORIGINS` with your actual Vercel domain:
   ```
   CORS_ORIGINS=https://smartomr-xxxx.vercel.app,http://localhost:3000
   ```
3. Save changes. Render will redeploy automatically.

---

## Verification & Post-Deployment Testing Checklist

1. **Verify Backend Health**:
   Visit `https://smartomr-backend.onrender.com/health` in your browser. Expected:
   ```json
   {"status":"healthy","service":"SmartOMR","version":"1.0.0"}
   ```

2. **Verify Frontend UI**:
   Visit your Vercel URL `https://smartomr-xxxx.vercel.app`. The landing page should render with all styling and features.

3. **Log In with Pre-seeded Teacher Account**:
   - URL: `/login`
   - **Email**: `teacher@smartomr.com`
   - **Password**: `Teacher@123`
   *(Database auto-seeds this default teacher on first startup!)*

4. **Verify OMR Evaluation**:
   - Navigate to the pre-seeded exam **"CSE Internal Assessment"**.
   - Check the **Dashboard** and **Results** tab.
   - Click any student row to view the detailed question-by-question breakdown.
   - Click **Review Scan** to verify that the annotated OMR sheet preview loads from Supabase Storage.
   - Try a manual bubble override and verify that marks recalculate instantly.

5. **Test Report Exports**:
   - On the results page, click **Download Excel (.xlsx)**, **Download CSV**, and **Download PDF**.
   - Verify all generated files download correctly.

---

## Important Free-Tier Notes & Best Practices

1. **Render Free Tier Spin-Down**:
   - Free Web Services on Render automatically spin down (sleep) after 15 minutes of inactivity.
   - When a new request arrives, it may take 30-50 seconds to wake up ("cold start"). This is normal for Render's free tier.
   - The frontend gracefully handles loading indicators during API requests.

2. **Supabase Limits (Completely Free)**:
   - 500 MB PostgreSQL database storage (stores millions of OMR evaluations and answer keys).
   - 1 GB file storage (stores thousands of OMR scans and annotated review images).
   - 50,000 monthly active users for authentication.

3. **Connection Pooling**:
   - Supabase free tier has a pool limit of ~60 connections.
   - The backend is preconfigured with SQLAlchemy connection pooling:
     `pool_size=5`, `max_overflow=10`, `pool_recycle=300`, `pool_pre_ping=True`.
   - Always use the **Transaction Pooler** connection string (Port `6543`) in production.
