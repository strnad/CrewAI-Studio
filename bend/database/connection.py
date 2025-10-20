"""
Database Connection Management
Supports SQLite and PostgreSQL via SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bend.config import settings

# Check if using PostgreSQL for connection pooling settings
is_postgresql = settings.database_url.startswith("postgresql")

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10 if is_postgresql else 5,         # Connection pool size
    max_overflow=20 if is_postgresql else 10,     # Max overflow connections
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create Base class for ORM models
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Used with FastAPI Depends()

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db_session)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_connection():
    """
    Legacy compatibility with app/db_utils.py
    Returns raw connection for non-ORM operations
    """
    return engine.connect()


def init_db():
    """
    Initialize database - create all tables
    Called on application startup
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables - use with caution!
    For development/testing only
    """
    Base.metadata.drop_all(bind=engine)


# Alias for compatibility
get_db = get_db_session
