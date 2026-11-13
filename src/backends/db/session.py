"""
SQLAlchemy engine, session factory, and base declarative class.

A single SQLite file is used. `check_same_thread=False` is required for
SQLite because FastAPI handlers may run in a thread pool, meaning the
connection can be touched from threads other than the one that created
the engine.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .paths import get_db_path


class Base(DeclarativeBase):
    """Base class for all ORM models."""


engine = create_engine(
    f"sqlite:///{get_db_path()}",
    connect_args={"check_same_thread": False},
    echo=False,
)


# SQLite disables foreign key enforcement by default. Turn it on so
# ON DELETE CASCADE actually fires at the database level.
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency that yields a scoped SQLAlchemy session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()