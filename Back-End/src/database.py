from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLModel engine (only if DATABASE_URL is available)
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
else:
    engine = None


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    if not engine:
        raise RuntimeError("Database not configured. Set DATABASE_URL in .env file.")
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


def create_db_and_tables():
    """Create all database tables"""
    if not engine:
        raise RuntimeError("Database not configured. Set DATABASE_URL in .env file.")
    SQLModel.metadata.create_all(engine)
