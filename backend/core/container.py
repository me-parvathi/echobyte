"""
Dependency injection container for service and repository resolution.
This module implements the Dependency Injection pattern for managing service dependencies.
"""

from typing import Dict, Type, Any, Optional
from .interfaces import DependencyProviderInterface
from .repository import BaseRepository
from .service import BaseService

class DependencyContainer(DependencyProviderInterface):
    """
    Dependency injection container for managing service and repository instances.
    Implements the Dependency Injection pattern for service resolution.
    """
    
    def __init__(self):
        """Initialize the dependency container."""
        self._services: Dict[Type, Type] = {}
        self._repositories: Dict[Type, Type] = {}
        self._instances: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_service(self, service_type: type, implementation: type):
        """Register a service implementation."""
        self._services[service_type] = implementation
    
    def register_repository(self, repository_type: type, implementation: type):
        """Register a repository implementation."""
        self._repositories[repository_type] = implementation
    
    def get_service(self, service_type: type) -> Any:
        """Get a service instance by type."""
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")
        
        implementation = self._services[service_type]
        instance = implementation()
        
        # Check if it's a singleton
        if hasattr(implementation, '__singleton__'):
            self._singletons[service_type] = instance
        
        return instance
    
    def get_repository(self, repository_type: type) -> Any:
        """Get a repository instance by type."""
        if repository_type in self._singletons:
            return self._singletons[repository_type]
        
        if repository_type not in self._repositories:
            raise ValueError(f"Repository {repository_type.__name__} not registered")
        
        implementation = self._repositories[repository_type]
        instance = implementation()
        
        # Check if it's a singleton
        if hasattr(implementation, '__singleton__'):
            self._singletons[repository_type] = instance
        
        return instance
    
    def register_singleton(self, service_type: type, instance: Any):
        """Register a singleton instance."""
        self._singletons[service_type] = instance
    
    def clear(self):
        """Clear all registrations and instances."""
        self._services.clear()
        self._repositories.clear()
        self._instances.clear()
        self._singletons.clear()

# Global dependency container instance
container = DependencyContainer()

# Register services immediately
try:
    from api.location.service import LocationService
    from api.location.repository import LocationRepository
    
    container.register_service(LocationService, LocationService)
    container.register_repository(LocationRepository, LocationRepository)
except ImportError as e:
    print(f"Warning: Could not import location services: {e}")

def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return container

def register_services():
    """Register all services and repositories in the container."""
    # This function will be called during application startup
    # to register all services and repositories
    
    # Import services
    from api.location.service import LocationService
    from api.location.repository import LocationRepository
    
    # Register services
    container.register_service(LocationService, LocationService)
    container.register_repository(LocationRepository, LocationRepository)

# Decorator for singleton services
def singleton(cls):
    """Decorator to mark a class as a singleton."""
    cls.__singleton__ = True
    return cls

# Dependency injection utilities
def inject_service(service_type: type):
    """Decorator to inject a service dependency."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            service = container.get_service(service_type)
            return func(service, *args, **kwargs)
        return wrapper
    return decorator

def inject_repository(repository_type: type):
    """Decorator to inject a repository dependency."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            repository = container.get_repository(repository_type)
            return func(repository, *args, **kwargs)
        return wrapper
    return decorator

# FastAPI dependency injection utilities
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db

def get_service_dependency(service_type: type):
    """Create a FastAPI dependency for a service."""
    def dependency(db: Session = Depends(get_db)):
        service = container.get_service(service_type)
        # Inject database session into service if it has a set_db method
        if hasattr(service, 'set_db'):
            service.set_db(db)
        return service
    return dependency

def get_repository_dependency(repository_type: type):
    """Create a FastAPI dependency for a repository."""
    def dependency(db: Session = Depends(get_db)):
        repository = container.get_repository(repository_type)
        # Inject database session into repository if it has a set_db method
        if hasattr(repository, 'set_db'):
            repository.set_db(db)
        return repository
    return dependency

# Service factory utilities
class ServiceFactory:
    """Factory for creating service instances with dependencies."""
    
    @staticmethod
    def create_service(service_class: type, *args, **kwargs) -> Any:
        """Create a service instance with resolved dependencies."""
        # Check if service has dependencies that need to be resolved
        if hasattr(service_class, '__dependencies__'):
            dependencies = {}
            for dep_name, dep_type in service_class.__dependencies__.items():
                if issubclass(dep_type, BaseRepository):
                    dependencies[dep_name] = container.get_repository(dep_type)
                elif issubclass(dep_type, BaseService):
                    dependencies[dep_name] = container.get_service(dep_type)
            
            # Merge with provided kwargs
            kwargs.update(dependencies)
        
        return service_class(*args, **kwargs)

# Dependency injection context manager
from contextlib import contextmanager

@contextmanager
def dependency_context():
    """Context manager for dependency injection operations."""
    try:
        yield container
    finally:
        # Cleanup if needed
        pass

# Export commonly used items
__all__ = [
    "DependencyContainer",
    "get_container",
    "register_services",
    "singleton",
    "inject_service",
    "inject_repository",
    "get_service_dependency",
    "get_repository_dependency",
    "ServiceFactory",
    "dependency_context"
] 