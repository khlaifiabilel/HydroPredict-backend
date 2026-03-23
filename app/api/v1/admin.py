"""
Admin API Routes (v1)
Endpoints for administration and scheduler management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.core.config import settings
from app.services import model_service, weather_service, forecast_service, scheduler_service
from app.schemas import (
    UserInfo,
    UserRoleUpdate,
    SystemSettings,
    SchedulerStatus,
    SchedulerTriggerResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== User Management ====================
# Note: These are placeholder endpoints. In production, integrate with
# AWS Cognito or another identity provider.

@router.get("/users", response_model=List[UserInfo])
async def get_users():
    """
    Get all users (placeholder)
    
    In production, this would integrate with AWS Cognito or similar.
    """
    # Placeholder - return empty list
    return []


@router.put("/users/{user_id}")
async def update_user_role(user_id: str, update: UserRoleUpdate):
    """
    Update user role (placeholder)
    
    In production, this would integrate with AWS Cognito or similar.
    """
    # Placeholder
    return {"user_id": user_id, "role": update.role, "status": "updated"}


# ==================== System Settings ====================

@router.get("/settings", response_model=SystemSettings)
async def get_settings():
    """Get system settings"""
    return SystemSettings(
        scheduler_enabled=settings.scheduler_enabled,
        scheduler_interval_seconds=settings.scheduler_interval_seconds,
        forecast_cache_ttl_seconds=forecast_service.cache_ttl_seconds,
        weather_cache_ttl_seconds=weather_service.cache_ttl_seconds,
        max_forecast_history=forecast_service.max_history,
    )


@router.put("/settings")
async def update_settings(new_settings: SystemSettings):
    """
    Update system settings
    
    Note: Some settings may require restart to take effect.
    """
    # Update service settings
    forecast_service.cache_ttl_seconds = new_settings.forecast_cache_ttl_seconds
    weather_service.cache_ttl_seconds = new_settings.weather_cache_ttl_seconds
    forecast_service.max_history = new_settings.max_forecast_history
    scheduler_service.state["interval_seconds"] = new_settings.scheduler_interval_seconds
    
    return {"status": "updated", "settings": new_settings}


# Note: Scheduler routes are available at /api/v1/scheduler/*
# See app/api/v1/scheduler.py for implementation


