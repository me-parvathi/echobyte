"""
Azure Blob Storage service for handling file operations.
This module provides Azure Blob Storage operations for profile pictures and other file uploads.
"""

import os
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from io import BytesIO

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from azure.core.exceptions import AzureError, ResourceNotFoundError, ResourceExistsError
from fastapi import HTTPException, UploadFile

# Configure logging
logger = logging.getLogger(__name__)

from .constants import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES, PROFILE_PICTURE_BLOB_PREFIX, PROFILE_PICTURE_CACHE_CONTROL
from .exceptions import (
    AzureConnectionError, AzureUploadError, FileValidationError, BlobCollisionError,
    handle_azure_error, handle_validation_error, create_error_response
)


class AzureStorageService:
    """
    Azure Blob Storage service for handling file operations.
    Provides methods for uploading, deleting, and managing profile pictures.
    """
    
    def __init__(self):
        """Initialize Azure Storage service with configuration from environment variables."""
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER")
        
        if not self.connection_string:
            raise AzureConnectionError("AZURE_STORAGE_CONNECTION_STRING environment variable is required")
        
        if not self.container_name:
            raise AzureConnectionError("AZURE_STORAGE_CONTAINER environment variable is required")
        
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            logger.info(f"Azure Storage service initialized with container: {self.container_name}")
        except Exception as e:
            error_context = {
                "operation": "azure_storage_initialization",
                "timestamp": datetime.utcnow().isoformat(),
                "connection_string_provided": bool(self.connection_string),
                "container_name_provided": bool(self.container_name)
            }
            logger.error(f"Failed to initialize Azure Storage service: {create_error_response(e, error_context)}")
            raise AzureConnectionError(f"Failed to initialize Azure Storage service: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file for size and type.
        
        Args:
            file: UploadFile object to validate
            
        Raises:
            FileValidationError: If file validation fails
        """
        try:
            if not file:
                raise FileValidationError("No file provided", "file_missing")
            
            # Check file size
            if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
                raise FileValidationError(
                    f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
                    "file_size_exceeded",
                    {"file_size": file.size, "max_size": MAX_FILE_SIZE}
                )
            
            # Check file type
            if file.content_type not in ALLOWED_IMAGE_TYPES:
                raise FileValidationError(
                    f"File type not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
                    "file_type_not_allowed",
                    {"content_type": file.content_type, "allowed_types": ALLOWED_IMAGE_TYPES}
                )
                
        except FileValidationError:
            raise
        except Exception as e:
            error_context = {
                "operation": "file_validation",
                "timestamp": datetime.utcnow().isoformat(),
                "file_name": file.filename if file else None,
                "file_size": file.size if file else None,
                "content_type": file.content_type if file else None
            }
            logger.error(f"Unexpected error during file validation: {create_error_response(e, error_context)}")
            raise FileValidationError(f"File validation failed: {str(e)}", "validation_error")
    
    def _generate_blob_name(self, employee_id: int, file_extension: str, retry_count: int = 0) -> str:
        """
        Generate a unique blob name for profile picture with collision resistance.
        
        Uses timestamp + counter + UUID to ensure uniqueness even with high-frequency uploads.
        
        Args:
            employee_id: Employee ID
            file_extension: File extension (e.g., 'jpg', 'png')
            retry_count: Current retry attempt (for collision handling)
            
        Returns:
            str: Generated blob name
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds
        unique_id = str(uuid.uuid4())[:12]  # Use more UUID characters for uniqueness
        counter = f"r{retry_count}" if retry_count > 0 else ""
        
        return f"{PROFILE_PICTURE_BLOB_PREFIX}/{employee_id}/{timestamp}_{unique_id}{counter}.{file_extension}"
    
    def _check_blob_exists(self, blob_name: str) -> bool:
        """
        Check if a blob already exists in Azure storage.
        
        Args:
            blob_name: Name of the blob to check
            
        Returns:
            bool: True if blob exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception as e:
            logger.warning(f"Error checking blob existence for {blob_name}: {str(e)}")
            return False
    
    def _upload_blob_with_retry(
        self, 
        blob_name: str, 
        file_content: bytes, 
        metadata: Dict[str, str], 
        content_type: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Upload blob with retry logic for collision handling.
        
        Args:
            blob_name: Name of the blob to upload
            file_content: File content as bytes
            metadata: Blob metadata
            content_type: MIME content type
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict containing upload result
            
        Raises:
            AzureUploadError: If upload fails after all retries
            BlobCollisionError: If blob collision persists after all retries
        """
        last_error = None
        employee_id = metadata.get('employee_id', 'unknown')
        
        for attempt in range(max_retries + 1):
            try:
                blob_client = self.container_client.get_blob_client(blob_name)
                
                # Check if blob already exists (for collision detection)
                try:
                    if self._check_blob_exists(blob_name):
                        if attempt < max_retries:
                            logger.warning(f"Blob collision detected for {blob_name}, attempt {attempt + 1}/{max_retries + 1}")
                            # Generate new blob name for next attempt
                            file_extension = blob_name.split('.')[-1]
                            blob_name = self._generate_blob_name(int(employee_id), file_extension, attempt + 1)
                            continue
                        else:
                            raise BlobCollisionError(blob_name, attempt + 1, max_retries)
                except Exception as e:
                    logger.warning(f"Error checking blob existence for {blob_name}: {str(e)}")
                    # Continue with upload attempt even if existence check fails
                
                # Upload blob with metadata
                blob_client.upload_blob(
                    file_content,
                    overwrite=False,  # Don't overwrite existing blobs
                    metadata=metadata,
                    content_settings=ContentSettings(
                        content_type=content_type,
                        cache_control=PROFILE_PICTURE_CACHE_CONTROL
                    )
                )
                
                # Get blob URL
                blob_url = blob_client.url
                
                logger.info(f"Successfully uploaded blob: {blob_name} (attempt {attempt + 1})")
                
                return {
                    "success": True,
                    "blob_name": blob_name,
                    "blob_url": blob_url,
                    "attempts": attempt + 1
                }
                
            except BlobCollisionError:
                raise
            except AzureError as e:
                last_error = e
                error_context = {
                    "operation": "azure_blob_upload",
                    "timestamp": datetime.utcnow().isoformat(),
                    "employee_id": employee_id,
                    "blob_name": blob_name,
                    "attempt": attempt + 1,
                    "max_attempts": max_retries + 1,
                    "file_size": len(file_content)
                }
                logger.warning(f"Azure upload attempt {attempt + 1} failed for {blob_name}: {create_error_response(e, error_context)}")
                
                if attempt < max_retries:
                    # Wait before retry (exponential backoff)
                    import time
                    time.sleep(0.1 * (2 ** attempt))  # 0.1s, 0.2s, 0.4s
                    
                    # Generate new blob name for next attempt
                    file_extension = blob_name.split('.')[-1]
                    blob_name = self._generate_blob_name(int(employee_id), file_extension, attempt + 1)
                else:
                    logger.error(f"All upload attempts failed for blob {blob_name}")
                    break
            except Exception as e:
                last_error = e
                error_context = {
                    "operation": "blob_upload",
                    "timestamp": datetime.utcnow().isoformat(),
                    "employee_id": employee_id,
                    "blob_name": blob_name,
                    "attempt": attempt + 1,
                    "max_attempts": max_retries + 1,
                    "file_size": len(file_content)
                }
                logger.error(f"Unexpected error during upload attempt {attempt + 1} for {blob_name}: {create_error_response(e, error_context)}")
                
                if attempt < max_retries:
                    # Wait before retry (exponential backoff)
                    import time
                    time.sleep(0.1 * (2 ** attempt))
                    
                    # Generate new blob name for next attempt
                    file_extension = blob_name.split('.')[-1]
                    blob_name = self._generate_blob_name(int(employee_id), file_extension, attempt + 1)
                else:
                    logger.error(f"All upload attempts failed for blob {blob_name}")
                    break
        
        # All retries failed
        error_context = {
            "operation": "blob_upload_final_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "blob_name": blob_name,
            "total_attempts": max_retries + 1,
            "file_size": len(file_content),
            "last_error": str(last_error) if last_error else "Unknown error"
        }
        logger.error(f"Failed to upload blob after {max_retries + 1} attempts: {create_error_response(last_error or Exception('Upload failed'), error_context)}")
        
        if isinstance(last_error, BlobCollisionError):
            raise last_error
        else:
            raise AzureUploadError(f"Failed to upload blob after {max_retries + 1} attempts. Last error: {str(last_error)}", blob_name)
    
    def _get_file_extension(self, content_type: str) -> str:
        """
        Extract file extension from content type.
        
        Args:
            content_type: MIME content type
            
        Returns:
            str: File extension
        """
        content_type_map = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp'
        }
        return content_type_map.get(content_type, 'jpg')
    
    async def upload_profile_picture(self, employee_id: int, file: UploadFile) -> Dict[str, Any]:
        """
        Upload a profile picture for an employee.
        
        Args:
            employee_id: Employee ID
            file: UploadFile object containing the image
            
        Returns:
            Dict containing upload result with blob URL and metadata
            
        Raises:
            FileValidationError: If file validation fails
            AzureUploadError: If Azure upload fails
            BlobCollisionError: If blob collision persists after retries
        """
        error_context = {
            "operation": "profile_picture_upload",
            "timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "file_name": file.filename if file else None,
            "content_type": file.content_type if file else None
        }
        
        try:
            # Validate file
            try:
                self._validate_file(file)
            except FileValidationError as e:
                error_context["validation_error"] = e.validation_type
                error_context["validation_details"] = e.details
                logger.error(f"File validation failed: {create_error_response(e, error_context)}")
                raise
            
            # Generate blob name
            file_extension = self._get_file_extension(file.content_type)
            blob_name = self._generate_blob_name(employee_id, file_extension)
            
            # Read file content
            try:
                file_content = await file.read()
            except Exception as e:
                error_context["file_read_error"] = str(e)
                logger.error(f"Failed to read file content: {create_error_response(e, error_context)}")
                raise FileValidationError(f"Failed to read file content: {str(e)}", "file_read_error")
            
            # Check file size after reading
            if len(file_content) > MAX_FILE_SIZE:
                error_context["file_size"] = len(file_content)
                error_context["max_size"] = MAX_FILE_SIZE
                raise FileValidationError(
                    f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
                    "file_size_exceeded",
                    {"file_size": len(file_content), "max_size": MAX_FILE_SIZE}
                )
            
            # Upload to Azure Blob Storage
            metadata = {
                'employee_id': str(employee_id),
                'upload_date': datetime.utcnow().isoformat(),
                'content_type': file.content_type,
                'original_filename': file.filename
            }
            
            try:
                upload_result = self._upload_blob_with_retry(
                    blob_name=blob_name,
                    file_content=file_content,
                    metadata=metadata,
                    content_type=file.content_type
                )
            except (AzureUploadError, BlobCollisionError) as e:
                error_context["upload_error"] = str(e)
                error_context["blob_name"] = blob_name
                error_context["file_size"] = len(file_content)
                logger.error(f"Azure upload failed: {create_error_response(e, error_context)}")
                raise
            
            logger.info(f"Successfully uploaded profile picture for employee {employee_id}: {upload_result['blob_name']}")
            
            return {
                "success": True,
                "blob_name": upload_result["blob_name"],
                "blob_url": upload_result["blob_url"],
                "file_size": len(file_content),
                "content_type": file.content_type,
                "metadata": metadata,
                "upload_attempts": upload_result.get("attempts", 1)
            }
            
        except (FileValidationError, AzureUploadError, BlobCollisionError):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            # Handle any other unexpected errors
            error_context["unexpected_error"] = str(e)
            logger.error(f"Unexpected error during profile picture upload: {create_error_response(e, error_context)}")
            raise AzureUploadError(f"An unexpected error occurred during upload: {str(e)}", blob_name if 'blob_name' in locals() else None)
    
    def delete_profile_picture(self, blob_name: str) -> Dict[str, Any]:
        """
        Delete a profile picture from Azure Blob Storage.
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            Dict containing deletion result
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            logger.info(f"Attempting to delete blob: {blob_name}")
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Check if blob exists
            if not blob_client.exists():
                logger.warning(f"Blob not found for deletion: {blob_name}")
                return {
                    "success": False,
                    "message": "Blob not found",
                    "blob_name": blob_name
                }
            
            # Delete blob
            blob_client.delete_blob()
            
            logger.info(f"Successfully deleted blob: {blob_name}")
            
            return {
                "success": True,
                "message": "Blob deleted successfully",
                "blob_name": blob_name
            }
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {blob_name}")
            return {
                "success": False,
                "message": "Blob not found",
                "blob_name": blob_name
            }
        except AzureError as e:
            logger.error(f"Azure Storage error during deletion of {blob_name}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete file from Azure Storage")
        except Exception as e:
            logger.error(f"Unexpected error during deletion of {blob_name}: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during deletion")
    
    def delete_employee_profile_pictures(self, employee_id: int) -> Dict[str, Any]:
        """
        Delete all profile pictures for a specific employee.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Dict containing deletion results
        """
        try:
            # List all blobs for the employee
            prefix = f"profile-pictures/{employee_id}/"
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            
            deleted_count = 0
            failed_count = 0
            deleted_blobs = []
            
            for blob in blobs:
                try:
                    blob_client = self.container_client.get_blob_client(blob.name)
                    blob_client.delete_blob()
                    deleted_count += 1
                    deleted_blobs.append(blob.name)
                    logger.info(f"Deleted blob: {blob.name}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to delete blob {blob.name}: {str(e)}")
            
            return {
                "success": True,
                "employee_id": employee_id,
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "deleted_blobs": deleted_blobs
            }
            
        except AzureError as e:
            logger.error(f"Azure Storage error during bulk deletion: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete employee profile pictures")
        except Exception as e:
            logger.error(f"Unexpected error during bulk deletion: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during bulk deletion")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Azure Storage connection and container access.
        
        Returns:
            Dict containing connection test results
        """
        try:
            # Test basic connection
            account_info = self.blob_service_client.get_account_information()
            
            # Test container access
            container_properties = self.container_client.get_container_properties()
            
            # Test blob operations with a test blob
            test_blob_name = f"test-connection-{uuid.uuid4()}"
            test_blob_client = self.container_client.get_blob_client(test_blob_name)
            
            # Upload test data
            test_data = b"test-connection-data"
            test_blob_client.upload_blob(test_data, overwrite=True)
            
            # Download and verify
            downloaded_data = test_blob_client.download_blob().readall()
            
            # Clean up test blob
            test_blob_client.delete_blob()
            
            if downloaded_data == test_data:
                logger.info("Azure Storage connection test successful")
                return {
                    "success": True,
                    "message": "Connection test successful",
                    "account_name": account_info.get('account_name', 'Unknown'),
                    "container_name": self.container_name,
                    "container_properties": {
                        "name": container_properties.name,
                        "last_modified": container_properties.last_modified.isoformat() if container_properties.last_modified else None,
                        "etag": container_properties.etag
                    }
                }
            else:
                logger.error("Azure Storage connection test failed - data mismatch")
                return {
                    "success": False,
                    "message": "Connection test failed - data verification failed"
                }
                
        except AzureError as e:
            logger.error(f"Azure Storage connection test failed: {str(e)}")
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "error_type": "AzureError"
            }
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {str(e)}")
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "error_type": "UnexpectedError"
            }
    
    def get_blob_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific blob.
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            Dict containing blob metadata or None if not found
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            properties = blob_client.get_blob_properties()
            
            return {
                "name": blob_name,
                "size": properties.size,
                "content_type": properties.content_settings.content_type,
                "last_modified": properties.last_modified.isoformat() if properties.last_modified else None,
                "etag": properties.etag,
                "metadata": properties.metadata
            }
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found: {blob_name}")
            return None
        except AzureError as e:
            logger.error(f"Azure Storage error getting blob metadata: {str(e)}")
            return None
    
    def get_blob_content(self, blob_name: str) -> Optional[bytes]:
        """
        Get the content of a blob as bytes.
        
        Args:
            blob_name: Name of the blob to get content for
            
        Returns:
            Blob content as bytes or None if not found
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            
            return blob_data.readall()
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found: {blob_name}")
            return None
        except AzureError as e:
            logger.error(f"Azure Storage error getting blob content: {str(e)}")
            return None
    
    def list_employee_profile_pictures(self, employee_id: int) -> List[Dict[str, Any]]:
        """
        List all profile pictures for a specific employee.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            List of blob metadata dictionaries
        """
        try:
            prefix = f"profile-pictures/{employee_id}/"
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            
            profile_pictures = []
            for blob in blobs:
                metadata = self.get_blob_metadata(blob.name)
                if metadata:
                    profile_pictures.append(metadata)
            
            return profile_pictures
            
        except AzureError as e:
            logger.error(f"Azure Storage error listing profile pictures: {str(e)}")
            return [] 

    def cleanup_orphaned_profile_pictures(self, db_profile_pictures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Clean up orphaned profile pictures in Azure that don't exist in the database.
        
        Args:
            db_profile_pictures: List of profile pictures from database with blob names
            
        Returns:
            Dict containing cleanup results
        """
        try:
            logger.info("Starting orphaned profile picture cleanup process")
            
            # Extract blob names from database records
            db_blob_names = set()
            for picture in db_profile_pictures:
                if picture.get('FilePath'):
                    # Extract blob name from file path
                    blob_name = picture['FilePath'].split("/")[-1]
                    if blob_name:
                        db_blob_names.add(blob_name)
            
            logger.info(f"Found {len(db_blob_names)} profile pictures in database")
            
            # List all blobs in Azure
            prefix = f"{PROFILE_PICTURE_BLOB_PREFIX}/"
            azure_blobs = list(self.container_client.list_blobs(name_starts_with=prefix))
            
            logger.info(f"Found {len(azure_blobs)} blobs in Azure storage")
            
            orphaned_blobs = []
            cleaned_count = 0
            failed_count = 0
            
            for blob in azure_blobs:
                blob_name = blob.name.split("/")[-1]  # Extract filename
                
                if blob_name not in db_blob_names:
                    orphaned_blobs.append(blob.name)
                    logger.warning(f"Found orphaned blob: {blob.name}")
                    
                    # Attempt to delete orphaned blob
                    try:
                        delete_result = self.delete_profile_picture(blob.name)
                        if delete_result.get("success"):
                            cleaned_count += 1
                            logger.info(f"Successfully cleaned up orphaned blob: {blob.name}")
                        else:
                            failed_count += 1
                            logger.error(f"Failed to clean up orphaned blob: {blob.name}")
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error cleaning up orphaned blob {blob.name}: {str(e)}")
            
            logger.info(f"Orphaned cleanup complete. Cleaned: {cleaned_count}, Failed: {failed_count}")
            
            return {
                "success": True,
                "total_azure_blobs": len(azure_blobs),
                "total_db_pictures": len(db_blob_names),
                "orphaned_blobs_found": len(orphaned_blobs),
                "cleaned_count": cleaned_count,
                "failed_count": failed_count,
                "orphaned_blobs": orphaned_blobs
            }
            
        except AzureError as e:
            logger.error(f"Azure Storage error during orphaned cleanup: {str(e)}")
            return {
                "success": False,
                "message": f"Azure Storage error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during orphaned cleanup: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            } 

    def test_blob_name_collision(self, employee_id: int, file_extension: str = "jpg", num_names: int = 10) -> List[str]:
        """
        Test blob name generation to check for collisions.
        
        Args:
            employee_id: Employee ID for testing
            file_extension: File extension to use
            num_names: Number of blob names to generate
            
        Returns:
            List of generated blob names
        """
        generated_names = []
        
        for i in range(num_names):
            blob_name = self._generate_blob_name(employee_id, file_extension, i)
            generated_names.append(blob_name)
            
            # Check for collisions in generated names
            if blob_name in generated_names[:-1]:
                logger.warning(f"Collision detected in generated names: {blob_name}")
        
        # Check for uniqueness
        unique_names = set(generated_names)
        if len(unique_names) != len(generated_names):
            logger.error(f"Collision test failed: {len(generated_names)} names generated, {len(unique_names)} unique")
        else:
            logger.info(f"Collision test passed: {len(generated_names)} unique names generated")
        
        return generated_names
    
    def simulate_concurrent_uploads(self, employee_id: int, num_uploads: int = 5) -> Dict[str, Any]:
        """
        Simulate concurrent uploads to test collision handling.
        
        Args:
            employee_id: Employee ID for testing
            num_uploads: Number of concurrent uploads to simulate
            
        Returns:
            Dict with simulation results
        """
        import threading
        import time
        
        results = {
            "successful_uploads": 0,
            "failed_uploads": 0,
            "total_attempts": 0,
            "blob_names": [],
            "errors": []
        }
        
        def simulate_upload():
            try:
                # Generate a test blob name
                file_extension = "jpg"
                blob_name = self._generate_blob_name(employee_id, file_extension)
                
                # Simulate upload attempt
                test_content = b"test_image_data"
                metadata = {
                    'employee_id': str(employee_id),
                    'upload_date': datetime.utcnow().isoformat(),
                    'content_type': 'image/jpeg',
                    'original_filename': 'test.jpg'
                }
                
                # Try to upload (this will fail in test environment, but we can count attempts)
                try:
                    upload_result = self._upload_blob_with_retry(
                        blob_name=blob_name,
                        file_content=test_content,
                        metadata=metadata,
                        content_type='image/jpeg',
                        max_retries=2
                    )
                    results["successful_uploads"] += 1
                    results["blob_names"].append(upload_result["blob_name"])
                    results["total_attempts"] += upload_result.get("attempts", 1)
                    
                except Exception as e:
                    results["failed_uploads"] += 1
                    results["errors"].append(str(e))
                    
            except Exception as e:
                results["failed_uploads"] += 1
                results["errors"].append(str(e))
        
        # Create threads for concurrent uploads
        threads = []
        for i in range(num_uploads):
            thread = threading.Thread(target=simulate_upload)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
            time.sleep(0.01)  # Small delay to ensure concurrent execution
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        logger.info(f"Concurrent upload simulation completed: {results}")
        return results 