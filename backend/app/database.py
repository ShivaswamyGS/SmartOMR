from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL configuration optimized for Supabase transaction/session poolers
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,    # Verifies connection liveness before query execution
        pool_recycle=300,      # Recycles idle connections after 5 mins to prevent stale socket errors
        pool_size=5,          # Stays safely within Supabase free-tier connection limits
        max_overflow=10,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
