#!/usr/bin/env python3
"""
Debug script to test ticket validation for case sensitivity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from core.database import get_db
from api.ticket import service, models

def test_validation():
    """Test the validation methods directly"""
    
    print("Testing Ticket Validation Debug")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test 1: Check what status codes exist in database
        print("\n1. Checking existing status codes in database:")
        statuses = db.query(models.TicketStatus).filter(models.TicketStatus.IsActive == True).all()
        for status in statuses:
            print(f"  - {status.TicketStatusCode} (Active: {status.IsActive})")
        
        # Test 2: Test validation with correct case
        print("\n2. Testing validation with correct case 'Closed':")
        result = service.TicketService.validate_status_code(db, "Closed")
        print(f"  Result: {result}")
        
        # Test 3: Test validation with incorrect case 'cLosed'
        print("\n3. Testing validation with incorrect case 'cLosed':")
        result = service.TicketService.validate_status_code(db, "cLosed")
        print(f"  Result: {result}")
        
        # Test 4: Test validation with completely wrong value
        print("\n4. Testing validation with wrong value 'INVALID_STATUS':")
        result = service.TicketService.validate_status_code(db, "INVALID_STATUS")
        print(f"  Result: {result}")
        
        # Test 5: Check the actual SQL query being executed
        print("\n5. Checking the actual query for 'cLosed':")
        status = db.query(models.TicketStatus).filter(
            models.TicketStatus.TicketStatusCode == "cLosed",
            models.TicketStatus.IsActive == True
        ).first()
        print(f"  Query result: {status}")
        
        # Test 6: Check if there are any case-insensitive matches
        print("\n6. Checking for any status codes that might match 'cLosed' case-insensitively:")
        all_statuses = db.query(models.TicketStatus).all()
        for status in all_statuses:
            if "closed" in status.TicketStatusCode.lower():
                print(f"  - Found: '{status.TicketStatusCode}' (matches 'closed' case-insensitively)")
        
        # Test 7: Test the update method directly
        print("\n7. Testing update method with invalid status:")
        try:
            from api.ticket.schemas import TicketUpdate
            update_data = TicketUpdate(StatusCode="cLosed")
            # This should raise an exception
            result = service.TicketService.update_ticket(db, 68, update_data)
            print(f"  Update succeeded (this should not happen): {result}")
        except Exception as e:
            print(f"  Update failed as expected: {e}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_validation() 