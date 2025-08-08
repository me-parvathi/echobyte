from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.auth import get_current_user
from api.employee.models import Employee
from .schemas import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from .service import CommentService
from .repository import CommentRepository

router = APIRouter()

# Dependency injection
def get_comment_repository() -> CommentRepository:
    return CommentRepository()

def get_comment_service(repository: CommentRepository = Depends(get_comment_repository)) -> CommentService:
    return CommentService(repository)

@router.get("/{entity_type}/{entity_id}", response_model=CommentListResponse)
async def get_comments_for_entity(
    entity_type: str,
    entity_id: int,
    comment_service: CommentService = Depends(get_comment_service),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a specific entity.
    
    Currently supported entity types:
    - LeaveApplication: Comments on leave applications
    - Ticket: Comments on tickets
    """
    return comment_service.get_comments_for_entity(db, entity_type, entity_id)

@router.post("/{entity_type}/{entity_id}", response_model=CommentResponse)
async def create_comment_for_entity(
    entity_type: str,
    entity_id: int,
    comment_data: CommentCreate,
    comment_service: CommentService = Depends(get_comment_service),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a comment for a specific entity.
    
    Currently supported entity types:
    - LeaveApplication: Comments on leave applications
    - Ticket: Comments on tickets
    """
    # Get employee ID for the current user
    employee = db.query(Employee).filter(Employee.UserID == current_user.UserID).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    return comment_service.create_comment(
        db, entity_type, entity_id, comment_data, employee.EmployeeID
    )

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    comment_service: CommentService = Depends(get_comment_service),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing comment.
    
    Users can only edit their own comments.
    """
    # Get employee ID for the current user
    employee = db.query(Employee).filter(Employee.UserID == current_user.UserID).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    return comment_service.update_comment(db, comment_id, comment_data, employee.EmployeeID)

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    comment_service: CommentService = Depends(get_comment_service),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment.
    
    Users can only delete their own comments.
    """
    # Get employee ID for the current user
    employee = db.query(Employee).filter(Employee.UserID == current_user.UserID).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found for current user")
    
    success = comment_service.delete_comment(db, comment_id, employee.EmployeeID)
    if success:
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found") 