"""
HydroPredict Backend - Schemas Package
"""

from app.schemas.common import (
    HealthResponse,
    CanalActivationConfig,
    ModelInfo,
    ErrorResponse,
)

from app.schemas.forecast import (
    ForecastRequest,
    ForecastDataPoint,
    ForecastResponse,
    ForecastHistoryEntry,
    ForecastHistoryResponse,
    AsyncJobResponse,
)

from app.schemas.weather import (
    WeatherDataPoint,
    WeatherForecastResponse,
)

from app.schemas.admin import (
    UserInfo,
    UserRoleUpdate,
    SystemSettings,
    SchedulerStatus,
    SchedulerTriggerResponse,
)

__all__ = [
    # Common
    "HealthResponse",
    "CanalActivationConfig",
    "ModelInfo",
    "ErrorResponse",
    # Forecast
    "ForecastRequest",
    "ForecastDataPoint",
    "ForecastResponse",
    "ForecastHistoryEntry",
    "ForecastHistoryResponse",
    "AsyncJobResponse",
    # Weather
    "WeatherDataPoint",
    "WeatherForecastResponse",
    # Admin
    "UserInfo",
    "UserRoleUpdate",
    "SystemSettings",
    "SchedulerStatus",
    "SchedulerTriggerResponse",
]

