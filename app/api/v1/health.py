"""
Health & Model API Routes (v1)
General health checks and model information
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import time
import logging

from app.core.config import settings
from app.services import model_service, forecast_service
from app.schemas import HealthResponse, ModelInfo

logger = logging.getLogger(__name__)
router = APIRouter(tags=["General"])

# Track app start time
APP_START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    device = "cpu"
    if model_service.is_loaded:
        device = model_service.device
    
    cache_status = "connected" if len(forecast_service.cache) > 0 else "empty"
    
    return HealthResponse(
        status="healthy" if model_service.is_loaded else "model_not_loaded",
        model_loaded=model_service.is_loaded,
        device=device,
        timestamp=datetime.now(),
        uptime_seconds=time.time() - APP_START_TIME,
        cache_status=cache_status,
    )


@router.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Get model information"""
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    info = model_service.get_model_info()
    return ModelInfo(**info)

