from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from typing import Generator
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration with environment variable support
class DatabaseConfig:
    """Database configuration class with environment variable support"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "1433")
        self.database = os.getenv("DB_NAME", "echobyte_test")
        self.username = os.getenv("DB_USERNAME", "sa")
        self.password = os.getenv("DB_PASSWORD", "YourPassword123!")
        self.driver = os.getenv("DB_DRIVER", "ODBC+Driver+18+for+SQL+Server")
        
        # Connection pool settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # Engine settings
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        
    @property
    def database_url(self) -> str:
        """Generate database URL from configuration"""
        # Azure SQL Database requires additional parameters
        return (
            f"mssql+pyodbc://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}?"
            f"driver={self.driver}&"
            f"Encrypt=yes&"
            f"TrustServerCertificate=no&"
            f"Connection+Timeout=30&"
            f"Login+Timeout=30"
        )

# Initialize configuration
db_config = DatabaseConfig()

# Create SQLAlchemy engine with enhanced configuration
engine = create_engine(
    db_config.database_url,
    echo=db_config.echo,
    poolclass=QueuePool,
    pool_size=db_config.pool_size,
    max_overflow=db_config.max_overflow,
    pool_timeout=db_config.pool_timeout,
    pool_recycle=db_config.pool_recycle,
    pool_pre_ping=db_config.pool_pre_ping,
    connect_args={
        "check_same_thread": False,  # For SQLite compatibility
    } if "sqlite" in db_config.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all declarative models
Base = declarative_base()

# Database session dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's properly closed.
    
    Usage in FastAPI:
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Context manager for database sessions
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
    with get_db_session() as db:
        result = db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Database connection test function
def test_database_connection() -> bool:
    """
    Test database connection and return True if successful.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with get_db_session() as db:
            # Execute a simple query to test connection
            db.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

# Database initialization function
def init_database() -> None:
    """
    Initialize database by creating all tables.
    This should be called once during application startup.
    """
    try:
        # Import all models to ensure they are registered with Base
        # Import each module explicitly to avoid wildcard imports
        import api.employee.models
        import api.department.models
        import api.team.models
        import api.location.models
        import api.leave.models
        import api.timesheet.models
        import api.asset.models
        import api.feedback.models
        import api.auth.models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test connection
        if test_database_connection():
            logger.info("Database initialization completed successfully")
        else:
            logger.error("Database initialization failed - connection test failed")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Event listeners for database operations
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and foreign key support"""
    if "sqlite" in db_config.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool"""
    logger.debug("Database connection checked out from pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log when a connection is checked in to the pool"""
    logger.debug("Database connection checked in to pool")

# Health check function
def get_database_health() -> dict:
    """
    Get database health status.
    
    Returns:
        dict: Health status information
    """
    try:
        with get_db_session() as db:
            # Test basic connectivity
            db.execute(text("SELECT 1"))
            
            # Get connection pool status
            pool = engine.pool
            health_status = {
                "status": "healthy",
                "connection_pool": {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid()
                },
                "database_url": db_config.database_url.replace(db_config.password, "***"),
                "config": {
                    "host": db_config.host,
                    "port": db_config.port,
                    "database": db_config.database,
                    "username": db_config.username,
                    "pool_size": db_config.pool_size,
                    "max_overflow": db_config.max_overflow
                }
            }
            return health_status
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": db_config.database_url.replace(db_config.password, "***")
        }

# Export commonly used items
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "get_db",
    "get_db_session",
    "test_database_connection",
    "init_database",
    "get_database_health",
    "db_config"
] 