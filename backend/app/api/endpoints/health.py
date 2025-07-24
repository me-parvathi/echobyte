from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "EchoByte API"}

@router.get("/db")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        # Simple query to test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)} 