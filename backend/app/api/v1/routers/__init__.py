"""API v1 domain routers grouped here for convenient import."""

from fastapi import APIRouter

from . import org, employees, assets, leave, timesheets  # noqa: F401

# Optionally expose a combined router
router = APIRouter()

for _r in (org.router, employees.router, assets.router, leave.router, timesheets.router):
    router.include_router(_r) 