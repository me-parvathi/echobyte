from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from core.repository import BaseRepository
from .models import Comment
from .schemas import CommentCreate, CommentUpdate

class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __init__(self):
        super().__init__(Comment)
    
    def get_by_id(self, db: Session, id: int) -> Optional[Comment]:
        """Get a specific comment by ID"""
        return db.query(Comment).filter(
            and_(
                Comment.CommentID == id,
                Comment.IsActive == True
            )
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get all active comments with pagination"""
        return db.query(Comment).filter(
            Comment.IsActive == True
        ).offset(skip).limit(limit).all()
    
    def get_by_entity(self, db: Session, entity_type: str, entity_id: int) -> List[Comment]:
        """Get all active comments for a specific entity"""
        return db.query(Comment).filter(
            and_(
                Comment.EntityType == entity_type,
                Comment.EntityID == entity_id,
                Comment.IsActive == True
            )
        ).order_by(Comment.CreatedAt.desc()).all()
    
    def create(self, db: Session, obj_in: CommentCreate) -> Comment:
        """Create a new comment - this method is not used directly"""
        # This method is required by the interface but not used for comments
        # Comments are created via create_comment_for_entity method
        raise NotImplementedError("Use create_comment_for_entity instead")
    
    def create_comment_for_entity(self, db: Session, comment_data: CommentCreate, entity_type: str, 
                                 entity_id: int, commenter_id: int) -> Comment:
        """Create a new comment for a specific entity"""
        comment = Comment(
            EntityType=entity_type,
            EntityID=entity_id,
            CommenterID=commenter_id,
            CommenterRole=comment_data.commenter_role,
            CommentText=comment_data.comment_text
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    
    def update(self, db: Session, comment_id: int, comment_data: CommentUpdate) -> Optional[Comment]:
        """Update an existing comment"""
        comment = self.get_by_id(db, comment_id)
        if comment:
            comment.CommentText = comment_data.comment_text
            comment.UpdatedAt = func.getutcdate()
            comment.IsEdited = True
            db.commit()
            db.refresh(comment)
        return comment
    
    def delete(self, db: Session, comment_id: int) -> bool:
        """Soft delete a comment"""
        comment = self.get_by_id(db, comment_id)
        if comment:
            comment.IsActive = False
            db.commit()
            return True
        return False
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count comments with optional filtering"""
        query = db.query(Comment).filter(Comment.IsActive == True)
        
        if filters:
            for key, value in filters.items():
                if hasattr(Comment, key):
                    query = query.filter(getattr(Comment, key) == value)
        
        return query.count() 