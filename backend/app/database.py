from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.models import Base  # re-exported so callers can do `from app.database import Base`

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://swingcheck:password@localhost:5432/swingcheck_db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
