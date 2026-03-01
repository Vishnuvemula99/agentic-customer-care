from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_engine():
    """Create the SQLAlchemy engine."""
    settings = get_settings()
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # Required for SQLite
        echo=settings.environment == "development",
    )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables."""
    from app.db import models  # noqa: F401 - import to register models
    Base.metadata.create_all(bind=engine)
