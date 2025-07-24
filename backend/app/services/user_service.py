from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import Optional, List
import uuid
from datetime import datetime

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.UserID == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.Email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.Username == username).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user.password)
        user_id = str(uuid.uuid4())
        db_user = User(
            UserID=user_id,
            Email=user.email,
            Username=user.username,
            HashedPassword=hashed_password,
            IsActive=user.is_active,
            IsSuperuser=user.is_superuser
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update a user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            # Map schema fields to model fields
            if field == "email":
                setattr(db_user, "Email", value)
            elif field == "username":
                setattr(db_user, "Username", value)
            elif field == "is_active":
                setattr(db_user, "IsActive", value)
            elif field == "is_superuser":
                setattr(db_user, "IsSuperuser", value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True 