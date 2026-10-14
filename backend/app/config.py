import os
from typing import List

class Settings:
    PROJECT_NAME: str = "SmartOMR"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smartomr_super_secret_production_key_change_in_prod_12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database Configuration: support SQLite locally & PostgreSQL on Supabase/Render
    raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./smartomr.db")
    # Normalize postgres:// prefix to postgresql:// for SQLAlchemy compatibility
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL: str = raw_db_url

    # Cloud Storage (Supabase Storage for persistent OMR scans & annotations)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_ANON_KEY", "")))
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "omr-sheets")

    # Local storage directories (used locally or as cache when Supabase is active)
    UPLOAD_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    ANNOTATED_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "annotated"))
    SAMPLES_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "samples"))
    
    # Public URLs
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

    # OMR Processing Defaults
    BUBBLE_FILLED_THRESHOLD: float = float(os.getenv("BUBBLE_FILLED_THRESHOLD", "0.32"))
    BUBBLE_EMPTY_THRESHOLD: float = float(os.getenv("BUBBLE_EMPTY_THRESHOLD", "0.15"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    AMBIGUOUS_DELTA_THRESHOLD: float = 0.08  # if diff between 1st & 2nd mark is < 0.08, flag ambiguous
    
    # Dynamic CORS Origins from environment (comma-separated)
    env_cors = os.getenv("CORS_ORIGINS", "")
    if env_cors:
        CORS_ORIGINS: List[str] = [origin.strip() for origin in env_cors.split(",") if origin.strip()]
    else:
        CORS_ORIGINS: List[str] = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "*"
        ]

settings = Settings()

# Ensure local directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.ANNOTATED_DIR, exist_ok=True)
os.makedirs(settings.SAMPLES_DIR, exist_ok=True)
