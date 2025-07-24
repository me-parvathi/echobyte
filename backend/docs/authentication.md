# Authentication and Session Management

This document describes the authentication and session management system for the EchoByte API.

## Overview

The authentication system uses JWT (JSON Web Tokens) for stateless authentication. It provides:

- User login/logout functionality
- Token-based authentication
- Role-based access control (regular users vs superusers)
- Token refresh capabilities
- Protected route dependencies

## API Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/login`
Authenticate a user and receive an access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "uuid-here",
  "username": "username",
  "email": "user@example.com",
  "is_superuser": false
}
```

#### POST `/api/v1/auth/logout`
Logout a user (client-side token invalidation).

**Request Body:**
```json
{
  "refresh_token": "optional-refresh-token"
}
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

#### POST `/api/v1/auth/refresh`
Refresh an access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:**
```json
{
  "access_token": "new-access-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET `/api/v1/auth/me`
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/v1/auth/verify`
Verify if the current token is valid.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "valid": true,
  "user_id": "user-uuid",
  "email": "user@example.com",
  "username": "username",
  "is_superuser": false
}
```

## Protecting Routes

### Using Authentication Dependencies

You can protect routes using the provided dependencies:

```python
from fastapi import Depends
from app.api.dependencies import get_current_user, get_current_superuser
from app.models.user import User

# Require authentication for any user
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.Username}"}

# Require superuser permissions
@router.post("/admin-only")
async def admin_route(current_user: User = Depends(get_current_superuser)):
    return {"message": f"Admin action by {current_user.Username}"}
```

### Available Dependencies

- `get_current_user`: Requires any authenticated user
- `get_current_superuser`: Requires authenticated superuser
- `get_optional_current_user`: Optional authentication (returns None if not authenticated)

## Configuration

### Environment Variables

Set these environment variables in your `.env` file:

```env
# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=your-database-connection-string
```

### Token Configuration

- **Access Token Expiry**: 30 minutes (configurable)
- **Algorithm**: HS256
- **Token Type**: Bearer

## Security Features

1. **Password Hashing**: Uses bcrypt for secure password hashing
2. **JWT Tokens**: Stateless authentication with configurable expiry
3. **Role-based Access**: Support for regular users and superusers
4. **Token Validation**: Automatic token validation on protected routes
5. **User Status Check**: Inactive users cannot authenticate

## Usage Examples

### Frontend Integration

```javascript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access_token } = await loginResponse.json();

// Use token for authenticated requests
const response = await fetch('/api/v1/employees', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### Python Client Example

```python
import requests

# Login
login_data = {
    "email": "user@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
token_data = response.json()
access_token = token_data["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/api/v1/employees", headers=headers)
```

## Error Handling

The authentication system returns appropriate HTTP status codes:

- `401 Unauthorized`: Invalid credentials or missing token
- `403 Forbidden`: Insufficient permissions (e.g., superuser required)
- `400 Bad Request`: Invalid request data
- `404 Not Found`: User not found

## Best Practices

1. **Store tokens securely**: Use secure storage (not localStorage for sensitive apps)
2. **Handle token expiry**: Implement automatic token refresh
3. **Validate tokens**: Always verify tokens on the server side
4. **Use HTTPS**: Always use HTTPS in production
5. **Rotate secrets**: Regularly rotate your SECRET_KEY
6. **Monitor usage**: Log authentication attempts for security monitoring

## Future Enhancements

- [ ] Refresh token rotation
- [ ] Token blacklisting for logout
- [ ] Rate limiting for login attempts
- [ ] Multi-factor authentication
- [ ] OAuth integration
- [ ] Session management with Redis 