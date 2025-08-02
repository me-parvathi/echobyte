from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from . import models, schemas
from fastapi import HTTPException
from datetime import datetime

class FeedbackService:
    
    @staticmethod
    def get_feedback(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        feedback_type_code: Optional[str] = None,
        target_manager_id: Optional[int] = None,
        target_department_id: Optional[int] = None,
        is_read: Optional[bool] = None
    ) -> List[models.EmployeeFeedback]:
        """Get list of feedback with optional filtering"""
        query = db.query(models.EmployeeFeedback)
        
        if feedback_type_code:
            query = query.filter(models.EmployeeFeedback.FeedbackTypeCode == feedback_type_code)
        
        if target_manager_id:
            query = query.filter(models.EmployeeFeedback.TargetManagerID == target_manager_id)
        
        if target_department_id:
            query = query.filter(models.EmployeeFeedback.TargetDepartmentID == target_department_id)
        
        if is_read is not None:
            query = query.filter(models.EmployeeFeedback.IsRead == is_read)
        
        return query.order_by(models.EmployeeFeedback.FeedbackAt.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_feedback_item(db: Session, feedback_id: int) -> Optional[models.EmployeeFeedback]:
        """Get a specific feedback by ID"""
        return db.query(models.EmployeeFeedback).filter(models.EmployeeFeedback.FeedbackID == feedback_id).first()
    
    @staticmethod
    def create_feedback(db: Session, feedback: schemas.EmployeeFeedbackCreate) -> models.EmployeeFeedback:
        """Create new feedback"""
        db_feedback = models.EmployeeFeedback(
            FeedbackTypeCode=feedback.FeedbackTypeCode,
            Category=feedback.Category,
            Subject=feedback.Subject,
            FeedbackText=feedback.FeedbackText,
            TargetManagerID=feedback.TargetManagerID,
            TargetDepartmentID=feedback.TargetDepartmentID,
            FeedbackAt=datetime.utcnow()
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    
    @staticmethod
    def update_feedback(
        db: Session, 
        feedback_id: int, 
        feedback_update: schemas.EmployeeFeedbackUpdate
    ) -> Optional[models.EmployeeFeedback]:
        """Update an existing feedback"""
        db_feedback = db.query(models.EmployeeFeedback).filter(
            models.EmployeeFeedback.FeedbackID == feedback_id
        ).first()
        
        if not db_feedback:
            return None
        
        update_data = feedback_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_feedback, field, value)
        
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    
    @staticmethod
    def delete_feedback(db: Session, feedback_id: int) -> bool:
        """Delete a feedback"""
        db_feedback = db.query(models.EmployeeFeedback).filter(
            models.EmployeeFeedback.FeedbackID == feedback_id
        ).first()
        
        if not db_feedback:
            return False
        
        db.delete(db_feedback)
        db.commit()
        return True
    
    @staticmethod
    def get_feedback_types(db: Session) -> List[models.FeedbackType]:
        """Get list of feedback types"""
        return db.query(models.FeedbackType).filter(models.FeedbackType.IsActive == True).all()
    
    @staticmethod
    def get_feedback_type(db: Session, type_code: str) -> Optional[models.FeedbackType]:
        """Get a specific feedback type by code"""
        return db.query(models.FeedbackType).filter(
            models.FeedbackType.FeedbackTypeCode == type_code,
            models.FeedbackType.IsActive == True
        ).first()
    
    @staticmethod
    def mark_as_read(
        db: Session, 
        feedback_id: int, 
        read_request: schemas.FeedbackReadRequest
    ) -> dict:
        """Mark feedback as read"""
        db_feedback = db.query(models.EmployeeFeedback).filter(
            models.EmployeeFeedback.FeedbackID == feedback_id
        ).first()
        
        if not db_feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        db_feedback.IsRead = True
        db_feedback.ReadByID = read_request.EmployeeID
        db_feedback.ReadAt = datetime.utcnow()
        
        db.commit()
        db.refresh(db_feedback)
        
        return {"message": "Feedback marked as read", "feedback_id": feedback_id}
    
    @staticmethod
    def get_unread_count(
        db: Session,
        target_manager_id: Optional[int] = None,
        target_department_id: Optional[int] = None
    ) -> dict:
        """Get count of unread feedback"""
        query = db.query(models.EmployeeFeedback).filter(models.EmployeeFeedback.IsRead == False)
        
        if target_manager_id:
            query = query.filter(models.EmployeeFeedback.TargetManagerID == target_manager_id)
        
        if target_department_id:
            query = query.filter(models.EmployeeFeedback.TargetDepartmentID == target_department_id)
        
        count = query.count()
        return {"unread_count": count} 