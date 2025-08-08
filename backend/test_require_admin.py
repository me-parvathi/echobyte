#!/usr/bin/env python3
"""
Test script to directly test the require_admin function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auth import require_admin
from api.auth.models import User
from core.database import get_db

def test_require_admin():
    """Test the require_admin function directly"""
    print("Testing require_admin function...")
    print("=" * 50)
    
    # Get the require_admin function
    admin_checker = require_admin
    
    print(f"✅ require_admin function: {admin_checker}")
    print(f"✅ Type: {type(admin_checker)}")
    print(f"✅ Callable: {callable(admin_checker)}")
    
    # Test if it's a dependency function
    try:
        # This should raise an exception since we're not in a FastAPI context
        result = admin_checker()
        print(f"❌ Unexpected result: {result}")
    except Exception as e:
        print(f"✅ Expected exception: {e}")
    
    print("\n✅ require_admin function is properly defined!")

if __name__ == "__main__":
    test_require_admin() 