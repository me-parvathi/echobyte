from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CommentBase(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=1000)
    commenter_role: Optional[str] = Field(None, max_length=20)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(CommentBase):
    comment_id: int
    entity_type: str
    entity_id: int
    commenter_id: int
    commenter_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_edited: bool
    is_active: bool
    
    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total_count: int 