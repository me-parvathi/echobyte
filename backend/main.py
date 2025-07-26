import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import time

# Load environment variables from .env file
load_dotenv()

# Import all routers
from api.employee.routes import router as employee_router
from api.department.routes import router as department_router
from api.team.routes import router as team_router
from api.location.routes import router as location_router
from api.leave.routes import router as leave_router
from api.timesheet.routes import router as timesheet_router
from api.asset.routes import router as asset_router
from api.feedback.routes import router as feedback_router
from api.auth.routes import router as auth_router

# Import database utilities
from core.database import init_database, get_database_health, test_database_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting EchoByte HR Management API...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Test database connection
        if test_database_connection():
            logger.info("Database connection successful")
        else:
            logger.error("Database connection failed")
            raise Exception("Database connection failed")
            
        logger.info("EchoByte HR Management API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down EchoByte HR Management API...")

# Initialize FastAPI application
app = FastAPI(
    title="EchoByte HR Management API",
    description="""
    A comprehensive HR management system API providing:
    
    ## Features
    * 👥 **Employee Management** - Complete employee lifecycle management
    * 🏢 **Department & Team Management** - Organizational structure management
    * 📍 **Location Management** - Multi-location support
    * 🏖️ **Leave Management** - Leave applications, approvals, and balances
    * ⏰ **Timesheet Management** - Time tracking and approval workflows
    * 💻 **Asset Management** - IT asset tracking and assignments
    * 💬 **Feedback System** - Employee feedback and communication
    * 🔐 **Authentication & Authorization** - Secure access control
    
    ## Authentication
    This API uses JWT tokens for authentication. Include the token in the Authorization header:
    `Authorization: Bearer <your-token>`
    
    ## Rate Limiting
    API requests are rate-limited to ensure fair usage and system stability.
    """,
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
    lifespan=lifespan,
    debug=DEBUG
)

# Middleware Configuration

# Trusted Host Middleware (Security)
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-API-Key"
    ],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=86400,  # 24 hours
)

# GZip Middleware (Compression)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests and their processing time.
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Exception Handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "path": request.url.path
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions.
    """
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path
        }
    )

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database-related exceptions.
    """
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error" if not DEBUG else str(exc),
            "path": request.url.path
        }
    )

# Include all routers with proper organization

# Authentication and Authorization
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication & Authorization"],
    responses={404: {"description": "Not found"}}
)

# Core HR Management
app.include_router(
    employee_router,
    prefix="/api/employees",
    tags=["Employee Management"],
    responses={404: {"description": "Employee not found"}}
)

app.include_router(
    department_router,
    prefix="/api/departments",
    tags=["Department Management"],
    responses={404: {"description": "Department not found"}}
)

app.include_router(
    team_router,
    prefix="/api/teams",
    tags=["Team Management"],
    responses={404: {"description": "Team not found"}}
)

app.include_router(
    location_router,
    prefix="/api/locations",
    tags=["Location Management"],
    responses={404: {"description": "Location not found"}}
)

# Workflow Management
app.include_router(
    leave_router,
    prefix="/api/leave",
    tags=["Leave Management"],
    responses={404: {"description": "Leave record not found"}}
)

app.include_router(
    timesheet_router,
    prefix="/api/timesheets",
    tags=["Timesheet Management"],
    responses={404: {"description": "Timesheet not found"}}
)

# Asset Management
app.include_router(
    asset_router,
    prefix="/api/assets",
    tags=["Asset Management"],
    responses={404: {"description": "Asset not found"}}
)

# Communication
app.include_router(
    feedback_router,
    prefix="/api/feedback",
    tags=["Feedback System"],
    responses={404: {"description": "Feedback not found"}}
)

# Root endpoints

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Welcome to EchoByte HR Management API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "docs_url": "/docs" if DEBUG else None,
        "health_check": "/health",
        "database_health": "/health/database"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/health/database", tags=["Health"])
async def database_health_check():
    """
    Database health check endpoint.
    """
    return get_database_health()

@app.get("/health/full", tags=["Health"])
async def full_health_check():
    """
    Comprehensive health check including all system components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": ENVIRONMENT,
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "database": "unknown"
        }
    }
    
    # Check database health
    try:
        db_health = get_database_health()
        health_status["components"]["database"] = db_health["status"]
        if db_health["status"] != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
        health_status["database_error"] = str(e)
    
    return health_status

# API Information endpoint
@app.get("/api/info", tags=["API Information"])
async def api_info():
    """
    Get detailed API information and available endpoints.
    """
    return {
        "name": "EchoByte HR Management API",
        "version": "1.0.0",
        "description": "A comprehensive HR management system API",
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "endpoints": {
            "authentication": "/api/auth",
            "employees": "/api/employees",
            "departments": "/api/departments",
            "teams": "/api/teams",
            "locations": "/api/locations",
            "leave": "/api/leave",
            "timesheets": "/api/timesheets",
            "assets": "/api/assets",
            "feedback": "/api/feedback"
        },
        "documentation": {
            "swagger": "/docs" if DEBUG else "Not available in production",
            "redoc": "/redoc" if DEBUG else "Not available in production",
            "openapi": "/openapi.json" if DEBUG else "Not available in production"
        }
    }

# Startup event (alternative to lifespan for compatibility)
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    """
    logger.info("Application startup event triggered")
    
    # Register services in dependency injection container
    from core.container import register_services
    register_services()
    logger.info("Services registered in dependency injection container")

# Shutdown event (alternative to lifespan for compatibility)
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    """
    logger.info("Application shutdown event triggered")

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    ) 