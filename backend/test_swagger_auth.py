#!/usr/bin/env python3
"""
Test script to demonstrate authentication flow for Swagger UI testing.
This shows the exact steps to follow in Swagger UI.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication_flow():
    """Demonstrate the complete authentication flow"""
    
    print("🔐 EchoByte Authentication Flow Test")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1️⃣ STEP 1: Login to get JWT token")
    print("-" * 30)
    
    login_data = {
        "username": "andrew.hickman",
        "password": "test123"
    }
    
    print(f"POST {BASE_URL}/api/auth/login")
    print(f"Body: {json.dumps(login_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"✅ Login successful!")
        print(f"Access Token: {access_token[:50]}...")
        print(f"Token Type: {token_data['token_type']}")
        print(f"Expires In: {token_data['expires_in']} seconds")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    # Step 2: Test protected endpoint
    print("\n2️⃣ STEP 2: Access protected endpoint")
    print("-" * 30)
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"GET {BASE_URL}/api/auth/me")
    print(f"Headers: Authorization: Bearer {access_token[:50]}...")
    
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Protected endpoint accessed successfully!")
        print(f"User Data: {json.dumps(user_data, indent=2)}")
    else:
        print(f"❌ Protected endpoint failed: {response.status_code}")
        print(response.text)
    
    # Step 3: Test without token (should fail)
    print("\n3️⃣ STEP 3: Test without token (should fail)")
    print("-" * 30)
    
    print(f"GET {BASE_URL}/api/auth/me")
    print("Headers: None")
    
    response = requests.get(f"{BASE_URL}/api/auth/me")
    
    if response.status_code == 403:
        print(f"✅ Correctly rejected without token: {response.status_code}")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        print(response.text)
    
    print("\n🎯 SWAGGER UI TESTING INSTRUCTIONS")
    print("=" * 50)
    print("1. Open http://localhost:8000/docs in your browser")
    print("2. Find /api/auth/login endpoint")
    print("3. Click 'Try it out' and enter the login data above")
    print("4. Copy the access_token from the response")
    print("5. Click the 'Authorize' button (🔒) at the top")
    print("6. Enter: Bearer <your_access_token>")
    print("7. Click 'Authorize' then 'Close'")
    print("8. Now test /api/auth/me endpoint")
    print("9. It should work without entering the token again!")

if __name__ == "__main__":
    test_authentication_flow() 