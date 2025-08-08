import os
import openai
import re
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from .system_prompt import SYSTEM_PROMPT
from ..rag_engine.retriever import get_relevant_context, get_rag_response

# Load environment variables
load_dotenv()

# Security Guardrails
PROFANITY_LIST = ["idiot", "stupid", "damn", "shit", "fuck", "bitch", "asshole"]
OFF_TOPIC_KEYWORDS = ["movie", "song", "relationship", "poem", "story"]
SENSITIVE_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    r"\b[\w.-]+@[\w.-]+\.\w+\b",  # email
    r"(AKIA|SKIA|ghp_)[A-Za-z0-9]{16,}"  # AWS/API keys
]

def contains_profanity(text: str) -> bool:
    """Check if text contains profanity."""
    return any(re.search(rf"\b{re.escape(word)}\b", text.lower()) for word in PROFANITY_LIST)

def is_off_topic(text: str) -> bool:
    """Check if text is off-topic for IT helpdesk."""
    return any(keyword in text.lower() for keyword in OFF_TOPIC_KEYWORDS)

def contains_sensitive_data(text: str) -> bool:
    """Check if text contains sensitive data patterns."""
    return any(re.search(pat, text) for pat in SENSITIVE_PATTERNS)


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
                text("""
                    SELECT TOP 1 t.TicketNumber, t.StatusCode, t.Subject, t.CreatedDate, t.PriorityCode
                    FROM Tickets t 
                    WHERE t.OpenedByID = :emp_id 
                    ORDER BY t.CreatedDate DESC
                """),
                {"emp_id": emp_id}
            ).fetchone()
            
            if result:
                ticket_num, status, subject, created_date, priority = result
                return f"Your most recent ticket (#{ticket_num}) is '{subject}' with status '{status}' and priority '{priority}'. Created on {created_date.strftime('%Y-%m-%d') if created_date else 'Unknown date'}."
            else:
                return "No tickets found for your account."
        finally:
            db.close()

    def get_all_tickets(self, username: str) -> str:
        """Get all tickets for a user."""
        emp_id = self.get_employee_id_by_username(username)
        if not emp_id:
            return "No employee found for this user."

        db: Session = next(get_db())
        try:
            results = db.execute(
                text("""
                    SELECT TicketNumber, StatusCode, Subject, CreatedDate, PriorityCode
                    FROM Tickets 
                    WHERE OpenedByID = :emp_id 
                    ORDER BY CreatedDate DESC
                """),
                {"emp_id": emp_id}
            ).fetchall()
            
            if results:
                ticket_info = []
                for ticket_num, status, subject, created_date, priority in results:
                    date_str = created_date.strftime('%Y-%m-%d') if created_date else 'Unknown'
                    ticket_info.append(f"#{ticket_num}: {subject} ({status}, {priority}) - {date_str}")
                
                return f"You have {len(results)} ticket(s):\n" + "\n".join(ticket_info)
            else:
                return "You have no tickets in the system."
        finally:
            db.close()

    def get_employee_info(self, username: str) -> str:
        """Get basic employee information."""
        emp_id = self.get_employee_id_by_username(username)
        if not emp_id:
            return "No employee found for this user."

        db: Session = next(get_db())
        try:
            result = db.execute(
                text("""
                    SELECT e.FirstName, e.LastName, e.Email, d.DepartmentName, e.HireDate
                    FROM Employees e
                    LEFT JOIN Departments d ON e.DepartmentID = d.DepartmentID
                    WHERE e.EmployeeID = :emp_id
                """),
                {"emp_id": emp_id}
            ).fetchone()
            
            if result:
                first_name, last_name, email, dept, hire_date = result
                hire_str = hire_date.strftime('%Y-%m-%d') if hire_date else 'Unknown'
                return f"Employee: {first_name} {last_name}\nEmail: {email}\nDepartment: {dept or 'Not assigned'}\nHire Date: {hire_str}"
            else:
                return "Employee information not found."
        finally:
            db.close()

    def handle_predefined_responses(self, user_question: str, username: str) -> Optional[str]:
        """Handle predefined responses for common queries."""
        question_lower = user_question.lower()
        
        if question_lower == "my ticket number":
            return self.get_ticket_number(username)
        elif question_lower == "my ticket status":
            return self.get_ticket_status(username)
        elif question_lower in ["my tickets", "all my tickets", "show my tickets"]:
            return self.get_all_tickets(username)
        elif question_lower in ["my info", "employee info", "my profile"]:
            return self.get_employee_info(username)
        elif question_lower == "how long will it take to resolve my ticket?":
            return "It usually takes 2–5 business days to resolve a ticket."
        elif question_lower in ["hi", "hello"]:
            return f"Hi {username.split('.')[0].capitalize()}, how can I help you today?"
        elif question_lower in ["logout", "sign out"]:
            return "You have been logged out. See you again!"
        elif question_lower in ["help", "what can you do"]:
            return """I can help you with:
• Check your ticket status and number
• View all your tickets
• Get your employee information
• IT support questions
• Password reset guidance
• VPN access help
• General IT assistance

Just ask me anything related to IT support!"""
        
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
            
            # Try to get RAG response first, fallback to context enhancement
            try:
                rag_response = get_rag_response(user_msg)
                if rag_response and "I'm sorry, I couldn't find anything" not in rag_response:
                    return rag_response
            except Exception as e:
                print(f"RAG response error (falling back to context): {e}")
            
            # Fallback: Try to get relevant context from RAG engine
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
        except openai.AuthenticationError:
            print("Azure OpenAI authentication failed")
            return self._get_fallback_response(user_msg)
        except openai.RateLimitError:
            print("Azure OpenAI rate limit exceeded")
            return "I'm experiencing high traffic right now. Please try again in a few minutes."
        except openai.APIError as e:  # ✅ CORRECT EXCEPTION
            print(f"Azure OpenAI API error: {e}")
            return self._get_fallback_response(user_msg)
        except Exception as e:
            print(f"Azure OpenAI error: {e}")
            return self._get_fallback_response(user_msg)
    def _get_fallback_response(self, user_msg: str) -> str:
        """Provide fallback responses when Azure OpenAI is not configured or fails."""
        msg_lower = user_msg.lower()
        
        # Common IT support responses
        if any(word in msg_lower for word in ['password', 'reset', 'forgot']):
            return "For password reset, please visit https://reset.company.com. If you face issues, contact IT at it@company.com or raise a ticket."
        
        elif any(word in msg_lower for word in ['vpn', 'remote', 'access']):
            return "To access VPN, install GlobalProtect VPN and use your employee ID to log in. For issues, raise a ticket on ServiceNow."
        
        elif any(word in msg_lower for word in ['ticket', 'sla', 'priority']):
            return "Ticket SLAs: Low priority - 72 hours, Medium priority - 24 hours, High priority - 6 hours. You can check your ticket status by asking 'my ticket status'."
        
        elif any(word in msg_lower for word in ['email', 'outlook', 'mail']):
            return "For email issues, try clearing your browser cache first. If problems persist, contact IT support or raise a ticket."
        
        elif any(word in msg_lower for word in ['printer', 'print', 'scanner']):
            return "For printer/scanner issues, check if the device is powered on and connected to the network. Contact IT if you need driver installation or troubleshooting."
        
        elif any(word in msg_lower for word in ['software', 'application', 'app']):
            return "For software installation requests, please raise a ticket with details about the application you need. IT will review and install approved software."
        
        elif any(word in msg_lower for word in ['hardware', 'computer', 'laptop', 'desktop']):
            return "For hardware issues, please raise a ticket with a detailed description of the problem. IT will schedule a technician if needed."
        
        elif any(word in msg_lower for word in ['network', 'internet', 'wifi']):
            return "For network connectivity issues, try restarting your router/modem first. If problems persist, contact IT support immediately."
        
        elif any(word in msg_lower for word in ['security', 'antivirus', 'malware']):
            return "For security concerns, immediately contact IT security team. Do not click on suspicious links or download unknown files."
        
        elif any(word in msg_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm ByteMate, your IT assistant. How can I help you today?"
        
        elif any(word in msg_lower for word in ['help', 'support', 'issue']):
            return "I can help you with password resets, VPN access, ticket information, email issues, and general IT support. What do you need help with?"
        
        elif any(word in msg_lower for word in ['bye', 'goodbye', 'logout']):
            return "Goodbye! Feel free to reach out if you need more help."
        
        elif any(word in msg_lower for word in ['thanks', 'thank you']):
            return "You're welcome! Is there anything else I can help you with?"
        
        else:
            return "I understand you're asking about IT support. While I'm currently in fallback mode, I can help with common issues like password resets, VPN access, ticket information, and general IT support. Please contact IT support directly for complex issues or raise a ticket for specific problems."

    def process_chat_message(self, session_id: str, user_message: str, username: str) -> str:
        """Process a chat message and return appropriate response."""
        # Initialize conversation if it doesn't exist
        if session_id not in self.conversations:
            self.conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Security validation
        if contains_profanity(user_message):
            response = "Please keep the conversation respectful. I'm here to assist you with IT helpdesk topics."
        elif is_off_topic(user_message):
            response = "I'm here to help with IT Help Desk topics only. Please ask me about technical support, tickets, or IT-related questions."
        elif contains_sensitive_data(user_message):
            response = "Please do not share sensitive information like passwords, API keys, or personal data. Contact IT support directly if you need to report security issues."
        else:
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