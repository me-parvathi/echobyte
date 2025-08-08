#!/usr/bin/env python3
"""
Test script to verify ticket validation for lookup table references
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_ticket_validation():
    """Test ticket validation for lookup table references"""
    
    print("Testing Ticket Validation for Lookup Tables")
    print("=" * 60)
    
    # Test 1: Create ticket with invalid priority code
    print("\n1. Testing invalid priority code...")
    try:
        ticket_data = {
            "Subject": "Test ticket with invalid priority",
            "Description": "This should fail due to invalid priority code",
            "CategoryID": 1,  # Assuming this exists
            "PriorityCode": "INVALID_PRIORITY",  # This should not exist
            "StatusCode": "Open"
        }
        response = requests.post(
            f"{BASE_URL}/api/tickets/",
            json=ticket_data,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid priority code")
            print(f"Error: {response.json()}")
        else:
            print("❌ Should have rejected invalid priority code")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 2: Create ticket with invalid status code
    print("\n2. Testing invalid status code...")
    try:
        ticket_data = {
            "Subject": "Test ticket with invalid status",
            "Description": "This should fail due to invalid status code",
            "CategoryID": 1,  # Assuming this exists
            "PriorityCode": "MED",  # Assuming this exists
            "StatusCode": "INVALID_STATUS"  # This should not exist
        }
        response = requests.post(
            f"{BASE_URL}/api/tickets/",
            json=ticket_data,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid status code")
            print(f"Error: {response.json()}")
        else:
            print("❌ Should have rejected invalid status code")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 3: Create ticket with invalid category ID
    print("\n3. Testing invalid category ID...")
    try:
        ticket_data = {
            "Subject": "Test ticket with invalid category",
            "Description": "This should fail due to invalid category ID",
            "CategoryID": 99999,  # This should not exist
            "PriorityCode": "MED",  # Assuming this exists
            "StatusCode": "Open"
        }
        response = requests.post(
            f"{BASE_URL}/api/tickets/",
            json=ticket_data,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid category ID")
            print(f"Error: {response.json()}")
        else:
            print("❌ Should have rejected invalid category ID")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 4: Update ticket with invalid values
    print("\n4. Testing update with invalid values...")
    try:
        # First get a list of tickets to find one to update
        response = requests.get(f"{BASE_URL}/api/tickets/")
        if response.status_code == 200:
            tickets = response.json()
            if tickets.get('tickets') and len(tickets['tickets']) > 0:
                ticket_id = tickets['tickets'][0]['TicketID']
                
                # Try to update with invalid priority
                update_data = {
                    "PriorityCode": "INVALID_PRIORITY"
                }
                response = requests.put(
                    f"{BASE_URL}/api/tickets/{ticket_id}",
                    json=update_data,
                    headers={"Authorization": "Bearer test-token"}
                )
                print(f"Update Status Code: {response.status_code}")
                if response.status_code == 400:
                    print("✅ Correctly rejected invalid priority in update")
                    print(f"Error: {response.json()}")
                else:
                    print("❌ Should have rejected invalid priority in update")
            else:
                print("No tickets found to test update")
        else:
            print("Could not get tickets list")
    except Exception as e:
        print(f"Error making request: {e}")
    
    # Test 5: Get lookup tables to see valid values
    print("\n5. Getting valid lookup table values...")
    try:
        # Get priorities
        response = requests.get(f"{BASE_URL}/api/tickets/priorities")
        if response.status_code == 200:
            priorities = response.json()
            print(f"✅ Valid priorities: {[p['PriorityCode'] for p in priorities]}")
        else:
            print("❌ Could not get priorities")
        
        # Get statuses
        response = requests.get(f"{BASE_URL}/api/tickets/statuses")
        if response.status_code == 200:
            statuses = response.json()
            print(f"✅ Valid statuses: {[s['TicketStatusCode'] for s in statuses]}")
        else:
            print("❌ Could not get statuses")
        
        # Get categories
        response = requests.get(f"{BASE_URL}/api/tickets/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Valid category IDs: {[c['CategoryID'] for c in categories]}")
        else:
            print("❌ Could not get categories")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_ticket_validation() 