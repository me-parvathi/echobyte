from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, Session

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------
# The connection string can be provided via the DATABASE_URL environment
# variable. Fallback to a local MySQL instance that matches the ddl.sql script
# (adjust credentials as needed).
# Example:  mysql+pymysql://user:password@localhost:3306/echobyte
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/echobyte",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# ---------------------------------------------------------------------------
# ORM base – reflect all tables defined in the existing database so we do not
# have to hand-write models for each one. This relies on the database already
# being migrated according to `database/ddl.sql`.
# ---------------------------------------------------------------------------
Base = automap_base()
Base.prepare(engine, reflect=True)

# ---------------------------------------------------------------------------
# Session helper
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency that yields a database session and ensures it is
    closed after use."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close() 