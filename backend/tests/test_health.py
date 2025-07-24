import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to EchoByte API"}

def test_health_endpoint():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_health_endpoint():
    """Test the API health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "EchoByte API"}

def test_database_health_endpoint():
    """Test the database health endpoint"""
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    # The response will depend on database connectivity
    data = response.json()
    assert "status" in data
    assert "database" in data 