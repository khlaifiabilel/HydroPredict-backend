"""
HydroPredict Backend - Main Application
FastAPI application for water level forecasting
"""

import sys
import time
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import router as v1_router
from app.api.v1.health import router as health_router
from app.services import model_service, weather_service, forecast_service, scheduler_service
from app.schemas import ErrorResponse

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track app start time
APP_START_TIME = time.time()


def load_model():
    """Load the ML model at startup"""
    checkpoint_path = settings.model_checkpoint_path
    config_path = settings.model_config_path
    
    # Resolve relative paths
    if not Path(checkpoint_path).is_absolute():
        checkpoint_path = str(Path(__file__).parent.parent / checkpoint_path)
    if not Path(config_path).is_absolute():
        config_path = str(Path(__file__).parent.parent / config_path)
    
    # Add model project to path
    model_project_root = Path(checkpoint_path).parent.parent.parent
    if str(model_project_root) not in sys.path:
        sys.path.insert(0, str(model_project_root))
    
    if Path(checkpoint_path).exists():
        success = model_service.load_model(checkpoint_path, config_path)
        if success:
            logger.info("✅ Model loaded successfully")
        else:
            logger.warning("⚠️ Failed to load model")
    else:
        logger.warning(f"⚠️ Checkpoint not found at {checkpoint_path}")
        logger.info("Model will need to be loaded manually or paths corrected")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting HydroPredict Backend...")
    
    # Load model
    load_model()
    
    # Start scheduler if enabled
    if settings.scheduler_enabled and model_service.is_loaded:
        historical_data_path = settings.historical_data_path
        weatherbit_config_path = settings.weatherbit_config_path
        
        # Resolve relative paths
        if not Path(historical_data_path).is_absolute():
            historical_data_path = str(Path(__file__).parent.parent / historical_data_path)
        if not Path(weatherbit_config_path).is_absolute():
            weatherbit_config_path = str(Path(__file__).parent.parent / weatherbit_config_path)
        
        await scheduler_service.start(
            model_service=model_service,
            weather_service=weather_service,
            forecast_service=forecast_service,
            historical_data_path=historical_data_path,
            weatherbit_config_path=weatherbit_config_path,
        )
        logger.info("✅ Scheduler started")
    
    logger.info("✅ HydroPredict Backend ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HydroPredict Backend...")
    await scheduler_service.stop()
    logger.info("👋 Goodbye!")


# Initialize FastAPI app
app = FastAPI(
    title="HydroPredict API",
    description="""
    Water level forecasting API using Temporal Fusion Transformer (TFT)
    
    ## Features
    - **Real-time forecasts:** 240-hour (10-day) water level and density predictions
    - **Confidence intervals:** Probabilistic forecasting with uncertainty quantification
    - **Canal configuration:** Custom scenario analysis with canal activation settings
    - **Weather integration:** Automatic Weatherbit API integration for meteorological data
    
    ## Endpoints
    - `/api/v1/forecast/latest` - Get latest forecast
    - `/api/v1/forecast/custom` - Generate custom forecast with canal configuration
    - `/api/v1/forecast/history` - Get forecast history
    - `/api/v1/weather/forecast` - Get weather forecast
    - `/health` - Service health check
    - `/model/info` - Model information
    
    ## Dashboard Integration
    This API is designed for use with the HydroPredict Dashboard web application.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "General", "description": "Health checks and general information"},
        {"name": "Forecast", "description": "Forecast generation and retrieval"},
        {"name": "Weather", "description": "Weather forecast data"},
        {"name": "Admin", "description": "Administration and scheduler management"},
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Root Routes ====================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "HydroPredict API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1"
    }


# Include routers
app.include_router(health_router)
app.include_router(v1_router)


# ==================== Exception Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    from datetime import datetime
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": None,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    from datetime import datetime
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None,
            "timestamp": datetime.now().isoformat()
        }
    )

