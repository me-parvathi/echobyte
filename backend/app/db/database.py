from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import urllib.parse

# Build the connection string for Azure SQL Database
def get_database_url():
    if settings.AZURE_SQL_SERVER and settings.AZURE_SQL_DATABASE:
        # Use individual Azure SQL settings
        password = urllib.parse.quote_plus(settings.AZURE_SQL_PASSWORD)
        return f"mssql+pyodbc://{settings.AZURE_SQL_USERNAME}:{password}@{settings.AZURE_SQL_SERVER}:{settings.AZURE_SQL_PORT}/{settings.AZURE_SQL_DATABASE}?driver=ODBC+Driver+18+for+SQL+Server"
    else:
        # Use the full DATABASE_URL
        return settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    get_database_url(),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 