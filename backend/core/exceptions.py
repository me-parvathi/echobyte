"""
Custom exceptions for handling different failure scenarios in the upload process.
This module provides specific exception types for different error conditions.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException


class AzureConnectionError(Exception):
    """Raised when Azure Storage connection fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AzureUploadError(Exception):
    """Raised when Azure blob upload fails"""
    
    def __init__(self, message: str, blob_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.blob_name = blob_name
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConstraintError(Exception):
    """Raised when database constraint violations occur"""
    
    def __init__(self, message: str, constraint_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.constraint_type = constraint_type
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(Exception):
    """Raised when file validation fails"""
    
    def __init__(self, message: str, validation_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.validation_type = validation_type
        self.details = details or {}
        super().__init__(self.message)


class EmployeeNotFoundError(Exception):
    """Raised when employee is not found"""
    
    def __init__(self, employee_id: int, message: Optional[str] = None):
        self.employee_id = employee_id
        self.message = message or f"Employee with ID {employee_id} not found"
        super().__init__(self.message)


class BlobCollisionError(Exception):
    """Raised when blob name collision occurs"""
    
    def __init__(self, blob_name: str, attempts: int, max_attempts: int):
        self.blob_name = blob_name
        self.attempts = attempts
        self.max_attempts = max_attempts
        self.message = f"Blob collision after {attempts} attempts (max: {max_attempts})"
        super().__init__(self.message)


class UploadRollbackError(Exception):
    """Raised when rollback operations fail"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, rollback_details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.original_error = original_error
        self.rollback_details = rollback_details or {}
        super().__init__(self.message)


def handle_azure_error(error: Exception, operation: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """
    Handle Azure-related errors and convert to appropriate HTTP exceptions.
    
    Args:
        error: The original Azure error
        operation: Description of the operation that failed
        details: Additional error details
        
    Returns:
        HTTPException with appropriate status code and message
    """
    error_message = str(error)
    
    # Azure connection errors
    if "connection" in error_message.lower() or "timeout" in error_message.lower():
        return HTTPException(
            status_code=503,
            detail=f"Azure Storage service is temporarily unavailable. Please try again later. Operation: {operation}"
        )
    
    # Azure authentication errors
    elif "unauthorized" in error_message.lower() or "authentication" in error_message.lower():
        return HTTPException(
            status_code=500,
            detail="Azure Storage authentication failed. Please contact system administrator."
        )
    
    # Azure permission errors
    elif "forbidden" in error_message.lower() or "permission" in error_message.lower():
        return HTTPException(
            status_code=500,
            detail="Azure Storage permission denied. Please contact system administrator."
        )
    
    # Azure resource not found
    elif "not found" in error_message.lower() or "404" in error_message.lower():
        return HTTPException(
            status_code=500,
            detail="Azure Storage resource not found. Please contact system administrator."
        )
    
    # Azure quota exceeded
    elif "quota" in error_message.lower() or "limit" in error_message.lower():
        return HTTPException(
            status_code=413,
            detail="Storage quota exceeded. Please contact system administrator."
        )
    
    # Generic Azure error
    else:
        return HTTPException(
            status_code=500,
            detail=f"Azure Storage error during {operation}. Please try again later."
        )


def handle_database_error(error: Exception, operation: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """
    Handle database-related errors and convert to appropriate HTTP exceptions.
    
    Args:
        error: The original database error
        operation: Description of the operation that failed
        details: Additional error details
        
    Returns:
        HTTPException with appropriate status code and message
    """
    error_message = str(error)
    
    # Foreign key constraint violations
    if "foreign key" in error_message.lower():
        return HTTPException(
            status_code=400,
            detail="Invalid reference. The employee or related record does not exist."
        )
    
    # Unique constraint violations
    elif "unique" in error_message.lower() or "duplicate" in error_message.lower():
        return HTTPException(
            status_code=409,
            detail="A record with this information already exists."
        )
    
    # Not null constraint violations
    elif "not null" in error_message.lower():
        return HTTPException(
            status_code=400,
            detail="Required information is missing. Please provide all required fields."
        )
    
    # Database connection errors
    elif "connection" in error_message.lower() or "timeout" in error_message.lower():
        return HTTPException(
            status_code=503,
            detail="Database service is temporarily unavailable. Please try again later."
        )
    
    # Generic database error
    else:
        return HTTPException(
            status_code=500,
            detail=f"Database error during {operation}. Please try again later."
        )


def handle_validation_error(error: Exception, validation_type: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """
    Handle validation errors and convert to appropriate HTTP exceptions.
    
    Args:
        error: The original validation error
        validation_type: Type of validation that failed
        details: Additional error details
        
    Returns:
        HTTPException with appropriate status code and message
    """
    error_message = str(error)
    
    # File size validation
    if "size" in validation_type.lower() or "size" in error_message.lower():
        return HTTPException(
            status_code=413,
            detail="File size exceeds the maximum allowed limit. Please choose a smaller file."
        )
    
    # File type validation
    elif "type" in validation_type.lower() or "format" in error_message.lower():
        return HTTPException(
            status_code=400,
            detail="File type not supported. Please upload a valid image file (JPEG, PNG, GIF, WebP)."
        )
    
    # File content validation
    elif "content" in validation_type.lower() or "corrupt" in error_message.lower():
        return HTTPException(
            status_code=400,
            detail="File appears to be corrupted or invalid. Please upload a valid image file."
        )
    
    # Generic validation error
    else:
        return HTTPException(
            status_code=400,
            detail=f"File validation failed: {error_message}"
        )


def create_error_response(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized error response for logging and debugging.
    
    Args:
        error: The original exception
        context: Context information about the error
        
    Returns:
        Dict containing error information
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": context.get("timestamp"),
        "operation": context.get("operation"),
        "user_id": context.get("user_id"),
        "employee_id": context.get("employee_id"),
        "additional_details": context.get("additional_details", {})
    } 