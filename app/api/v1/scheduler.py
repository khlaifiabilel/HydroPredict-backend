"""
Scheduler API Routes (v1)
Endpoints for scheduler management - direct access without /admin prefix
"""

from fastapi import APIRouter, HTTPException
import logging

from app.core.config import settings
from app.services import model_service, weather_service, forecast_service, scheduler_service
from app.schemas import SchedulerStatus, SchedulerTriggerResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status():
    """Get the current status of the hourly scheduler."""
    status = scheduler_service.get_status()
    return SchedulerStatus(**status)


@router.post("/trigger", response_model=SchedulerTriggerResponse)
async def trigger_scheduler():
    """Manually trigger a scheduler cycle (weather fetch + inference)."""
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    result = await scheduler_service.trigger_manual(
        model_service=model_service,
        weather_service=weather_service,
        forecast_service=forecast_service,
        historical_data_path=settings.historical_data_path,
        weatherbit_config_path=settings.weatherbit_config_path,
    )
    
    return SchedulerTriggerResponse(**result)

