"""
Centralized constants for the EchoByte application.
This module contains configuration values used across different services.
"""

# File upload constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

# Azure Storage constants
AZURE_STORAGE_CONNECTION_STRING_ENV = "AZURE_STORAGE_CONNECTION_STRING"
AZURE_STORAGE_CONTAINER_ENV = "AZURE_STORAGE_CONTAINER"

# Profile picture constants
PROFILE_PICTURE_BLOB_PREFIX = "profile-pictures"
PROFILE_PICTURE_CACHE_CONTROL = "public, max-age=31536000"  # 1 year cache

# Database constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 1000

# Validation constants
MAX_STRING_LENGTH = 255
MAX_TEXT_LENGTH = 1000
MAX_URL_LENGTH = 500

# Time constants
DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour in seconds
TOKEN_EXPIRY_HOURS = 24

# Status codes
STATUS_ACTIVE = True
STATUS_INACTIVE = False

# Common error messages
ERROR_EMPLOYEE_NOT_FOUND = "Employee not found"
ERROR_FILE_TOO_LARGE = "File size exceeds maximum allowed size"
ERROR_INVALID_FILE_TYPE = "File type not allowed"
ERROR_UPLOAD_FAILED = "Failed to upload file"
ERROR_DELETE_FAILED = "Failed to delete file"
ERROR_NOT_FOUND = "Resource not found"
ERROR_UNAUTHORIZED = "Unauthorized access"
ERROR_FORBIDDEN = "Access forbidden"
ERROR_VALIDATION_FAILED = "Validation failed" 