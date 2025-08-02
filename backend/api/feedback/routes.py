from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service

router = APIRouter()

# Feedback Type routes (must come before parameterized routes)
@router.get("/types", response_model=List[schemas.FeedbackTypeResponse])
def get_feedback_types(db: Session = Depends(get_db)):
    """Get list of feedback types"""
    return service.FeedbackService.get_feedback_types(db)

@router.get("/types/{type_code}", response_model=schemas.FeedbackTypeResponse)
def get_feedback_type(type_code: str, db: Session = Depends(get_db)):
    """Get a specific feedback type by code"""
    feedback_type = service.FeedbackService.get_feedback_type(db, type_code)
    if not feedback_type:
        raise HTTPException(status_code=404, detail="Feedback type not found")
    return feedback_type

# Feedback management routes (must come before parameterized routes)
@router.get("/unread/count")
def get_unread_feedback_count(
    target_manager_id: Optional[int] = None,
    target_department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get count of unread feedback"""
    return service.FeedbackService.get_unread_count(db, target_manager_id, target_department_id)

# Feedback routes
@router.get("/", response_model=List[schemas.EmployeeFeedbackResponse])
def get_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    feedback_type_code: Optional[str] = None,
    target_manager_id: Optional[int] = None,
    target_department_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of feedback with optional filtering"""
    return service.FeedbackService.get_feedback(db, skip, limit, feedback_type_code, target_manager_id, target_department_id, is_read)

@router.post("/", response_model=schemas.EmployeeFeedbackResponse, status_code=201)
def create_feedback(feedback: schemas.EmployeeFeedbackCreate, db: Session = Depends(get_db)):
    """Create new feedback"""
    return service.FeedbackService.create_feedback(db, feedback)

# Parameterized routes (must come last)
@router.get("/{feedback_id}", response_model=schemas.EmployeeFeedbackResponse)
def get_feedback_item(feedback_id: int, db: Session = Depends(get_db)):
    """Get a specific feedback by ID"""
    feedback = service.FeedbackService.get_feedback_item(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.put("/{feedback_id}", response_model=schemas.EmployeeFeedbackResponse)
def update_feedback(
    feedback_id: int, 
    feedback_update: schemas.EmployeeFeedbackUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing feedback"""
    return service.FeedbackService.update_feedback(db, feedback_id, feedback_update)

@router.delete("/{feedback_id}", status_code=204)
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """Delete a feedback"""
    service.FeedbackService.delete_feedback(db, feedback_id)
    return None

@router.post("/{feedback_id}/mark-read")
def mark_feedback_as_read(
    feedback_id: int,
    read_request: schemas.FeedbackReadRequest,
    db: Session = Depends(get_db)
):
    """Mark feedback as read"""
    return service.FeedbackService.mark_as_read(db, feedback_id, read_request) 