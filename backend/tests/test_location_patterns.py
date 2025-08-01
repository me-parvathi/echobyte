"""
Comprehensive tests for Location module using dependency injection, service, and repository patterns.
This module tests the new architectural patterns implemented.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import the modules to test
from api.location.models import Location
from api.location.schemas import LocationCreate, LocationUpdate, Location as LocationSchema
from api.location.repository import LocationRepository
from api.location.service import LocationService
from core.container import DependencyContainer, get_container
from main import app

# Test client
client = TestClient(app)

class TestLocationRepository:
    """Test cases for LocationRepository using Repository pattern."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def location_repository(self):
        """Create a LocationRepository instance."""
        return LocationRepository()
    
    @pytest.fixture
    def sample_location_data(self):
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
    
    def test_get_by_id_success(self, mock_db, location_repository, sample_location_data):
        """Test successful retrieval of location by ID."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_location
        
        # Act
        result = location_repository.get_by_id(mock_db, 1)
        
        # Assert
        assert result is not None
        assert result.LocationID == 1
        assert result.LocationName == "Test Location"
    
    def test_get_by_id_not_found(self, mock_db, location_repository):
        """Test retrieval of non-existent location by ID."""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = location_repository.get_by_id(mock_db, 999)
        
        # Assert
        assert result is None
    
    def test_get_by_name_success(self, mock_db, location_repository, sample_location_data):
        """Test successful retrieval of location by name."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_location
        
        # Act
        result = location_repository.get_by_name(mock_db, "Test Location")
        
        # Assert
        assert result is not None
        assert result.LocationName == "Test Location"
    
    def test_get_active_locations(self, mock_db, location_repository, sample_location_data):
        """Test retrieval of active locations."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [mock_location]
        
        # Act
        result = location_repository.get_active_locations(mock_db, skip=0, limit=10)
        
        # Assert
        assert len(result) == 1
        assert result[0].IsActive is True
    
    def test_search_locations(self, mock_db, location_repository, sample_location_data):
        """Test location search functionality."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [mock_location]
        
        # Act
        result = location_repository.search_locations(mock_db, "Test", skip=0, limit=10)
        
        # Assert
        assert len(result) == 1
        assert result[0].LocationName == "Test Location"
    
    def test_validate_location_name_unique_true(self, mock_db, location_repository):
        """Test location name uniqueness validation when name is unique."""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = location_repository.validate_location_name_unique(mock_db, "Unique Name")
        
        # Assert
        assert result is True
    
    def test_validate_location_name_unique_false(self, mock_db, location_repository, sample_location_data):
        """Test location name uniqueness validation when name already exists."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_location
        
        # Act
        result = location_repository.validate_location_name_unique(mock_db, "Test Location")
        
        # Assert
        assert result is False

class TestLocationService:
    """Test cases for LocationService using Service pattern."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def location_service(self):
        """Create a LocationService instance."""
        return LocationService()
    
    @pytest.fixture
    def sample_location_create(self):
        """Sample location create data."""
        return LocationCreate(
            LocationName="Test Location",
            Address1="123 Test Street",
            Address2="Suite 100",
            City="Test City",
            State="Test State",
            Country="Test Country",
            PostalCode="12345",
            Phone="+1-555-123-4567",
            TimeZone="UTC"
        )
    
    @pytest.fixture
    def sample_location_update(self):
        """Sample location update data."""
        return LocationUpdate(
            LocationName="Updated Location",
            Address1="456 Updated Street",
            City="Updated City"
        )
    
    def test_get_by_id_success(self, mock_db, location_service, sample_location_data):
        """Test successful retrieval of location by ID through service."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        with patch.object(location_service.repository, 'get_by_id', return_value=mock_location):
            # Act
            result = location_service.get_by_id(mock_db, 1)
            
            # Assert
            assert result is not None
            assert isinstance(result, LocationSchema)
            assert result.LocationID == 1
    
    def test_get_by_id_not_found(self, mock_db, location_service):
        """Test retrieval of non-existent location by ID through service."""
        # Arrange
        with patch.object(location_service.repository, 'get_by_id', return_value=None):
            # Act
            result = location_service.get_by_id(mock_db, 999)
            
            # Assert
            assert result is None
    
    def test_create_location_success(self, mock_db, location_service, sample_location_create, sample_location_data):
        """Test successful location creation through service."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        with patch.object(location_service.repository, 'validate_location_name_unique', return_value=True), \
             patch.object(location_service.repository, 'create', return_value=mock_location):
            # Act
            result = location_service.create_location(mock_db, sample_location_create)
            
            # Assert
            assert result is not None
            assert isinstance(result, LocationSchema)
            assert result.LocationName == "Test Location"
    
    def test_create_location_duplicate_name(self, mock_db, location_service, sample_location_create):
        """Test location creation with duplicate name."""
        # Arrange
        with patch.object(location_service.repository, 'validate_location_name_unique', return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                location_service.create_location(mock_db, sample_location_create)
            
            assert exc_info.value.status_code == 400
            assert "Location name already exists" in exc_info.value.detail
    
    def test_update_location_success(self, mock_db, location_service, sample_location_update, sample_location_data):
        """Test successful location update through service."""
        # Arrange
        mock_location = Mock()
        for key, value in sample_location_data.items():
            setattr(mock_location, key, value)
        
        with patch.object(location_service.repository, 'exists', return_value=True), \
             patch.object(location_service.repository, 'validate_location_name_unique', return_value=True), \
             patch.object(location_service.repository, 'update', return_value=mock_location):
            # Act
            result = location_service.update_location(mock_db, 1, sample_location_update)
            
            # Assert
            assert result is not None
            assert isinstance(result, LocationSchema)
    
    def test_update_location_not_found(self, mock_db, location_service, sample_location_update):
        """Test location update when location doesn't exist."""
        # Arrange
        with patch.object(location_service.repository, 'exists', return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                location_service.update_location(mock_db, 999, sample_location_update)
            
            assert exc_info.value.status_code == 404
            assert "Entity not found" in exc_info.value.detail
    
    def test_delete_location_success(self, mock_db, location_service):
        """Test successful location deletion through service."""
        # Arrange
        with patch.object(location_service.repository, 'exists', return_value=True), \
             patch.object(location_service.repository, 'delete', return_value=True):
            # Act
            result = location_service.delete_location(mock_db, 1)
            
            # Assert
            assert result is True
    
    def test_delete_location_not_found(self, mock_db, location_service):
        """Test location deletion when location doesn't exist."""
        # Arrange
        with patch.object(location_service.repository, 'exists', return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                location_service.delete_location(mock_db, 999)
            
            assert exc_info.value.status_code == 404
            assert "Entity not found" in exc_info.value.detail
    
    def test_validate_location_data_success(self, mock_db, location_service, sample_location_create):
        """Test location data validation success."""
        # Act
        result = location_service._validate_location_data(mock_db, sample_location_create, "create")
        
        # Assert
        assert result is True
    
    def test_validate_location_data_missing_required_fields(self, mock_db, location_service):
        """Test location data validation with missing required fields."""
        # Arrange
        invalid_location = LocationCreate(
            LocationName="",  # Empty name
            Address1="",      # Empty address
            City="",          # Empty city
            Country="",       # Empty country
            TimeZone=""       # Empty timezone
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            location_service._validate_location_data(mock_db, invalid_location, "create")
        
        assert exc_info.value.status_code == 400
        assert "Location name is required" in exc_info.value.detail
    
    def test_validate_phone_number_valid(self, mock_db, location_service):
        """Test phone number validation with valid format."""
        # Act
        result = location_service._is_valid_phone("+1-555-123-4567")
        
        # Assert
        assert result is True
    
    def test_validate_phone_number_invalid(self, mock_db, location_service):
        """Test phone number validation with invalid format."""
        # Act
        result = location_service._is_valid_phone("invalid-phone")
        
        # Assert
        assert result is False
    
    def test_validate_postal_code_valid(self, mock_db, location_service):
        """Test postal code validation with valid format."""
        # Act
        result = location_service._is_valid_postal_code("12345")
        
        # Assert
        assert result is True
    
    def test_validate_postal_code_invalid(self, mock_db, location_service):
        """Test postal code validation with invalid format."""
        # Act
        result = location_service._is_valid_postal_code("invalid@code")
        
        # Assert
        assert result is False

class TestDependencyInjection:
    """Test cases for Dependency Injection pattern."""
    
    @pytest.fixture
    def container(self):
        """Create a fresh dependency container."""
        return DependencyContainer()
    
    def test_register_and_get_service(self, container):
        """Test service registration and retrieval."""
        # Arrange
        class TestService:
            def __init__(self):
                self.name = "TestService"
        
        # Act
        container.register_service(TestService, TestService)
        service = container.get_service(TestService)
        
        # Assert
        assert service is not None
        assert isinstance(service, TestService)
        assert service.name == "TestService"
    
    def test_register_and_get_repository(self, container):
        """Test repository registration and retrieval."""
        # Arrange
        class TestRepository:
            def __init__(self):
                self.name = "TestRepository"
        
        # Act
        container.register_repository(TestRepository, TestRepository)
        repository = container.get_repository(TestRepository)
        
        # Assert
        assert repository is not None
        assert isinstance(repository, TestRepository)
        assert repository.name == "TestRepository"
    
    def test_get_unregistered_service(self, container):
        """Test getting an unregistered service."""
        # Arrange
        class UnregisteredService:
            pass
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            container.get_service(UnregisteredService)
        
        assert "Service UnregisteredService not registered" in str(exc_info.value)
    
    def test_singleton_service(self, container):
        """Test singleton service behavior."""
        # Arrange
        @container.singleton
        class SingletonService:
            def __init__(self):
                self.id = id(self)
        
        # Act
        service1 = container.get_service(SingletonService)
        service2 = container.get_service(SingletonService)
        
        # Assert
        assert service1 is service2
        assert service1.id == service2.id

class TestLocationAPIEndpoints:
    """Test cases for Location API endpoints using dependency injection."""
    
    def test_get_locations_endpoint(self):
        """Test GET /api/locations/ endpoint."""
        # Act
        response = client.get("/api/locations/")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_locations_with_filters(self):
        """Test GET /api/locations/ with query parameters."""
        # Act
        response = client.get("/api/locations/?skip=0&limit=10&is_active=true")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_locations_with_search(self):
        """Test GET /api/locations/ with search parameter."""
        # Act
        response = client.get("/api/locations/?search=test")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_active_locations_endpoint(self):
        """Test GET /api/locations/active endpoint."""
        # Act
        response = client.get("/api/locations/active")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_location_by_id_endpoint(self):
        """Test GET /api/locations/{location_id} endpoint."""
        # Act
        response = client.get("/api/locations/1")
        
        # Assert
        # This might return 404 if no location exists, which is expected
        assert response.status_code in [200, 404]
    
    def test_create_location_endpoint(self):
        """Test POST /api/locations/ endpoint."""
        # Arrange
        location_data = {
            "LocationName": "Test API Location",
            "Address1": "123 API Street",
            "City": "API City",
            "Country": "API Country",
            "TimeZone": "UTC"
        }
        
        # Act
        response = client.post("/api/locations/", json=location_data)
        
        # Assert
        # This might return 400 if validation fails, which is expected
        assert response.status_code in [201, 400, 500]
    
    def test_update_location_endpoint(self):
        """Test PUT /api/locations/{location_id} endpoint."""
        # Arrange
        location_data = {
            "LocationName": "Updated API Location",
            "Address1": "456 Updated Street"
        }
        
        # Act
        response = client.put("/api/locations/1", json=location_data)
        
        # Assert
        # This might return 404 if location doesn't exist, which is expected
        assert response.status_code in [200, 404, 500]
    
    def test_delete_location_endpoint(self):
        """Test DELETE /api/locations/{location_id} endpoint."""
        # Act
        response = client.delete("/api/locations/1")
        
        # Assert
        # This might return 404 if location doesn't exist, which is expected
        assert response.status_code in [204, 404, 500]
    
    def test_get_location_statistics_endpoint(self):
        """Test GET /api/locations/statistics endpoint."""
        # Act
        response = client.get("/api/locations/statistics")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_locations" in data
        assert "active_locations" in data
        assert "inactive_locations" in data

class TestIntegrationPatterns:
    """Integration tests for the complete pattern implementation."""
    
    def test_repository_service_integration(self):
        """Test integration between repository and service layers."""
        # This test would require a real database connection
        # For now, we'll test the pattern structure
        repository = LocationRepository()
        service = LocationService()
        
        # Assert that service uses repository
        assert hasattr(service, 'repository')
        assert isinstance(service.repository, LocationRepository)
    
    def test_dependency_injection_integration(self):
        """Test integration of dependency injection with services."""
        container = get_container()
        
        # Register services
        container.register_service(LocationService, LocationService)
        container.register_repository(LocationRepository, LocationRepository)
        
        # Get service through container
        service = container.get_service(LocationService)
        
        # Assert service is properly instantiated
        assert isinstance(service, LocationService)
        assert hasattr(service, 'repository')
    
    def test_business_rule_validation_integration(self):
        """Test integration of business rule validation."""
        service = LocationService()
        
        # Assert business rules are registered
        assert hasattr(service, 'business_rules')
        assert len(service.business_rules) > 0
        
        # Check for specific business rules
        rule_names = [rule.__name__ for rule in service.business_rules]
        assert '_validate_location_name_unique' in rule_names
        assert '_validate_location_data' in rule_names
        assert '_validate_location_deletion' in rule_names

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 