#!/usr/bin/env python3
"""
Script to seed ticket system lookup data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.ticket.models import TicketStatus, TicketPriority, TicketCategory

def seed_ticket_statuses(db: Session):
    """Seed ticket statuses"""
    statuses = [
        ("Open", "Open - Awaiting Assignment"),
        ("Assigned", "Assigned - Work in Progress"),
        ("In-Progress", "In Progress - Being Worked On"),
        ("Pending-User", "Pending User Response"),
        ("Pending-Vendor", "Pending Vendor Response"),
        ("Resolved", "Resolved - Issue Fixed"),
        ("Closed", "Closed - Ticket Complete"),
        ("Escalated", "Escalated - Manager Review"),
        ("Cancelled", "Cancelled - No Longer Needed"),
        ("On-Hold", "On Hold - Temporarily Suspended")
    ]
    
    for status_code, status_name in statuses:
        existing = db.query(TicketStatus).filter(TicketStatus.TicketStatusCode == status_code).first()
        if not existing:
            status = TicketStatus(
                TicketStatusCode=status_code,
                TicketStatusName=status_name,
                IsActive=True
            )
            db.add(status)
            print(f"Added ticket status: {status_code}")

def seed_ticket_priorities(db: Session):
    """Seed ticket priorities"""
    priorities = [
        ("LOW", "Low Priority", 72),           # 3 business days
        ("MED", "Medium Priority", 24),        # 1 business day
        ("HIGH", "High Priority", 4),          # 4 hours
        ("CRIT", "Critical", 1),               # 1 hour
        ("URG", "Urgent", 2)                   # 2 hours
    ]
    
    for priority_code, priority_name, sla_hours in priorities:
        existing = db.query(TicketPriority).filter(TicketPriority.PriorityCode == priority_code).first()
        if not existing:
            priority = TicketPriority(
                PriorityCode=priority_code,
                PriorityName=priority_name,
                SLAHours=sla_hours,
                IsActive=True
            )
            db.add(priority)
            print(f"Added ticket priority: {priority_code}")

def seed_ticket_categories(db: Session):
    """Seed ticket categories"""
    categories = [
        # Parent Categories
        ("Hardware Issues", None),
        ("Software Issues", None),
        ("Network & Connectivity", None),
        ("Access & Permissions", None),
        ("Email & Communication", None),
        ("Security Issues", None),
        ("Mobile Devices", None),
        ("Printing & Scanning", None),
        ("General IT Support", None)
    ]
    
    # Create parent categories first
    parent_categories = {}
    for category_name, parent_id in categories:
        existing = db.query(TicketCategory).filter(TicketCategory.CategoryName == category_name).first()
        if not existing:
            category = TicketCategory(
                CategoryName=category_name,
                ParentCategoryID=parent_id,
                IsActive=True
            )
            db.add(category)
            db.flush()  # Get the ID
            parent_categories[category_name] = category.CategoryID
            print(f"Added parent category: {category_name}")
    
    # Subcategories
    subcategories = [
        # Hardware Subcategories
        ("Laptop Issues", "Hardware Issues"),
        ("Desktop Issues", "Hardware Issues"),
        ("Monitor Problems", "Hardware Issues"),
        ("Keyboard/Mouse Issues", "Hardware Issues"),
        ("Docking Station Problems", "Hardware Issues"),
        ("Hardware Replacement", "Hardware Issues"),
        ("Hardware Repair", "Hardware Issues"),
        
        # Software Subcategories
        ("Operating System Issues", "Software Issues"),
        ("Application Crashes", "Software Issues"),
        ("Software Installation", "Software Issues"),
        ("Software Updates", "Software Issues"),
        ("License Issues", "Software Issues"),
        ("Performance Issues", "Software Issues"),
        ("Compatibility Problems", "Software Issues"),
        
        # Network Subcategories
        ("WiFi Connectivity", "Network & Connectivity"),
        ("VPN Issues", "Network & Connectivity"),
        ("Internet Access", "Network & Connectivity"),
        ("Network Printer Issues", "Network & Connectivity"),
        ("Network Drive Access", "Network & Connectivity"),
        ("Bandwidth Issues", "Network & Connectivity"),
        
        # Access Subcategories
        ("Account Creation", "Access & Permissions"),
        ("Password Reset", "Access & Permissions"),
        ("Access Rights", "Access & Permissions"),
        ("Account Lockout", "Access & Permissions"),
        ("Multi-Factor Authentication", "Access & Permissions"),
        ("System Permissions", "Access & Permissions"),
        
        # Email Subcategories
        ("Email Access Issues", "Email & Communication"),
        ("Email Configuration", "Email & Communication"),
        ("Spam/Phishing", "Email & Communication"),
        ("Email Storage", "Email & Communication"),
        ("Calendar Issues", "Email & Communication"),
        ("Email Client Problems", "Email & Communication"),
        
        # Security Subcategories
        ("Malware/Virus Issues", "Security Issues"),
        ("Security Software", "Security Issues"),
        ("Data Breach Concerns", "Security Issues"),
        ("Compliance Issues", "Security Issues"),
        ("Security Training", "Security Issues"),
        
        # Mobile Device Subcategories
        ("Mobile Phone Issues", "Mobile Devices"),
        ("Tablet Problems", "Mobile Devices"),
        ("Mobile App Issues", "Mobile Devices"),
        ("Mobile Device Setup", "Mobile Devices"),
        ("Mobile Security", "Mobile Devices"),
        
        # Printing Subcategories
        ("Printer Setup", "Printing & Scanning"),
        ("Print Quality Issues", "Printing & Scanning"),
        ("Scanner Problems", "Printing & Scanning"),
        ("Printer Network Issues", "Printing & Scanning"),
        ("Printer Maintenance", "Printing & Scanning"),
        
        # General IT Subcategories
        ("Training Requests", "General IT Support"),
        ("Documentation Requests", "General IT Support"),
        ("Equipment Requests", "General IT Support"),
        ("General Questions", "General IT Support"),
        ("System Maintenance", "General IT Support")
    ]
    
    for subcategory_name, parent_name in subcategories:
        existing = db.query(TicketCategory).filter(TicketCategory.CategoryName == subcategory_name).first()
        if not existing and parent_name in parent_categories:
            subcategory = TicketCategory(
                CategoryName=subcategory_name,
                ParentCategoryID=parent_categories[parent_name],
                IsActive=True
            )
            db.add(subcategory)
            print(f"Added subcategory: {subcategory_name}")

def main():
    """Main function to seed all ticket data"""
    db = SessionLocal()
    try:
        print("Seeding ticket statuses...")
        seed_ticket_statuses(db)
        
        print("Seeding ticket priorities...")
        seed_ticket_priorities(db)
        
        print("Seeding ticket categories...")
        seed_ticket_categories(db)
        
        db.commit()
        print("Ticket system data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding ticket data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 