from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
import os
import logging
import time
import threading
from typing import Generator, Optional
from contextlib import contextmanager
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection monitoring
_connection_monitor = {
    "active_connections": 0,
    "total_requests": 0,
    "failed_requests": 0,
    "last_reset": time.time(),
    "lock": threading.Lock()
}

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
        
        # Connection pool settings - increased for better handling
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "15"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "30"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "60"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 minutes
        
        # Engine settings
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        
        # Retry settings
        self.max_retries = int(os.getenv("DB_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("DB_RETRY_DELAY", "1.0"))
        
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

def validate_connection(db: Session) -> bool:
    """
    Validate that a database connection is still active.
    
    Args:
        db: Database session to validate
        
    Returns:
        bool: True if connection is valid, False otherwise
    """
    try:
        db.execute(text("SELECT 1"))
        return True
    except (OperationalError, DisconnectionError):
        return False
    except Exception:
        return False

def retry_on_connection_failure(max_retries: int = None, delay: float = None):
    """
    Decorator to retry database operations on connection failures.
    
    Args:
        max_retries: Maximum number of retries (defaults to config)
        delay: Delay between retries in seconds (defaults to config)
    """
    max_retries = max_retries or db_config.max_retries
    delay = delay or db_config.retry_delay
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Database connection failed, retrying in {delay}s (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        # Exponential backoff
                        delay *= 2
                    else:
                        logger.error(f"Database connection failed after {max_retries + 1} attempts: {e}")
                        raise
                except Exception as e:
                    # Don't retry on non-connection errors
                    raise
            
            raise last_exception
        return wrapper
    return decorator

def get_connection_stats() -> dict:
    """
    Get current connection pool statistics.
    
    Returns:
        dict: Connection pool statistics
    """
    pool = engine.pool
    with _connection_monitor["lock"]:
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "active_connections": _connection_monitor["active_connections"],
            "total_requests": _connection_monitor["total_requests"],
            "failed_requests": _connection_monitor["failed_requests"],
            "last_reset": _connection_monitor["last_reset"]
        }

def reset_connection_pool():
    """
    Reset the connection pool to clear any stuck connections.
    """
    logger.warning("Resetting database connection pool")
    try:
        engine.dispose()
        with _connection_monitor["lock"]:
            _connection_monitor["last_reset"] = time.time()
        logger.info("Database connection pool reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset connection pool: {e}")

# Database session dependency for FastAPI with enhanced error handling
def get_db() -> Generator[Session, None, None]:
    """
    Enhanced dependency function to get database session with proper cleanup.
    Yields a database session and ensures it's properly closed.
    
    Usage in FastAPI:
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = None
    with _connection_monitor["lock"]:
        _connection_monitor["active_connections"] += 1
        _connection_monitor["total_requests"] += 1
    
    try:
        db = SessionLocal()
        
        # Validate connection before use
        if not validate_connection(db):
            logger.warning("Invalid database connection detected, attempting to reset pool")
            reset_connection_pool()
            db = SessionLocal()
            if not validate_connection(db):
                raise OperationalError("Failed to establish valid database connection", None, None)
        
        yield db
        
    except SQLAlchemyError as e:
        with _connection_monitor["lock"]:
            _connection_monitor["failed_requests"] += 1
        logger.error(f"Database error: {e}")
        if db:
            db.rollback()
        raise
    except Exception as e:
        with _connection_monitor["lock"]:
            _connection_monitor["failed_requests"] += 1
        logger.error(f"Unexpected error: {e}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
        
        with _connection_monitor["lock"]:
            _connection_monitor["active_connections"] = max(0, _connection_monitor["active_connections"] - 1)

# Enhanced context manager for database sessions
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Enhanced context manager for database sessions with proper cleanup.
    
    Usage:
    with get_db_session() as db:
        result = db.query(Item).all()
    """
    db = None
    with _connection_monitor["lock"]:
        _connection_monitor["active_connections"] += 1
        _connection_monitor["total_requests"] += 1
    
    try:
        db = SessionLocal()
        
        # Validate connection before use
        if not validate_connection(db):
            logger.warning("Invalid database connection detected, attempting to reset pool")
            reset_connection_pool()
            db = SessionLocal()
            if not validate_connection(db):
                raise OperationalError("Failed to establish valid database connection", None, None)
        
        yield db
        db.commit()
        
    except SQLAlchemyError as e:
        with _connection_monitor["lock"]:
            _connection_monitor["failed_requests"] += 1
        logger.error(f"Database error: {e}")
        if db:
            db.rollback()
        raise
    except Exception as e:
        with _connection_monitor["lock"]:
            _connection_monitor["failed_requests"] += 1
        logger.error(f"Unexpected error: {e}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
        
        with _connection_monitor["lock"]:
            _connection_monitor["active_connections"] = max(0, _connection_monitor["active_connections"] - 1)

# Enhanced database connection test function
@retry_on_connection_failure()
def test_database_connection() -> bool:
    """
    Test database connection with retry logic.
    
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

# Enhanced event listeners for database operations
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
    with _connection_monitor["lock"]:
        _connection_monitor["active_connections"] += 1

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log when a connection is checked in to the pool"""
    logger.debug("Database connection checked in to pool")
    with _connection_monitor["lock"]:
        _connection_monitor["active_connections"] = max(0, _connection_monitor["active_connections"] - 1)

# Enhanced health check function
def get_database_health() -> dict:
    """
    Get comprehensive database health status.
    
    Returns:
        dict: Health status information
    """
    try:
        with get_db_session() as db:
            # Test basic connectivity
            db.execute(text("SELECT 1"))
            
            # Get connection pool status
            pool = engine.pool
            stats = get_connection_stats()
            
            health_status = {
                "status": "healthy",
                "connection_pool": {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow()
                },
                "monitoring": stats,
                "database_url": db_config.database_url.replace(db_config.password, "***"),
                "config": {
                    "host": db_config.host,
                    "port": db_config.port,
                    "database": db_config.database,
                    "username": db_config.username,
                    "pool_size": db_config.pool_size,
                    "max_overflow": db_config.max_overflow,
                    "pool_timeout": db_config.pool_timeout,
                    "pool_recycle": db_config.pool_recycle,
                    "max_retries": db_config.max_retries,
                    "retry_delay": db_config.retry_delay
                }
            }
            
            # Check for potential issues
            if stats["checked_out"] > db_config.pool_size * 0.8:
                health_status["warnings"] = ["High connection usage detected"]
            
            if stats["failed_requests"] > 0:
                health_status["warnings"] = health_status.get("warnings", []) + [f"{stats['failed_requests']} failed requests"]
            
            return health_status
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": db_config.database_url.replace(db_config.password, "***"),
            "monitoring": get_connection_stats()
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
    "get_connection_stats",
    "reset_connection_pool",
    "validate_connection",
    "retry_on_connection_failure",
    "db_config"
] 