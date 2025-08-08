import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_user
from .schemas import (
    ChatRequest, ChatResponse,
    ClearConversationRequest, ClearConversationResponse
)
from core.chatbot.chatbot_service import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()





@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    """
    Chat endpoint for processing user messages.
    Uses the main app's authentication system.
    """
    session_id = request.session_id
    user_message = request.user_message

    if not session_id or not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing session_id or user_message"
        )

    try:
        # Extract username from the current user object
        username = current_user.username if hasattr(current_user, 'username') else str(current_user)
        response = chatbot_service.process_chat_message(session_id, user_message, username)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.post("/clear-conversation", response_model=ClearConversationResponse)
async def clear_conversation(
    request: ClearConversationRequest,
    current_user = Depends(get_current_user)
):
    """
    Clear conversation history for a session.
    Uses the main app's authentication system.
    """
    session_id = request.session_id
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing session_id"
        )

    try:
        chatbot_service.clear_conversation(session_id)
        return ClearConversationResponse(message="Conversation cleared successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing conversation: {str(e)}"
        ) 