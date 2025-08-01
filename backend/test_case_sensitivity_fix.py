#!/usr/bin/env python3
"""
Test script to verify case sensitivity fix for ticket validation
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_case_sensitivity():
    """Test that case sensitivity validation works correctly"""
    
    print("Testing Case Sensitivity Fix")
    print("=" * 40)
    
    # Test 1: Try to update with incorrect case "cLosed"
    print("\n1. Testing update with incorrect case 'cLosed':")
    try:
        update_data = {
            "StatusCode": "cLosed"  # Should be "Closed"
        }
        response = requests.put(
            f"{BASE_URL}/api/tickets/68",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected incorrect case 'cLosed'")
            print(f"Error: {response.json()}")
        else:
            print("❌ Should have rejected incorrect case 'cLosed'")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 2: Try to update with correct case "Closed"
    print("\n2. Testing update with correct case 'Closed':")
    try:
        update_data = {
            "StatusCode": "Closed"  # Correct case
        }
        response = requests.put(
            f"{BASE_URL}/api/tickets/68",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Correctly accepted correct case 'Closed'")
        else:
            print("❌ Should have accepted correct case 'Closed'")
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 3: Try to update with completely wrong value
    print("\n3. Testing update with completely wrong value 'INVALID_STATUS':")
    try:
        update_data = {
            "StatusCode": "INVALID_STATUS"
        }
        response = requests.put(
            f"{BASE_URL}/api/tickets/68",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid status 'INVALID_STATUS'")
            print(f"Error: {response.json()}")
        else:
            print("❌ Should have rejected invalid status 'INVALID_STATUS'")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 4: Try to update with different case variations
    print("\n4. Testing various case variations:")
    test_cases = [
        "closed",      # all lowercase
        "CLOSED",      # all uppercase  
        "cLOSED",      # first letter lowercase
        "ClOsEd",      # mixed case
        "CLosed",      # mixed case
    ]
    
    for test_case in test_cases:
        try:
            update_data = {"StatusCode": test_case}
            response = requests.put(
                f"{BASE_URL}/api/tickets/68",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"  '{test_case}': {response.status_code} {'✅' if response.status_code == 400 else '❌'}")
        except Exception as e:
            print(f"  '{test_case}': Error - {e}")

if __name__ == "__main__":
    test_case_sensitivity() 