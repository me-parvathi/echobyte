#!/usr/bin/env python3
"""
Test script for the authentication system.
This script demonstrates how to use the authentication endpoints.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

def test_authentication_flow():
    """Test the complete authentication flow"""
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    # Step 1: Create a test user (if not exists)
    print("\n1. Creating test user...")
    create_user_response = create_test_user()
    
    if create_user_response.get("status") == "created":
        print("✅ Test user created successfully")
    elif create_user_response.get("status") == "exists":
        print("ℹ️  Test user already exists")
    else:
        print("❌ Failed to create test user")
        return
    
    # Step 2: Test login
    print("\n2. Testing login...")
    login_response = login_user(TEST_USER["email"], TEST_USER["password"])
    
    if login_response.get("success"):
        access_token = login_response["access_token"]
        print("✅ Login successful")
        print(f"   Access Token: {access_token[:50]}...")
    else:
        print("❌ Login failed")
        return
    
    # Step 3: Test protected endpoint
    print("\n3. Testing protected endpoint...")
    protected_response = test_protected_endpoint(access_token)
    
    if protected_response.get("success"):
        print("✅ Protected endpoint accessible")
        print(f"   Response: {protected_response['data']}")
    else:
        print("❌ Protected endpoint failed")
    
    # Step 4: Test token verification
    print("\n4. Testing token verification...")
    verify_response = verify_token(access_token)
    
    if verify_response.get("success"):
        print("✅ Token verification successful")
        print(f"   User: {verify_response['data']['username']}")
    else:
        print("❌ Token verification failed")
    
    # Step 5: Test get current user
    print("\n5. Testing get current user...")
    me_response = get_current_user(access_token)
    
    if me_response.get("success"):
        print("✅ Get current user successful")
        print(f"   User ID: {me_response['data']['id']}")
    else:
        print("❌ Get current user failed")
    
    # Step 6: Test invalid token
    print("\n6. Testing invalid token...")
    invalid_response = test_protected_endpoint("invalid_token")
    
    if not invalid_response.get("success"):
        print("✅ Invalid token correctly rejected")
    else:
        print("❌ Invalid token should have been rejected")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")

def create_test_user() -> Dict[str, Any]:
    """Create a test user"""
    try:
        response = requests.post(
            f"{BASE_URL}/users/",
            json={
                "email": TEST_USER["email"],
                "username": "testuser",
                "password": TEST_USER["password"],
                "is_active": True,
                "is_superuser": False
            }
        )
        
        if response.status_code == 201:
            return {"status": "created"}
        elif response.status_code == 400 and "already registered" in response.text:
            return {"status": "exists"}
        else:
            return {"status": "error", "message": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def login_user(email: str, password: str) -> Dict[str, Any]:
    """Login a user and return access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "access_token": data["access_token"],
                "user_id": data["user_id"]
            }
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_protected_endpoint(token: str) -> Dict[str, Any]:
    """Test accessing a protected endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/employees/", headers=headers)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_token(token: str) -> Dict[str, Any]:
    """Verify a token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_current_user(token: str) -> Dict[str, Any]:
    """Get current user information"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Authentication System Test")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn main:app --reload")
    
    try:
        test_authentication_flow()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        print("Make sure your server is running and the database is accessible") 