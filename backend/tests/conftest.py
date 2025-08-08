"""
Pytest configuration and fixtures for EchoByte HR Management API tests.
This module provides common fixtures and configuration for all tests.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator

# Import application components
from main import app
from core.database import Base, get_db
from core.container import DependencyContainer, get_container

# Test database URL (SQLite in-memory for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def test_db():
    """Create test database and tables."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db):
    """Create a database session for testing."""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock(spec=Session)

@pytest.fixture
def dependency_container():
    """Create a fresh dependency container for testing."""
    container = DependencyContainer()
    yield container
    container.clear()

@pytest.fixture
def sample_location_data():
    """Sample location data for testing."""
    return {
        "LocationID": 1,
        "LocationName": "Test Location",
        "Address1": "123 Test Street",
        "Address2": "Suite 100",
        "City": "Test City",
        "State": "Test State",
        "Country": "Test Country",
        "PostalCode": "12345",
        "Phone": "+1-555-123-4567",
        "TimeZone": "UTC",
        "IsActive": True
    }

@pytest.fixture
def sample_employee_data():
    """Sample employee data for testing."""
    return {
        "EmployeeID": 1,
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john.doe@example.com",
        "Phone": "+1-555-123-4567",
        "HireDate": "2023-01-01",
        "IsActive": True
    }

@pytest.fixture
def sample_department_data():
    """Sample department data for testing."""
    return {
        "DepartmentID": 1,
        "DepartmentName": "Test Department",
        "Description": "Test department description",
        "IsActive": True
    }

# Mock fixtures for external dependencies
@pytest.fixture
def mock_email_service():
    """Mock email service."""
    return Mock()

@pytest.fixture
def mock_notification_service():
    """Mock notification service."""
    return Mock()

@pytest.fixture
def mock_file_storage():
    """Mock file storage service."""
    return Mock()

# Test data factories
@pytest.fixture
def location_factory():
    """Factory for creating location test data."""
    def _create_location(**kwargs):
        default_data = {
            "LocationName": "Test Location",
            "Address1": "123 Test Street",
            "City": "Test City",
            "Country": "Test Country",
            "TimeZone": "UTC",
            "IsActive": True
        }
        default_data.update(kwargs)
        return default_data
    return _create_location

@pytest.fixture
def employee_factory():
    """Factory for creating employee test data."""
    def _create_employee(**kwargs):
        default_data = {
            "FirstName": "John",
            "LastName": "Doe",
            "Email": "john.doe@example.com",
            "Phone": "+1-555-123-4567",
            "HireDate": "2023-01-01",
            "IsActive": True
        }
        default_data.update(kwargs)
        return default_data
    return _create_employee

# Test markers
pytest_plugins = ["pytest_mock"]

# Configure test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API endpoint test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "repository: mark test as repository pattern test"
    )
    config.addinivalue_line(
        "markers", "service: mark test as service pattern test"
    )
    config.addinivalue_line(
        "markers", "dependency_injection: mark test as dependency injection test"
    )

# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_mock_model(data: dict):
        """Create a mock model with the given data."""
        mock_model = Mock()
        for key, value in data.items():
            setattr(mock_model, key, value)
        return mock_model
    
    @staticmethod
    def assert_location_data(location, expected_data):
        """Assert that location data matches expected data."""
        for key, value in expected_data.items():
            assert getattr(location, key) == value
    
    @staticmethod
    def assert_http_error(response, status_code, detail_contains=None):
        """Assert that response contains expected HTTP error."""
        assert response.status_code == status_code
        if detail_contains:
            assert detail_contains in response.json()["detail"]

# Make TestUtils available as a fixture
@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils 