"""SQLAlchemy database engine, session, and base model setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from backend.app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_engine(database_url: str | None = None):
    """Create SQLAlchemy engine."""
    url = database_url or get_settings().database_url
    # For SQLite, we need check_same_thread=False
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args, echo=False)


def get_session_factory(engine=None) -> sessionmaker[Session]:
    """Create a session factory."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def create_tables(engine=None):
    """Create all database tables and safely add any new columns."""
    if engine is None:
        engine = get_engine()
    # Import models to register them with Base
    import backend.app.models.candidate  # noqa: F401
    import backend.app.models.interview  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Safe lightweight SQLite column migrations for new features
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check interview_sessions.is_completed_early
            try:
                conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN is_completed_early INTEGER DEFAULT 0"))
                conn.commit()
            except Exception:
                pass

            # Check questions.section & provenance columns
            for col, col_type in [
                ("section", "VARCHAR DEFAULT 'Technical Concepts'"),
                ("source_type", "VARCHAR DEFAULT 'general_rag'"),
                ("resume_section", "VARCHAR DEFAULT 'General Technical'"),
                ("source_item", "TEXT DEFAULT ''"),
                ("source_signals_json", "TEXT DEFAULT '[]'"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE questions ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass

            # Check interview_reports.is_completed_early, questions_answered, coverage_summary_json
            for col, col_type in [
                ("is_completed_early", "INTEGER DEFAULT 0"),
                ("questions_answered", "INTEGER DEFAULT 0"),
                ("coverage_summary_json", "TEXT DEFAULT '{}'"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE interview_reports ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass
    except Exception:
        pass


def get_db():
    """Dependency that yields a database session."""
    engine = get_engine()
    SessionLocal = get_session_factory(engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
