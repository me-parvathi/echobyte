"""
Main Agent Service for EchoByte Workflow Management
Coordinates all agents and provides main interface
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db
from .workflow_agent import WorkflowAgent
from .learning_engine import LearningEngine
from .notification_system import NotificationSystem
from .base_agent import AgentDecision, DecisionStatus


class AgentServiceConfig(BaseModel):
    """Configuration for agent service"""
    enable_auto_processing: bool = True
    enable_learning: bool = True
    enable_notifications: bool = True
    confidence_threshold: float = 0.7
    max_processing_time: int = 30  # seconds
    batch_size: int = 10


class ProcessingResult(BaseModel):
    """Result of agent processing"""
    success: bool
    decision: Optional[AgentDecision] = None
    processing_time: float
    error_message: Optional[str] = None
    notifications_sent: int = 0


class AgentService:
    """
    Main agent service that coordinates all agents and provides the main interface
    """
    
    def __init__(self, config: AgentServiceConfig = None):
        self.config = config or AgentServiceConfig()
        self.logger = logging.getLogger("agent_service")
        
        # Initialize agents
        self.workflow_agent = WorkflowAgent()
        self.learning_engine = LearningEngine()
        self.notification_system = NotificationSystem()
        
        # Processing queues
        self.leave_queue: List[int] = []
        self.timesheet_queue: List[int] = []
        
        # Service state
        self.is_running = False
        self.processing_stats = {
            "total_processed": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "average_processing_time": 0.0
        }
    
    async def start_service(self) -> None:
        """Start the agent service"""
        if self.is_running:
            self.logger.warning("Agent service is already running")
            return
        
        self.is_running = True
        self.logger.info("Starting agent service")
        
        # Start background processing
        asyncio.create_task(self._background_processor())
        
        # Start weekly digest scheduler
        asyncio.create_task(self._weekly_digest_scheduler())
    
    async def stop_service(self) -> None:
        """Stop the agent service"""
        self.is_running = False
        self.logger.info("Stopping agent service")
    
    async def process_leave_application(
        self, 
        leave_application_id: int,
        db: Session
    ) -> ProcessingResult:
        """Process a leave application"""
        
        start_time = datetime.utcnow()
        
        try:
            # Process with workflow agent
            decision = await self.workflow_agent.process_leave_application(
                leave_application_id, db
            )
            
            # Track accuracy
            await self.learning_engine.track_decision_accuracy(
                "workflow_agent", "leave", decision
            )
            
            # Send notifications
            notifications_sent = await self._send_leave_notifications(decision, db)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update stats
            self._update_processing_stats(True, processing_time)
            
            return ProcessingResult(
                success=True,
                decision=decision,
                processing_time=processing_time,
                notifications_sent=notifications_sent
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Error processing leave application {leave_application_id}: {str(e)}")
            
            # Update stats
            self._update_processing_stats(False, processing_time)
            
            return ProcessingResult(
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def process_timesheet(
        self, 
        timesheet_id: int,
        db: Session
    ) -> ProcessingResult:
        """Process a timesheet"""
        
        start_time = datetime.utcnow()
        
        try:
            # Process with workflow agent
            decision = await self.workflow_agent.process_timesheet(timesheet_id, db)
            
            # Track accuracy
            await self.learning_engine.track_decision_accuracy(
                "workflow_agent", "timesheet", decision
            )
            
            # Send notifications
            notifications_sent = await self._send_timesheet_notifications(decision, db)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update stats
            self._update_processing_stats(True, processing_time)
            
            return ProcessingResult(
                success=True,
                decision=decision,
                processing_time=processing_time,
                notifications_sent=notifications_sent
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Error processing timesheet {timesheet_id}: {str(e)}")
            
            # Update stats
            self._update_processing_stats(False, processing_time)
            
            return ProcessingResult(
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def learn_from_override(
        self,
        original_decision: AgentDecision,
        override_decision: AgentDecision,
        override_reason: str,
        override_by: str
    ) -> None:
        """Learn from a manager override"""
        
        await self.learning_engine.learn_from_override(
            original_decision, override_decision, override_reason, override_by
        )
        
        self.logger.info(f"Learned from override by {override_by}")
    
    async def get_agent_insights(
        self, 
        agent_name: str = "workflow_agent",
        time_period: str = "6months"
    ) -> Dict[str, Any]:
        """Get insights and recommendations for agent"""
        
        insights = await self.learning_engine.get_learning_insights(agent_name, time_period)
        
        # Add processing stats
        insights["processing_stats"] = self.processing_stats
        
        return insights
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get notifications for user"""
        
        notifications = await self.notification_system.get_user_notifications(
            user_id, limit, unread_only
        )
        
        return [notification.dict() for notification in notifications]
    
    async def mark_notification_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Mark notification as read"""
        
        return await self.notification_system.mark_notification_read(
            notification_id, user_id
        )
    
    async def generate_weekly_digest(
        self,
        user_id: str,
        week_start: datetime
    ) -> Dict[str, Any]:
        """Generate weekly digest for user"""
        
        digest = await self.notification_system.generate_weekly_digest(
            user_id, week_start
        )
        
        return digest.dict()
    
    async def _background_processor(self) -> None:
        """Background processor for queued items"""
        
        while self.is_running:
            try:
                # Process leave applications
                if self.leave_queue:
                    leave_id = self.leave_queue.pop(0)
                    db = next(get_db())
                    await self.process_leave_application(leave_id, db)
                
                # Process timesheets
                if self.timesheet_queue:
                    timesheet_id = self.timesheet_queue.pop(0)
                    db = next(get_db())
                    await self.process_timesheet(timesheet_id, db)
                
                # Sleep if no items to process
                if not self.leave_queue and not self.timesheet_queue:
                    await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in background processor: {str(e)}")
                await asyncio.sleep(10)
    
    async def _weekly_digest_scheduler(self) -> None:
        """Scheduler for weekly digest generation"""
        
        while self.is_running:
            try:
                # Calculate next Monday
                now = datetime.utcnow()
                days_until_monday = (7 - now.weekday()) % 7
                next_monday = now + timedelta(days=days_until_monday)
                next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
                
                # Wait until next Monday
                wait_seconds = (next_monday - now).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                
                # Generate digests for all users
                await self._generate_all_weekly_digests()
                
                # Wait a week
                await asyncio.sleep(7 * 24 * 60 * 60)
                
            except Exception as e:
                self.logger.error(f"Error in weekly digest scheduler: {str(e)}")
                await asyncio.sleep(60 * 60)  # Wait an hour on error
    
    async def _generate_all_weekly_digests(self) -> None:
        """Generate weekly digests for all users"""
        
        # TODO: Get all active users and generate digests
        self.logger.info("Generating weekly digests for all users")
    
    async def _send_leave_notifications(
        self, 
        decision: AgentDecision, 
        db: Session
    ) -> int:
        """Send leave-related notifications"""
        
        notifications_sent = 0
        
        try:
            # Get leave data
            leave_data = await self._get_leave_data(decision.entity_id, db)
            
            if leave_data:
                # Send to employee
                await self.notification_system.create_leave_notification(
                    leave_data["employee_id"], decision, leave_data
                )
                notifications_sent += 1
                
                # Send to manager if escalated
                if decision.decision == DecisionStatus.ESCALATED:
                    manager_id = leave_data.get("manager_id")
                    if manager_id:
                        await self.notification_system.create_notification(
                            str(manager_id),
                            "leave_escalated_manager",
                            "Leave Requires Approval",
                            f"Leave application from {leave_data.get('employee_name', 'Employee')} requires your approval.",
                            {"leave_data": leave_data, "decision": decision.dict()}
                        )
                        notifications_sent += 1
            
        except Exception as e:
            self.logger.error(f"Error sending leave notifications: {str(e)}")
        
        return notifications_sent
    
    async def _send_timesheet_notifications(
        self, 
        decision: AgentDecision, 
        db: Session
    ) -> int:
        """Send timesheet-related notifications"""
        
        notifications_sent = 0
        
        try:
            # Get timesheet data
            timesheet_data = await self._get_timesheet_data(decision.entity_id, db)
            
            if timesheet_data:
                # Send to employee
                await self.notification_system.create_timesheet_notification(
                    timesheet_data["employee_id"], decision, timesheet_data
                )
                notifications_sent += 1
                
                # Send to manager if flagged
                if decision.decision == DecisionStatus.FLAGGED:
                    manager_id = timesheet_data.get("manager_id")
                    if manager_id:
                        await self.notification_system.create_notification(
                            str(manager_id),
                            "timesheet_flagged_manager",
                            "Timesheet Flagged",
                            f"Timesheet from {timesheet_data.get('employee_name', 'Employee')} has been flagged for review.",
                            {"timesheet_data": timesheet_data, "decision": decision.dict()}
                        )
                        notifications_sent += 1
            
        except Exception as e:
            self.logger.error(f"Error sending timesheet notifications: {str(e)}")
        
        return notifications_sent
    
    async def _get_leave_data(self, leave_application_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Get leave application data"""
        # TODO: Implement database query
        return {
            "employee_id": 1,
            "employee_name": "John Doe",
            "manager_id": 2,
            "number_of_days": 3,
            "leave_type": "pto"
        }
    
    async def _get_timesheet_data(self, timesheet_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Get timesheet data"""
        # TODO: Implement database query
        return {
            "employee_id": 1,
            "employee_name": "John Doe",
            "manager_id": 2,
            "total_hours": 42.5
        }
    
    def _update_processing_stats(self, success: bool, processing_time: float) -> None:
        """Update processing statistics"""
        
        self.processing_stats["total_processed"] += 1
        
        if success:
            self.processing_stats["successful_decisions"] += 1
        else:
            self.processing_stats["failed_decisions"] += 1
        
        # Update average processing time
        current_avg = self.processing_stats["average_processing_time"]
        total_processed = self.processing_stats["total_processed"]
        
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total_processed - 1) + processing_time) / total_processed
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and statistics"""
        
        return {
            "is_running": self.is_running,
            "processing_stats": self.processing_stats,
            "queue_sizes": {
                "leave_queue": len(self.leave_queue),
                "timesheet_queue": len(self.timesheet_queue)
            },
            "config": self.config.dict()
        }
    
    async def queue_leave_processing(self, leave_application_id: int) -> None:
        """Queue leave application for processing"""
        
        if leave_application_id not in self.leave_queue:
            self.leave_queue.append(leave_application_id)
            self.logger.info(f"Queued leave application {leave_application_id} for processing")
    
    async def queue_timesheet_processing(self, timesheet_id: int) -> None:
        """Queue timesheet for processing"""
        
        if timesheet_id not in self.timesheet_queue:
            self.timesheet_queue.append(timesheet_id)
            self.logger.info(f"Queued timesheet {timesheet_id} for processing")


# Global agent service instance
agent_service = AgentService()
