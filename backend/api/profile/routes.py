from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from . import schemas, service
from core.constants import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES
import logging
import requests
from fastapi.responses import StreamingResponse
from io import BytesIO
from core.azure_storage import AzureStorageService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded file for image type and size.
    
    Args:
        file: UploadFile object to validate
        
    Raises:
        HTTPException: If validation fails
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )
    
    # Check file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )


@router.post("/upload/{employee_id}", response_model=schemas.ProfilePictureUploadResponse, status_code=201)
async def upload_profile_picture(
    employee_id: int,
    file: UploadFile = File(..., description="Profile picture image file"),
    uploaded_by_id: int = Query(..., description="ID of the employee uploading the picture"),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture for an employee.
    
    - **employee_id**: ID of the employee for whom to upload the picture
    - **file**: Image file (JPEG, PNG, GIF, WebP, max 5MB)
    - **uploaded_by_id**: ID of the employee uploading the picture
    """
    try:
        # Validate file
        validate_image_file(file)
        
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Upload profile picture
        result = await profile_service.upload_profile_picture(
            db=db,
            employee_id=employee_id,
            uploaded_by_id=uploaded_by_id,
            file=file
        )
        
        logger.info(f"Profile picture uploaded successfully for employee {employee_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading profile picture for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload profile picture")


@router.get("/{employee_id}", response_model=schemas.ProfilePictureListResponse)
def get_employee_profile_pictures(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all profile pictures for an employee.
    
    - **employee_id**: ID of the employee whose pictures to retrieve
    """
    try:
        # Validate employee exists
        if not service.ProfilePictureService.validate_employee_id(db, employee_id):
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get profile pictures
        pictures = service.ProfilePictureService.get_employee_profile_pictures(db, employee_id)
        
        return schemas.ProfilePictureListResponse(
            pictures=pictures,
            total=len(pictures),
            employee_id=employee_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile pictures for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile pictures")


@router.get("/{employee_id}/latest", response_model=schemas.ProfilePictureResponse)
def get_latest_profile_picture(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the most recent profile picture for an employee.
    
    - **employee_id**: ID of the employee whose latest picture to retrieve
    """
    try:
        # Validate employee exists
        if not service.ProfilePictureService.validate_employee_id(db, employee_id):
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get latest profile picture
        picture = service.ProfilePictureService.get_latest_profile_picture(db, employee_id)
        
        if not picture:
            raise HTTPException(status_code=404, detail="No profile picture found for employee")
        
        return picture
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest profile picture for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile picture")


@router.get("/serve-latest/{employee_id}")
def serve_latest_profile_picture(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Serve the latest profile picture for an employee, proxying from Azure Blob Storage.
    This endpoint avoids CORS issues by serving images through the backend.
    
    - **employee_id**: ID of the employee whose latest picture to serve
    """
    try:
        # Get latest profile picture
        picture = service.ProfilePictureService.get_latest_profile_picture(db, employee_id)
        
        if not picture:
            raise HTTPException(status_code=404, detail="No profile picture found for employee")
        
        # Use Azure Storage SDK to fetch the image
        try:
            azure_storage = AzureStorageService()
            
            # Extract blob name from the full path
            blob_name = picture.FilePath.split('/profile-pictures/')[-1]
            
            # Get the blob content using Azure SDK
            blob_content = azure_storage.get_blob_content(blob_name)
            
            if blob_content:
                # Return the image as a streaming response
                return StreamingResponse(
                    BytesIO(blob_content),
                    media_type=picture.MimeType or "image/jpeg",
                    headers={
                        "Cache-Control": "public, max-age=31536000",  # Cache for 1 year
                        "Content-Disposition": f"inline; filename={picture.FileName}"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail="Image not found in storage")
            
        except Exception as e:
            logger.error(f"Failed to fetch image from Azure: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch image from storage")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving latest profile picture for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve profile picture")


@router.get("/picture/{picture_id}", response_model=schemas.ProfilePictureResponse)
def get_profile_picture(
    picture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific profile picture by ID.
    
    - **picture_id**: ID of the profile picture to retrieve
    """
    try:
        # Get profile picture
        picture = service.ProfilePictureService.get_profile_picture(db, picture_id)
        
        if not picture:
            raise HTTPException(status_code=404, detail="Profile picture not found")
        
        return picture
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile picture {picture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile picture")


@router.get("/serve/{picture_id}")
def serve_profile_picture(
    picture_id: int,
    db: Session = Depends(get_db)
):
    """
    Serve a profile picture by ID, proxying from Azure Blob Storage.
    This endpoint avoids CORS issues by serving images through the backend.
    
    - **picture_id**: ID of the profile picture to serve
    """
    try:
        # Get profile picture
        picture = service.ProfilePictureService.get_profile_picture(db, picture_id)
        
        if not picture:
            raise HTTPException(status_code=404, detail="Profile picture not found")
        
        # Fetch the image from Azure Blob Storage
        try:
            response = requests.get(picture.FilePath, stream=True)
            response.raise_for_status()
            
            # Return the image as a streaming response
            return StreamingResponse(
                BytesIO(response.content),
                media_type=picture.MimeType or "image/jpeg",
                headers={
                    "Cache-Control": "public, max-age=31536000",  # Cache for 1 year
                    "Content-Disposition": f"inline; filename={picture.FileName}"
                }
            )
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch image from Azure: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch image from storage")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving profile picture {picture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve profile picture")


@router.delete("/picture/{picture_id}", response_model=schemas.ProfilePictureDeleteResponse)
def delete_profile_picture(
    picture_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific profile picture by ID.
    
    - **picture_id**: ID of the profile picture to delete
    """
    try:
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Delete profile picture
        result = profile_service.delete_profile_picture(db, picture_id)
        
        logger.info(f"Profile picture {picture_id} deleted successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile picture {picture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete profile picture")


@router.delete("/{employee_id}", response_model=dict)
def delete_employee_profile_pictures(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete all profile pictures for an employee.
    
    - **employee_id**: ID of the employee whose pictures to delete
    """
    try:
        # Validate employee exists
        if not service.ProfilePictureService.validate_employee_id(db, employee_id):
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Delete all profile pictures
        result = profile_service.delete_employee_profile_pictures(db, employee_id)
        
        logger.info(f"All profile pictures deleted for employee {employee_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile pictures for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete profile pictures")


@router.get("/test/azure-connection")
def test_azure_connection():
    """
    Test Azure Storage connection.
    """
    try:
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Test connection
        result = profile_service.test_azure_connection()
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing Azure connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test Azure connection") 


@router.post("/admin/cleanup-orphaned", response_model=dict)
def cleanup_orphaned_profile_pictures(
    db: Session = Depends(get_db)
):
    """
    Clean up orphaned profile pictures in Azure that don't exist in the database.
    
    This endpoint is for administrative use to clean up files that may have been
    left behind due to failed database operations.
    
    Returns:
        Dict with cleanup results including counts of cleaned and failed files
    """
    try:
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Perform cleanup
        result = profile_service.cleanup_orphaned_profile_pictures(db)
        
        if result.get("success"):
            logger.info("Orphaned profile picture cleanup completed successfully")
        else:
            logger.error(f"Orphaned profile picture cleanup failed: {result.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during orphaned profile picture cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup orphaned profile pictures") 


@router.post("/admin/test-collision", response_model=dict)
def test_blob_collision_handling(
    employee_id: int = Query(..., description="Employee ID for testing"),
    num_names: int = Query(10, description="Number of blob names to generate"),
    db: Session = Depends(get_db)
):
    """
    Test blob collision handling and retry logic.
    
    This endpoint is for testing and debugging blob name generation and collision handling.
    
    Args:
        employee_id: Employee ID for testing
        num_names: Number of blob names to generate for testing
        
    Returns:
        Dict with test results
    """
    try:
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Test blob name collision
        azure_service = profile_service.azure_storage
        blob_names = azure_service.test_blob_name_collision(employee_id, "jpg", num_names)
        
        # Check for collisions
        unique_names = set(blob_names)
        collision_count = len(blob_names) - len(unique_names)
        
        result = {
            "success": True,
            "employee_id": employee_id,
            "total_names_generated": len(blob_names),
            "unique_names": len(unique_names),
            "collision_count": collision_count,
            "collision_detected": collision_count > 0,
            "sample_names": blob_names[:5] if len(blob_names) > 5 else blob_names
        }
        
        if collision_count == 0:
            logger.info(f"Blob collision test passed for employee {employee_id}")
        else:
            logger.warning(f"Blob collision test detected {collision_count} collisions for employee {employee_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing blob collision for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test blob collision handling")


@router.post("/admin/simulate-concurrent", response_model=dict)
def simulate_concurrent_uploads(
    employee_id: int = Query(..., description="Employee ID for testing"),
    num_uploads: int = Query(5, description="Number of concurrent uploads to simulate"),
    db: Session = Depends(get_db)
):
    """
    Simulate concurrent uploads to test collision handling.
    
    This endpoint simulates multiple concurrent uploads for the same employee
    to test the collision handling and retry logic.
    
    Args:
        employee_id: Employee ID for testing
        num_uploads: Number of concurrent uploads to simulate
        
    Returns:
        Dict with simulation results
    """
    try:
        # Initialize service
        profile_service = service.ProfilePictureService()
        
        # Simulate concurrent uploads
        azure_service = profile_service.azure_storage
        simulation_result = azure_service.simulate_concurrent_uploads(employee_id, num_uploads)
        
        result = {
            "success": True,
            "employee_id": employee_id,
            "simulation_results": simulation_result,
            "summary": {
                "total_uploads_simulated": num_uploads,
                "successful_uploads": simulation_result.get("successful_uploads", 0),
                "failed_uploads": simulation_result.get("failed_uploads", 0),
                "total_attempts": simulation_result.get("total_attempts", 0),
                "average_attempts_per_upload": simulation_result.get("total_attempts", 0) / max(num_uploads, 1)
            }
        }
        
        logger.info(f"Concurrent upload simulation completed for employee {employee_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error simulating concurrent uploads for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to simulate concurrent uploads") 