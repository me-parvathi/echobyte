from fastapi import APIRouter
from app.api.endpoints import health, users, employees, auth

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"]) 