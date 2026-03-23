"""
Weather API Routes (v1)
Endpoints for weather forecast retrieval
"""

from fastapi import APIRouter, HTTPException, Query
import logging

from app.core.config import settings
from app.services import weather_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/forecast")
async def get_weather_forecast(
    hours: int = Query(240, ge=1, le=240, description="Number of hours to fetch"),
):
    """
    Fetch live weather forecast from Weatherbit API.
    
    Uses scheduler cache if available (< 1h old), otherwise fetches live.
    Falls back to realistic demo data if the API is unavailable.
    
    Args:
        hours: Number of hours to forecast (max 240)
    """
    try:
        return weather_service.get_weather_api_response(
            hours=hours,
            config_path=settings.weatherbit_config_path
        )
        
    except Exception as e:
        logger.warning(f"Weather forecast error, falling back to demo data: {e}")
        return weather_service.generate_demo_weather(min(hours, 240))

