"""
Forecast API Routes (v1)
Main endpoints for forecast generation and retrieval
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging

from app.core.config import settings
from app.services import model_service, weather_service, forecast_service
from app.schemas import (
    ForecastRequest,
    ForecastResponse,
    ForecastHistoryResponse,
    CanalActivationConfig,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get("/latest", response_model=ForecastResponse)
async def get_latest_forecast(
    hours: int = Query(240, ge=1, le=240, description="Number of hours to forecast"),
    include_confidence: bool = Query(True, description="Include confidence intervals"),
    include_weather: bool = Query(True, description="Use weather data for alignment"),
):
    """
    Get the latest forecast
    
    Returns cached forecast if available (< 1 hour old), otherwise generates new forecast.
    Updated hourly by the scheduler.
    
    Args:
        hours: Number of hours to forecast (max 240)
        include_confidence: Include confidence intervals
        include_weather: Use weather data for alignment
    """
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        response = forecast_service.get_latest_forecast(
            hours=hours,
            include_confidence=include_confidence,
            historical_data_path=settings.historical_data_path,
            weatherbit_config_path=settings.weatherbit_config_path if include_weather else None,
        )
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Forecast error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


@router.post("/custom", response_model=ForecastResponse)
async def generate_custom_forecast(request: ForecastRequest):
    """
    Generate a custom forecast with specific canal configuration
    
    This endpoint allows users to specify canal activation status for scenario analysis.
    The canal_config parameter accepts activation status (0 or 1) for each canal/pump.
    
    Example use cases:
    - "What if we activate pump Moret2 and close canal E4?"
    - "How does water level change with all canals open?"
    """
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        canal_config_dict = request.canal_config.to_dict() if request.canal_config else None
        
        response = forecast_service.generate_forecast(
            hours=request.hours,
            include_confidence=request.include_confidence,
            canal_config=canal_config_dict,
            historical_data_path=settings.historical_data_path,
            weatherbit_config_path=settings.weatherbit_config_path if request.use_latest_weather else None,
            use_weather=request.use_latest_weather,
        )
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Custom forecast error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Custom forecast failed: {str(e)}")


@router.get("/history")
async def get_forecast_history(
    limit: int = Query(24, ge=1, le=100, description="Maximum entries to return"),
    include_data: bool = Query(False, description="Include full forecast data points"),
):
    """
    Get history of past forecast runs.
    
    Args:
        limit: Maximum number of history entries to return (default 24)
        include_data: If True, include full forecast data points in each entry.
                      If False (default), return only summaries for performance.
    """
    return forecast_service.get_history(limit=limit, include_data=include_data)


@router.post("/refresh")
async def refresh_forecast():
    """
    Manually trigger a forecast refresh
    
    This endpoint forces regeneration of the forecast cache
    with the latest weather data.
    """
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Clear cache and regenerate
        forecast_service.clear_cache()
        
        response = forecast_service.generate_forecast(
            hours=240,
            include_confidence=True,
            historical_data_path=settings.historical_data_path,
            weatherbit_config_path=settings.weatherbit_config_path,
            use_weather=True,
        )
        
        return {
            "status": "success",
            "forecast_id": response.forecast_id,
            "generated_at": response.generated_at.isoformat(),
            "num_predictions": response.num_predictions,
        }
        
    except Exception as e:
        logger.error(f"Forecast refresh error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forecast refresh failed: {str(e)}")

