"""
Database engine and session management using SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings

# SQLite connection with thread safety for multi-threaded streaming & dashboard access
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for obtaining database session in API routes and scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
