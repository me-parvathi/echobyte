"""
Database-level locking utilities for preventing race conditions.
This module provides locking mechanisms using SELECT FOR UPDATE to ensure
data consistency during concurrent operations.
"""

import logging
import time
from typing import Optional, Callable, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from api.employee.models import Employee

# Configure logging
logger = logging.getLogger(__name__)


class LockingError(Exception):
    """Custom exception for locking-related errors"""
    pass


class EmployeeLockManager:
    """
    Manages database-level locking for employee records to prevent race conditions.
    Uses SELECT FOR UPDATE to lock employee records during critical operations.
    """
    
    @staticmethod
    def lock_employee_for_update(db: Session, employee_id: int, timeout_seconds: int = 30) -> Optional[Employee]:
        """
        Lock an employee record for update using SELECT FOR UPDATE.
        
        Args:
            db: Database session
            employee_id: ID of the employee to lock
            timeout_seconds: Lock timeout in seconds (default: 30) - not used in SQL Server
        
        Returns:
            Employee object if found and locked, None if not found
            
        Raises:
            LockingError: If lock acquisition fails or times out
        """
        try:
            logger.info(f"Attempting to lock employee {employee_id} for update")
            
            # First, check if employee exists without locking
            check_query = text("""
                SELECT EmployeeID FROM Employees 
                WHERE EmployeeID = :employee_id AND IsActive = 1
            """)
            
            check_result = db.execute(check_query, {
                "employee_id": employee_id
            }).fetchone()
            
            if not check_result:
                logger.warning(f"Employee {employee_id} not found or not active")
                return None
            
            # Now lock the employee record
            query = text("""
                SELECT * FROM Employees WITH (UPDLOCK, ROWLOCK)
                WHERE EmployeeID = :employee_id AND IsActive = 1
            """)
            
            result = db.execute(query, {
                "employee_id": employee_id
            }).fetchone()
            
            if result:
                # Convert result to Employee object
                employee = Employee()
                for column in Employee.__table__.columns:
                    setattr(employee, column.name, getattr(result, column.name))
                
                logger.info(f"Successfully locked employee {employee_id} for update")
                return employee
            else:
                logger.warning(f"Employee {employee_id} not found or not active")
                return None
                
        except Exception as e:
            error_msg = f"Failed to lock employee {employee_id}: {str(e)}"
            logger.error(error_msg)
            
            # SQL Server specific error handling
            if "timeout" in str(e).lower() or "deadlock" in str(e).lower() or "blocked" in str(e).lower():
                raise LockingError(f"Lock acquisition timed out for employee {employee_id}. Please try again.")
            else:
                raise LockingError(f"Database error while locking employee {employee_id}: {str(e)}")
    
    @staticmethod
    def lock_employee_with_retry(
        db: Session, 
        employee_id: int, 
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
        timeout_seconds: int = 30
    ) -> Optional[Employee]:
        """
        Lock an employee record with retry logic for handling temporary lock conflicts.
        
        Args:
            db: Database session
            employee_id: ID of the employee to lock
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay_seconds: Delay between retries in seconds (default: 1.0)
            timeout_seconds: Lock timeout in seconds (default: 30)
            
        Returns:
            Employee object if found and locked, None if not found
            
        Raises:
            LockingError: If lock acquisition fails after all retries
        """
        import time
        
        for attempt in range(max_retries + 1):
            try:
                return EmployeeLockManager.lock_employee_for_update(db, employee_id, timeout_seconds)
                
            except LockingError as e:
                if attempt < max_retries:
                    logger.warning(f"Lock attempt {attempt + 1} failed for employee {employee_id}, retrying in {retry_delay_seconds}s: {str(e)}")
                    time.sleep(retry_delay_seconds)
                    # Increase delay for next retry (exponential backoff)
                    retry_delay_seconds *= 1.5
                else:
                    logger.error(f"All lock attempts failed for employee {employee_id} after {max_retries + 1} tries")
                    raise e
    
    @staticmethod
    @contextmanager
    def employee_lock_context(
        db: Session, 
        employee_id: int, 
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
        timeout_seconds: int = 30
    ):
        """
        Context manager for employee locking that automatically releases the lock.
        
        Usage:
            with EmployeeLockManager.employee_lock_context(db, employee_id) as employee:
                if employee:
                    # Perform operations with locked employee record
                    pass
                else:
                    # Employee not found
                    pass
        
        Args:
            db: Database session
            employee_id: ID of the employee to lock
            max_retries: Maximum number of retry attempts
            retry_delay_seconds: Delay between retries in seconds
            timeout_seconds: Lock timeout in seconds
            
        Yields:
            Employee object if found and locked, None if not found
        """
        employee = None
        try:
            employee = EmployeeLockManager.lock_employee_with_retry(
                db, employee_id, max_retries, retry_delay_seconds, timeout_seconds
            )
            yield employee
            
        except LockingError as e:
            logger.error(f"Lock acquisition failed for employee {employee_id}: {str(e)}")
            raise HTTPException(
                status_code=409, 
                detail=f"Employee record is currently being modified by another request. Please try again in a few moments."
            )
        except Exception as e:
            logger.error(f"Unexpected error during employee locking for {employee_id}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during employee locking")
        finally:
            # Lock is automatically released when the database transaction ends
            # or when the session is closed
            logger.debug(f"Employee lock context ended for employee {employee_id}")


def with_employee_lock(
    max_retries: int = 3,
    retry_delay_seconds: float = 1.0,
    timeout_seconds: int = 30
):
    """
    Decorator for functions that require employee locking.
    
    Usage:
        @with_employee_lock()
        def upload_profile_picture(self, db: Session, employee_id: int, ...):
            # Function will automatically lock the employee record
            pass
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay_seconds: Delay between retries in seconds
        timeout_seconds: Lock timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(self, db: Session, employee_id: int, *args, **kwargs):
            with EmployeeLockManager.employee_lock_context(
                db, employee_id, max_retries, retry_delay_seconds, timeout_seconds
            ) as employee:
                if not employee:
                    raise HTTPException(status_code=404, detail="Employee not found")
                
                # Add the locked employee to kwargs for use in the function
                kwargs['locked_employee'] = employee
                return await func(self, db, employee_id, *args, **kwargs)
        
        return wrapper
    return decorator 