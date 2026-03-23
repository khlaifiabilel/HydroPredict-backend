"""
HydroPredict Backend - Services Package
"""

from app.services.model_service import model_service, ModelService
from app.services.weather_service import weather_service, WeatherService
from app.services.forecast_service import forecast_service, ForecastService
from app.services.scheduler_service import scheduler_service, SchedulerService

__all__ = [
    "model_service",
    "ModelService",
    "weather_service",
    "WeatherService",
    "forecast_service",
    "ForecastService",
    "scheduler_service",
    "SchedulerService",
]

