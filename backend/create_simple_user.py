#!/usr/bin/env python3
"""
Simple script to create a test user in the SQLite database
"""

import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal, init_database
from api.auth.models import User

def create_test_user():
    """Create a test user for login"""
    
    # Initialize database
    init_database()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.Username == "john.doe@company.com").first()
        if existing_user:
            print("✅ Test user already exists")
            return
        
        # Create test user
        test_user = User(
            UserID="test-user-001",
            Username="john.doe@company.com",
            Email="john.doe@company.com",
            Password=hashlib.sha256("password123".encode()).hexdigest(),
            IsActive=True,
            LastLoginAt=None,
            PasswordChangedAt=datetime.utcnow(),
            CreatedAt=datetime.utcnow(),
            UpdatedAt=datetime.utcnow()
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("Username: john.doe@company.com")
        print("Password: password123")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 