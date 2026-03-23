"""
Forecast schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.schemas.common import CanalActivationConfig


class ForecastRequest(BaseModel):
    """
    Request model for generating forecasts with weather data and canal configuration
    """
    use_latest_weather: bool = Field(
        True,
        description="Fetch latest weather forecast from Weatherbit API"
    )
    hours: int = Field(
        240,
        ge=1,
        le=240,
        description="Number of hours to forecast (max 240 = 10 days)"
    )
    include_confidence: bool = Field(
        True,
        description="Include confidence intervals in response"
    )
    canal_config: Optional[CanalActivationConfig] = Field(
        None,
        description="Canal activation configuration for scenario analysis"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "use_latest_weather": True,
                "hours": 240,
                "include_confidence": True,
                "canal_config": {
                    "water_pumpe_moret2": 1,
                    "water_pumpe_moret3": 0,
                    "canal_e1": 1,
                    "canal_e4": 0
                }
            }
        }
    }


class ForecastDataPoint(BaseModel):
    """Single forecast data point with confidence intervals"""
    timestamp: datetime
    water_level_m: float
    water_level_lower: Optional[float] = None
    water_level_upper: Optional[float] = None
    water_density_kg_m3: float
    water_density_lower: Optional[float] = None
    water_density_upper: Optional[float] = None
    confidence: Optional[float] = 0.95
    
    # Weather context (optional)
    air_temperature_celsius: Optional[float] = None
    humidity_percent: Optional[float] = None
    precipitation_mm: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    atmospheric_pressure_hpa: Optional[float] = None


class ForecastResponse(BaseModel):
    """Response model for forecast endpoint"""
    forecast_id: str
    generated_at: datetime
    forecast_start: datetime
    forecast_end: datetime
    num_predictions: int
    model_version: str
    canal_config_used: Optional[Dict[str, int]] = None
    data: List[ForecastDataPoint]

    model_config = {
        "json_schema_extra": {
            "example": {
                "forecast_id": "550e8400-e29b-41d4-a716-446655440000",
                "generated_at": "2026-03-23T12:00:00Z",
                "forecast_start": "2026-03-23T13:00:00Z",
                "forecast_end": "2026-04-02T13:00:00Z",
                "num_predictions": 240,
                "model_version": "TFT-v1.0",
                "data": [
                    {
                        "timestamp": "2026-03-23T13:00:00Z",
                        "water_level_m": -85.2,
                        "water_level_lower": -86.1,
                        "water_level_upper": -84.3,
                        "water_density_kg_m3": 1203.5,
                        "water_density_lower": 1202.1,
                        "water_density_upper": 1204.9,
                        "confidence": 0.95
                    }
                ]
            }
        }
    }


class ForecastHistoryEntry(BaseModel):
    """Single forecast history entry"""
    forecast_id: str
    generated_at: str
    forecast_start: Optional[str] = None
    forecast_end: Optional[str] = None
    num_predictions: int
    model_version: str
    source: str  # "scheduler" or "api"
    summary: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None


class ForecastHistoryResponse(BaseModel):
    """Response for forecast history"""
    total: int
    limit: int
    entries: List[ForecastHistoryEntry]


class AsyncJobResponse(BaseModel):
    """Response for async batch prediction jobs"""
    job_id: str
    status: str
    estimated_completion: Optional[datetime] = None
    created_at: datetime

