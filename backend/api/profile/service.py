from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from fastapi import HTTPException, UploadFile
from . import models, schemas
from api.employee.models import Employee
from core.azure_storage import AzureStorageService
from core.constants import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES
from core.locking import EmployeeLockManager, with_employee_lock
from core.exceptions import (
    AzureConnectionError, AzureUploadError, FileValidationError, BlobCollisionError,
    DatabaseConstraintError, EmployeeNotFoundError, UploadRollbackError,
    handle_azure_error, handle_database_error, handle_validation_error, create_error_response
)

# Configure logging
logger = logging.getLogger(__name__)


class ProfilePictureService:
    """
    Service class for handling profile picture operations.
    Manages both Azure Blob Storage and database operations with employee locking.
    """
    
    def __init__(self):
        """Initialize the service with Azure Storage client"""
        self.azure_storage = AzureStorageService()
    
    @staticmethod
    def validate_employee_id(db: Session, employee_id: int) -> bool:
        """Validate that employee ID exists and is active"""
        employee = db.query(Employee).filter(
            Employee.EmployeeID == employee_id,
            Employee.IsActive == True
        ).first()
        return employee is not None
    
    @staticmethod
    def get_profile_picture(db: Session, picture_id: int) -> Optional[models.ProfilePicture]:
        """Get a specific profile picture by ID"""
        return db.query(models.ProfilePicture).filter(
            models.ProfilePicture.PictureID == picture_id
        ).first()
    
    @staticmethod
    def get_employee_profile_pictures(db: Session, employee_id: int) -> List[models.ProfilePicture]:
        """Get all profile pictures for an employee"""
        return db.query(models.ProfilePicture).filter(
            models.ProfilePicture.EmployeeID == employee_id
        ).order_by(models.ProfilePicture.UploadedAt.desc()).all()
    
    @staticmethod
    def get_latest_profile_picture(db: Session, employee_id: int) -> Optional[models.ProfilePicture]:
        """Get the most recent profile picture for an employee"""
        return db.query(models.ProfilePicture).filter(
            models.ProfilePicture.EmployeeID == employee_id
        ).order_by(models.ProfilePicture.UploadedAt.desc()).first()
    
    # Temporarily disabled locking for debugging
    # @with_employee_lock(max_retries=3, retry_delay_seconds=1.0, timeout_seconds=30)
    async def upload_profile_picture(
        self, 
        db: Session, 
        employee_id: int, 
        uploaded_by_id: int, 
        file: UploadFile,
        locked_employee: Employee = None
    ) -> schemas.ProfilePictureUploadResponse:
        """
        Upload a profile picture for an employee with employee record locking.
        Handles both Azure storage upload and database record creation with proper rollback.
        
        Implementation follows the pattern:
        1. Lock employee record to prevent race conditions
        2. Upload to Azure first
        3. If database operation fails, automatically delete Azure file
        4. Log all cleanup operations
        5. Ensure no orphaned files remain
        
        Args:
            db: Database session
            employee_id: Employee ID for whom to upload the picture
            uploaded_by_id: Employee ID who is uploading the picture
            file: UploadFile object containing the image
            locked_employee: Employee object (locked by decorator)
            
        Returns:
            ProfilePictureUploadResponse with upload details
            
        Raises:
            HTTPException: If upload fails, validation fails, or employee is locked
        """
        azure_result = None
        blob_name = None
        error_context = {
            "operation": "profile_picture_upload",
            "timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "uploaded_by_id": uploaded_by_id,
            "file_name": file.filename if file else None,
            "content_type": file.content_type if file else None
        }
        
        try:
            # Validate employee exists (since locking is disabled)
            if not self.validate_employee_id(db, employee_id):
                raise HTTPException(status_code=404, detail="Employee not found")
            
            logger.info(f"Employee {employee_id} validated for profile picture upload")
            
            # Validate uploader exists
            try:
                if not self.validate_employee_id(db, uploaded_by_id):
                    raise EmployeeNotFoundError(uploaded_by_id, "Uploader not found")
            except Exception as e:
                error_context["validation_error"] = "uploader_not_found"
                logger.error(f"Uploader validation failed: {create_error_response(e, error_context)}")
                raise HTTPException(status_code=404, detail="Uploader not found")
            
            # Validate file using Azure storage service
            try:
                self.azure_storage._validate_file(file)
            except FileValidationError as e:
                error_context["validation_error"] = e.validation_type
                error_context["validation_details"] = e.details
                logger.error(f"File validation failed: {create_error_response(e, error_context)}")
                raise handle_validation_error(e, e.validation_type, e.details)
            
            # Step 1: Upload to Azure Blob Storage first
            logger.info(f"Starting Azure upload for employee {employee_id}")
            try:
                azure_result = await self.azure_storage.upload_profile_picture(employee_id, file)
            except FileValidationError as e:
                error_context["azure_error"] = "file_validation"
                logger.error(f"Azure file validation failed: {create_error_response(e, error_context)}")
                raise handle_validation_error(e, e.validation_type, e.details)
            except AzureUploadError as e:
                error_context["azure_error"] = "upload_failed"
                error_context["blob_name"] = e.blob_name
                logger.error(f"Azure upload failed: {create_error_response(e, error_context)}")
                raise handle_azure_error(e, "profile picture upload", e.details)
            except BlobCollisionError as e:
                error_context["azure_error"] = "blob_collision"
                error_context["blob_name"] = e.blob_name
                error_context["attempts"] = e.attempts
                error_context["max_attempts"] = e.max_attempts
                logger.error(f"Blob collision after all retries: {create_error_response(e, error_context)}")
                raise HTTPException(
                    status_code=409,
                    detail="Unable to upload file due to naming conflict. Please try again."
                )
            except AzureConnectionError as e:
                error_context["azure_error"] = "connection_failed"
                logger.error(f"Azure connection failed: {create_error_response(e, error_context)}")
                raise handle_azure_error(e, "profile picture upload", e.details)
            
            if not azure_result.get("success"):
                error_context["azure_error"] = "upload_failed"
                error_context["azure_result"] = azure_result
                logger.error(f"Azure upload returned failure: {create_error_response(Exception('Azure upload failed'), error_context)}")
                raise HTTPException(status_code=500, detail="Failed to upload to Azure Storage")
            
            blob_name = azure_result["blob_name"]
            logger.info(f"Successfully uploaded to Azure: {blob_name}")
            
            # Step 2: Create database record
            try:
                profile_picture = models.ProfilePicture(
                    EmployeeID=employee_id,
                    UploadedByID=uploaded_by_id,
                    FileName=azure_result["blob_name"].split("/")[-1],  # Extract filename from blob name
                    FilePath=azure_result["blob_url"],
                    FileSize=azure_result["file_size"],
                    MimeType=azure_result["content_type"]
                )
                
                db.add(profile_picture)
                db.commit()
                db.refresh(profile_picture)
                
                logger.info(f"Successfully created database record for profile picture: {blob_name}")
                
                return schemas.ProfilePictureUploadResponse(
                    success=True,
                    blob_name=azure_result["blob_name"],
                    blob_url=azure_result["blob_url"],
                    file_size=azure_result["file_size"],
                    content_type=azure_result["content_type"],
                    metadata=azure_result["metadata"],
                    picture_id=profile_picture.PictureID
                )
                
            except Exception as db_error:
                # Step 3: Database operation failed - rollback and cleanup Azure file
                error_context["database_error"] = str(db_error)
                error_context["blob_name"] = blob_name
                logger.error(f"Database operation failed for employee {employee_id}, blob {blob_name}: {create_error_response(db_error, error_context)}")
                
                # Rollback database changes
                try:
                    db.rollback()
                except Exception as rollback_error:
                    logger.error(f"Database rollback failed: {str(rollback_error)}")
                
                # Cleanup: Delete the Azure file that was successfully uploaded
                if blob_name:
                    try:
                        logger.info(f"Cleaning up orphaned Azure file: {blob_name}")
                        cleanup_result = self.azure_storage.delete_profile_picture(blob_name)
                        
                        if cleanup_result.get("success"):
                            logger.info(f"Successfully cleaned up orphaned Azure file: {blob_name}")
                        else:
                            logger.error(f"Failed to cleanup orphaned Azure file: {blob_name}. Manual cleanup may be required.")
                            # Log additional details for manual cleanup
                            logger.error(f"Manual cleanup required - Blob name: {blob_name}, Employee ID: {employee_id}")
                    except Exception as cleanup_error:
                        logger.error(f"Error during Azure file cleanup: {str(cleanup_error)}")
                        logger.error(f"Manual cleanup required - Blob name: {blob_name}, Employee ID: {employee_id}")
                
                # Convert database error to appropriate HTTP exception
                raise handle_database_error(db_error, "profile picture record creation")
            
        except HTTPException:
            # Re-raise HTTP exceptions (validation errors, etc.)
            raise
        except Exception as e:
            # Handle any other unexpected errors
            error_context["unexpected_error"] = str(e)
            logger.error(f"Unexpected error uploading profile picture for employee {employee_id}: {create_error_response(e, error_context)}")
            
            # If we have a blob name but haven't handled cleanup yet, clean it up
            if blob_name and azure_result and azure_result.get("success"):
                try:
                    logger.info(f"Cleaning up Azure file due to unexpected error: {blob_name}")
                    cleanup_result = self.azure_storage.delete_profile_picture(blob_name)
                    
                    if cleanup_result.get("success"):
                        logger.info(f"Successfully cleaned up Azure file after unexpected error: {blob_name}")
                    else:
                        logger.error(f"Failed to cleanup Azure file after unexpected error: {blob_name}")
                except Exception as cleanup_error:
                    logger.error(f"Error during cleanup after unexpected error: {str(cleanup_error)}")
            
            # Rollback any database changes
            try:
                db.rollback()
            except Exception as rollback_error:
                logger.error(f"Database rollback failed after unexpected error: {str(rollback_error)}")
            
            raise HTTPException(status_code=500, detail="Failed to upload profile picture")
    
    def delete_profile_picture(self, db: Session, picture_id: int) -> schemas.ProfilePictureDeleteResponse:
        """
        Delete a profile picture from both Azure storage and database with employee locking.
        
        Args:
            db: Database session
            picture_id: ID of the profile picture to delete
            
        Returns:
            ProfilePictureDeleteResponse with deletion details
            
        Raises:
            HTTPException: If picture not found or deletion fails
        """
        try:
            # Get the profile picture record first
            profile_picture = self.get_profile_picture(db, picture_id)
            
            if not profile_picture:
                raise HTTPException(status_code=404, detail="Profile picture not found")
            
            # Lock the employee record for this operation
            with EmployeeLockManager.employee_lock_context(db, profile_picture.EmployeeID) as locked_employee:
                if not locked_employee:
                    raise HTTPException(status_code=404, detail="Employee not found")
                
                logger.info(f"Employee {profile_picture.EmployeeID} is locked for profile picture deletion")
                
                # Extract blob name from file path
                blob_name = profile_picture.FilePath.split("/")[-1]
                if not blob_name:
                    # If we can't extract blob name, try to construct it from the database record
                    blob_name = f"profile-pictures/{profile_picture.EmployeeID}/{profile_picture.FileName}"
                
                # Delete from Azure storage
                azure_result = self.azure_storage.delete_profile_picture(blob_name)
                
                # Delete from database
                db.delete(profile_picture)
                db.commit()
                
                logger.info(f"Successfully deleted profile picture {picture_id}: {blob_name}")
                
                return schemas.ProfilePictureDeleteResponse(
                    success=True,
                    message="Profile picture deleted successfully",
                    blob_name=blob_name,
                    picture_id=picture_id
                )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Rollback database changes if any were made
            db.rollback()
            logger.error(f"Error deleting profile picture {picture_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete profile picture")
    
    @with_employee_lock(max_retries=3, retry_delay_seconds=1.0, timeout_seconds=30)
    def delete_employee_profile_pictures(self, db: Session, employee_id: int, locked_employee: Employee = None) -> Dict[str, Any]:
        """
        Delete all profile pictures for an employee with employee locking.
        
        Args:
            db: Database session
            employee_id: Employee ID whose pictures should be deleted
            locked_employee: Employee object (locked by decorator)
            
        Returns:
            Dict with deletion results
        """
        try:
            logger.info(f"Employee {employee_id} is locked for bulk profile picture deletion")
            
            # Get all profile pictures for the employee
            profile_pictures = self.get_employee_profile_pictures(db, employee_id)
            
            if not profile_pictures:
                return {
                    "success": True,
                    "message": "No profile pictures found for employee",
                    "deleted_count": 0,
                    "employee_id": employee_id
                }
            
            deleted_count = 0
            failed_count = 0
            
            for picture in profile_pictures:
                try:
                    # Extract blob name from file path
                    blob_name = picture.FilePath.split("/")[-1]
                    if not blob_name:
                        blob_name = f"profile-pictures/{picture.EmployeeID}/{picture.FileName}"
                    
                    # Delete from Azure storage
                    azure_result = self.azure_storage.delete_profile_picture(blob_name)
                    
                    # Delete from database
                    db.delete(picture)
                    deleted_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to delete profile picture {picture.PictureID}: {str(e)}")
            
            # Commit all database changes
            db.commit()
            
            logger.info(f"Deleted {deleted_count} profile pictures for employee {employee_id}")
            
            return {
                "success": True,
                "message": f"Deleted {deleted_count} profile pictures",
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "employee_id": employee_id
            }
            
        except Exception as e:
            # Rollback database changes if any were made
            db.rollback()
            logger.error(f"Error deleting profile pictures for employee {employee_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete employee profile pictures")
    
    def get_profile_picture_with_azure_info(self, db: Session, picture_id: int) -> Optional[Dict[str, Any]]:
        """
        Get profile picture with additional Azure storage information.
        
        Args:
            db: Database session
            picture_id: ID of the profile picture
            
        Returns:
            Dict with profile picture data and Azure metadata, or None if not found
        """
        profile_picture = self.get_profile_picture(db, picture_id)
        
        if not profile_picture:
            return None
        
        # Get Azure metadata
        blob_name = profile_picture.FilePath.split("/")[-1]
        if not blob_name:
            blob_name = f"profile-pictures/{profile_picture.EmployeeID}/{profile_picture.FileName}"
        
        azure_metadata = self.azure_storage.get_blob_metadata(blob_name)
        
        return {
            "picture": profile_picture,
            "azure_metadata": azure_metadata
        }
    
    def test_azure_connection(self) -> Dict[str, Any]:
        """
        Test Azure Storage connection.
        
        Returns:
            Dict with connection test results
        """
        return self.azure_storage.test_connection() 

    def cleanup_orphaned_profile_pictures(self, db: Session) -> Dict[str, Any]:
        """
        Clean up orphaned profile pictures in Azure that don't exist in the database.
        
        Args:
            db: Database session
            
        Returns:
            Dict with cleanup results
        """
        try:
            logger.info("Starting orphaned profile picture cleanup")
            
            # Get all profile pictures from database
            profile_pictures = db.query(models.ProfilePicture).all()
            
            # Convert to list of dictionaries for the cleanup utility
            db_pictures = []
            for picture in profile_pictures:
                db_pictures.append({
                    'PictureID': picture.PictureID,
                    'EmployeeID': picture.EmployeeID,
                    'FilePath': picture.FilePath,
                    'FileName': picture.FileName
                })
            
            # Use Azure storage service to clean up orphaned files
            cleanup_result = self.azure_storage.cleanup_orphaned_profile_pictures(db_pictures)
            
            if cleanup_result.get("success"):
                logger.info(f"Orphaned cleanup completed successfully. Cleaned: {cleanup_result.get('cleaned_count', 0)} files")
            else:
                logger.error(f"Orphaned cleanup failed: {cleanup_result.get('message', 'Unknown error')}")
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"Error during orphaned profile picture cleanup: {str(e)}")
            return {
                "success": False,
                "message": f"Cleanup error: {str(e)}"
            } 