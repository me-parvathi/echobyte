#!/usr/bin/env python3
"""
Script to create a test user in the database for authentication testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from core.database import SessionLocal
from api.auth.models import User

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create a test user for authentication testing"""
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.Username == "admin").first()
        
        if existing_user:
            print("Test user 'admin' already exists!")
            return
        
        # Create test user
        hashed_password = pwd_context.hash("admin123")
        
        test_user = User(
            Username="admin",
            Email="admin@echobyte.com",
            Password=hashed_password,
            IsActive=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Test user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@echobyte.com")
        print(f"UserID: {test_user.UserID}")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 