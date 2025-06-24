from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings # Adjusted import

# No need to create data directory here, FastAPI lifespan event in main.py handles it.

engine = create_engine(
    settings.DATABASE_URL,
    # connect_args are only for SQLite. For PostgreSQL, these are not needed and might cause issues.
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for declarative models will be imported from here by models.py
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
