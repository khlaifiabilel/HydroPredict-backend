"""
Admin schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserInfo(BaseModel):
    """User information"""
    user_id: str
    email: str
    role: str
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserRoleUpdate(BaseModel):
    """Request to update user role"""
    role: str = Field(..., description="New role for the user")


class SystemSettings(BaseModel):
    """System settings"""
    scheduler_enabled: bool = True
    scheduler_interval_seconds: int = 3600
    forecast_cache_ttl_seconds: int = 3600
    weather_cache_ttl_seconds: int = 3600
    max_forecast_history: int = 100


class SchedulerStatus(BaseModel):
    """Scheduler status information"""
    running: bool
    interval_seconds: int
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int
    last_error: Optional[str] = None
    last_weather_fetch: Optional[str] = None
    last_inference_run: Optional[str] = None
    forecast_result_cache: Optional[Dict[str, Any]] = None


class SchedulerTriggerResponse(BaseModel):
    """Response after triggering scheduler"""
    status: str
    last_run: Optional[str] = None
    run_count: int
    last_error: Optional[str] = None

