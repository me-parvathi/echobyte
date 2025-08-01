#!/usr/bin/env python3
"""
Test database connection and reset pool if needed.
This script helps diagnose and fix database connection issues.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_database_health():
    """Test database connection health"""
    print("🔍 Testing database connection health...")
    
    try:
        # Test basic health
        response = requests.get(f"{BASE_URL}/health/database", timeout=10)
        print(f"✅ Database health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Database status: {data.get('status', 'unknown')}")
            return data.get('status') == 'healthy'
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False

def test_connection_pool():
    """Test connection pool status"""
    print("🔍 Testing connection pool status...")
    
    try:
        response = requests.get(f"{BASE_URL}/health/connections", timeout=10)
        print(f"✅ Connection pool check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('connection_stats', {})
            print(f"📊 Active connections: {stats.get('active_connections', 0)}")
            print(f"📊 Total requests: {stats.get('total_requests', 0)}")
            print(f"📊 Failed requests: {stats.get('failed_requests', 0)}")
            return stats.get('active_connections', 0) < 20  # If less than 20 active, pool is healthy
    except Exception as e:
        print(f"❌ Connection pool check failed: {e}")
        return False

def reset_connection_pool():
    """Reset the connection pool"""
    print("🔄 Resetting connection pool...")
    
    try:
        response = requests.post(f"{BASE_URL}/health/connections/reset", timeout=10)
        print(f"✅ Pool reset response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Reset status: {data.get('status', 'unknown')}")
            return data.get('status') == 'success'
    except Exception as e:
        print(f"❌ Pool reset failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔍 Testing authentication endpoints...")
    
    try:
        # Test login endpoint
        login_data = {
            "username": "andrew.hickman",
            "password": "test123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=30)
        print(f"✅ Login test: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            
            print("✅ Login successful, testing token refresh...")
            
            # Test token refresh
            refresh_data = {"refresh_token": refresh_token}
            refresh_response = requests.post(f"{BASE_URL}/api/auth/refresh", json=refresh_data, timeout=30)
            print(f"✅ Token refresh test: {refresh_response.status_code}")
            
            return refresh_response.status_code == 200
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Auth endpoint test failed: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("🚀 EchoByte Database Connection Test")
    print("=" * 50)
    
    # Test 1: Database health
    db_healthy = test_database_health()
    print()
    
    # Test 2: Connection pool
    pool_healthy = test_connection_pool()
    print()
    
    # If database is unhealthy, try to reset pool
    if not db_healthy or not pool_healthy:
        print("⚠️  Database or pool issues detected, attempting reset...")
        reset_success = reset_connection_pool()
        
        if reset_success:
            print("✅ Pool reset successful, waiting 5 seconds...")
            time.sleep(5)
            
            # Test again after reset
            print("🔍 Re-testing after reset...")
            db_healthy = test_database_health()
            pool_healthy = test_connection_pool()
        else:
            print("❌ Pool reset failed")
    
    # Test 3: Authentication endpoints
    auth_working = test_auth_endpoints()
    print()
    
    # Summary
    print("📋 Test Summary:")
    print(f"   Database Health: {'✅' if db_healthy else '❌'}")
    print(f"   Connection Pool: {'✅' if pool_healthy else '❌'}")
    print(f"   Authentication: {'✅' if auth_working else '❌'}")
    
    if db_healthy and pool_healthy and auth_working:
        print("🎉 All tests passed! Database connection is healthy.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("💡 Try restarting the backend server if issues persist.")

if __name__ == "__main__":
    main() 