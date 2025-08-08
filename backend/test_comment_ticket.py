#!/usr/bin/env python3
"""
Test script to verify comment functionality for tickets
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_ticket_comments():
    """Test the comment functionality for tickets"""
    
    print("Testing Ticket Comment Functionality")
    print("=" * 50)
    
    # Test 1: Get comments for a ticket (assuming ticket ID 1 exists)
    print("\n1. Testing GET comments for ticket...")
    try:
        response = requests.get(f"{BASE_URL}/api/comments/Ticket/1")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Comments found: {data.get('total_count', 0)}")
            print("Response:", json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 2: Create a comment for a ticket
    print("\n2. Testing POST comment for ticket...")
    try:
        comment_data = {
            "comment_text": "This is a test comment for the ticket",
            "commenter_role": "Employee"
        }
        response = requests.post(
            f"{BASE_URL}/api/comments/Ticket/1",
            json=comment_data,
            headers={"Authorization": "Bearer test-token"}  # You'll need a real token
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Comment created successfully!")
            print("Response:", json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_ticket_comments() 