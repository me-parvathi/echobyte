from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    user_message: str


class ChatResponse(BaseModel):
    response: str


class ClearConversationRequest(BaseModel):
    session_id: str


class ClearConversationResponse(BaseModel):
    message: str 