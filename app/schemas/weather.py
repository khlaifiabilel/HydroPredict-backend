"""
Weather schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WeatherDataPoint(BaseModel):
    """Single weather data point"""
    timestamp: str
    temp: Optional[float] = None
    app_temp: Optional[float] = None
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_gust: Optional[float] = None
    wind_direction: Optional[int] = None
    wind_cdir: Optional[str] = None
    pressure: Optional[float] = None
    sea_level_pressure: Optional[float] = None
    clouds: Optional[float] = None
    cloud_low: Optional[float] = None
    cloud_mid: Optional[float] = None
    cloud_high: Optional[float] = None
    visibility: Optional[float] = None
    dew_point: Optional[float] = None
    uv_index: Optional[float] = None
    solar_radiation: Optional[float] = None
    ghi: Optional[float] = None
    dni: Optional[float] = None
    dhi: Optional[float] = None
    snow: Optional[float] = None
    snow_depth: Optional[float] = None
    ozone: Optional[float] = None
    weather_icon: Optional[str] = None
    weather_code: Optional[int] = None
    weather_description: Optional[str] = None
    pod: Optional[str] = None  # Part of day: 'd' or 'n'


class WeatherForecastResponse(BaseModel):
    """Response model for weather forecast"""
    city: str
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    num_hours: int
    data: List[WeatherDataPoint]
    cached: Optional[bool] = None
    cached_at: Optional[str] = None
    demo: Optional[bool] = None

