#!/usr/bin/env python3
"""
Example script demonstrating ticket creation with asset selection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.ticket.service import AssetIntegrationService, TicketService
from api.ticket import schemas

def demonstrate_asset_selection():
    """Demonstrate the asset selection functionality"""
    db = SessionLocal()
    
    try:
        # Example user ID (replace with actual user ID)
        user_id = 1
        
        print("=== Asset Selection Demo ===\n")
        
        # 1. Get user's assigned assets
        print("1. Getting user's assigned assets...")
        user_assets = AssetIntegrationService.get_user_assigned_assets(db, user_id)
        
        if user_assets:
            print(f"   Found {len(user_assets)} assets assigned to user:")
            for asset in user_assets:
                print(f"   - {asset.AssetTag} ({asset.AssetTypeID})")
        else:
            print("   No assets assigned to user")
        
        # 2. Get asset selection options
        print("\n2. Getting asset selection options...")
        selection_options = AssetIntegrationService.get_asset_selection_options(db, user_id)
        
        print(f"   Personal assets: {len(selection_options.personal_assets)}")
        print(f"   Community assets: {len(selection_options.community_assets)}")
        print(f"   Total available: {selection_options.total_assets}")
        
        # 3. Validate asset access
        if user_assets:
            test_asset_id = user_assets[0].AssetID
            print(f"\n3. Validating access to asset {test_asset_id}...")
            
            has_access = AssetIntegrationService.validate_asset_access(db, test_asset_id, user_id)
            print(f"   User has access: {has_access}")
            
            # Test with invalid asset
            invalid_asset_id = 99999
            has_access_invalid = AssetIntegrationService.validate_asset_access(db, invalid_asset_id, user_id)
            print(f"   User has access to invalid asset: {has_access_invalid}")
        
        # 4. Create a ticket with asset
        if user_assets:
            print(f"\n4. Creating ticket with asset {user_assets[0].AssetID}...")
            
            ticket_data = schemas.TicketCreate(
                Subject="Test ticket with asset",
                Description="This is a test ticket linked to an asset",
                CategoryID=1,  # Hardware Issues
                PriorityCode="MED",
                StatusCode="Open",
                AssetID=user_assets[0].AssetID
            )
            
            try:
                ticket = TicketService.create_ticket(db, ticket_data, user_id)
                print(f"   Ticket created successfully: {ticket.TicketNumber}")
                print(f"   Linked to asset: {ticket.AssetID}")
            except Exception as e:
                print(f"   Error creating ticket: {e}")
        
        # 5. Create a ticket without asset
        print(f"\n5. Creating ticket without asset...")
        
        ticket_data_no_asset = schemas.TicketCreate(
            Subject="Test ticket without asset",
            Description="This is a test ticket for general IT issue",
            CategoryID=9,  # General IT Support
            PriorityCode="LOW",
            StatusCode="Open"
            # No AssetID specified
        )
        
        try:
            ticket_no_asset = TicketService.create_ticket(db, ticket_data_no_asset, user_id)
            print(f"   Ticket created successfully: {ticket_no_asset.TicketNumber}")
            print(f"   No asset linked: {ticket_no_asset.AssetID is None}")
        except Exception as e:
            print(f"   Error creating ticket: {e}")
        
        print("\n=== Demo Complete ===")
        
    except Exception as e:
        print(f"Error in demo: {e}")
        db.rollback()
    finally:
        db.close()

def show_community_asset_placeholders():
    """Show the planned community asset functionality"""
    print("\n=== Community Asset Placeholders ===\n")
    
    print("1. Community Asset Types (to be implemented):")
    print("   - Shared printers in office locations")
    print("   - Conference room projectors and equipment")
    print("   - Kitchen appliances and common area devices")
    print("   - Network infrastructure (WiFi, switches)")
    print("   - Building security systems")
    print("   - HVAC and environmental controls")
    
    print("\n2. Asset Classification (planned):")
    print("   - Personal: Assigned to specific user")
    print("   - Community: Shared within location")
    print("   - Public: Available to all users")
    print("   - Restricted: IT staff only")
    
    print("\n3. Location-Based Asset Discovery (planned):")
    print("   - Assets filtered by user's location")
    print("   - Cross-location assets for remote workers")
    print("   - Mobile assets that move between locations")
    
    print("\n4. Category-Based Asset Filtering (planned):")
    print("   - Hardware issues → Show relevant hardware")
    print("   - Software issues → Show user's devices")
    print("   - Network issues → Show network infrastructure")
    print("   - General IT → No asset required")

if __name__ == "__main__":
    demonstrate_asset_selection()
    show_community_asset_placeholders() 