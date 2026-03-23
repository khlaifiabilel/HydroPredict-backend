"""
API v1 Router
Aggregates all v1 routes
"""

from fastapi import APIRouter

from app.api.v1 import forecast, weather, admin, health, scheduler

router = APIRouter(prefix="/api/v1")

# Include all route modules
router.include_router(forecast.router)
router.include_router(weather.router)
router.include_router(admin.router)
router.include_router(scheduler.router)

# Routes available:
# - /api/v1/forecast/* - Forecast endpoints
# - /api/v1/weather/* - Weather endpoints  
# - /api/v1/admin/* - Admin endpoints
# - /api/v1/scheduler/* - Scheduler endpoints




