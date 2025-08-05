import os
import openai
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from .system_prompt import SYSTEM_PROMPT
from ..rag_engine.retriever import get_relevant_context

# Load environment variables
load_dotenv()


class ChatbotService:
    def __init__(self):
        # Azure OpenAI configuration
        openai.api_type = "azure"
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        # Check if Azure OpenAI is configured
        config_values = [
            openai.api_base,
            openai.api_key,
            openai.api_version,
            self.deployment
        ]
        
        self.azure_configured = all(config_values)
        
        if not self.azure_configured:
            print("⚠️  Azure OpenAI not configured. Chatbot will use fallback responses.")
        
        # Store for session messages
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

    def get_employee_id_by_username(self, username: str) -> Optional[int]:
        """Get employee ID by username from database."""
        db: Session = next(get_db())
        try:
            result = db.execute(
                text("SELECT EmployeeID FROM Employees WHERE UserID = :username"),
                {"username": username}
            ).fetchone()
            return result[0] if result else None
        finally:
            db.close()

    def get_ticket_number(self, username: str) -> str:
        """Get the most recent ticket number for a user."""
        emp_id = self.get_employee_id_by_username(username)
        if not emp_id:
            return "No employee found for this user."

        db: Session = next(get_db())
        try:
            result = db.execute(
                text("SELECT TOP 1 TicketNumber FROM Tickets WHERE OpenedByID = :emp_id"),
                {"emp_id": emp_id}
            ).fetchone()
            return result[0] if result else "You have not raised any tickets."
        finally:
            db.close()

    def get_ticket_status(self, username: str) -> str:
        """Get the status of the most recent ticket for a user."""
        emp_id = self.get_employee_id_by_username(username)
        if not emp_id:
            return "No employee found for this user."

        db: Session = next(get_db())
        try:
            result = db.execute(
                text("SELECT TOP 1 StatusCode FROM Tickets WHERE OpenedByID = :emp_id"),
                {"emp_id": emp_id}
            ).fetchone()
            return f"Your ticket status is: {result[0]}" if result else "No ticket found."
        finally:
            db.close()

    def handle_predefined_responses(self, user_question: str, username: str) -> Optional[str]:
        """Handle predefined responses for common queries."""
        question_lower = user_question.lower()
        
        if question_lower == "my ticket number":
            return self.get_ticket_number(username)
        elif question_lower == "my ticket status":
            return self.get_ticket_status(username)
        elif question_lower == "how long will it take to resolve my ticket?":
            return "It usually takes 2–5 business days to resolve a ticket."
        elif question_lower in ["hi", "hello"]:
            return f"Hi {username.split('.')[0].capitalize()}, how can I help you today?"
        elif question_lower in ["logout", "sign out"]:
            return "You have been logged out. See you again!"
        
        return None

    def generate_gpt_response(self, session_id: str, user_msg: str) -> str:
        """Generate response using Azure OpenAI or fallback responses."""
        
        # If Azure OpenAI is not configured, use fallback responses
        if not self.azure_configured:
            return self._get_fallback_response(user_msg)
        
        try:
            client = openai.AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )

            messages = self.conversations[session_id].copy()
            messages.append({"role": "user", "content": user_msg})
            
            # Try to get relevant context from RAG engine
            try:
                context = get_relevant_context(user_msg)
                if context:
                    # Add context to the user message
                    enhanced_message = f"Context: {context}\n\nUser question: {user_msg}"
                    messages[-1]["content"] = enhanced_message
            except Exception as e:
                # If RAG fails, continue without context
                print(f"RAG engine error (continuing without context): {e}")
                pass

            chat_response = client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.3
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"

    def _get_fallback_response(self, user_msg: str) -> str:
        """Provide fallback responses when Azure OpenAI is not configured."""
        msg_lower = user_msg.lower()
        
        # Common IT support responses
        if any(word in msg_lower for word in ['password', 'reset', 'forgot']):
            return "For password reset, please visit https://reset.company.com. If you face issues, contact IT at it@company.com."
        
        elif any(word in msg_lower for word in ['vpn', 'remote', 'access']):
            return "To access VPN, install GlobalProtect VPN and use your employee ID to log in. For issues, raise a ticket on ServiceNow."
        
        elif any(word in msg_lower for word in ['ticket', 'sla', 'priority', 'time']):
            return "Ticket SLAs: Low priority - 72 hours, Medium priority - 24 hours, High priority - 6 hours."
        
        elif any(word in msg_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm ByteMate, your IT assistant. How can I help you today?"
        
        elif any(word in msg_lower for word in ['help', 'support', 'issue']):
            return "I can help you with password resets, VPN access, ticket information, and general IT support. What do you need help with?"
        
        elif any(word in msg_lower for word in ['bye', 'goodbye', 'logout']):
            return "Goodbye! Feel free to reach out if you need more help."
        
        else:
            return "I understand you're asking about IT support. While I'm currently in fallback mode, I can help with common issues like password resets, VPN access, and ticket information. Please contact IT support directly for complex issues."

    def process_chat_message(self, session_id: str, user_message: str, username: str) -> str:
        """Process a chat message and return appropriate response."""
        # Initialize conversation if it doesn't exist
        if session_id not in self.conversations:
            self.conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Check for predefined responses first
        predefined_response = self.handle_predefined_responses(user_message, username)
        if predefined_response:
            response = predefined_response
        else:
            # Generate AI response
            response = self.generate_gpt_response(session_id, user_message)

        # Update conversation history
        self.conversations[session_id].append({"role": "user", "content": user_message})
        self.conversations[session_id].append({"role": "assistant", "content": response})

        return response

    def clear_conversation(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id] 