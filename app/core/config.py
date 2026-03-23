"""
HydroPredict Backend - Core Settings
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")
    
    # Model Configuration
    model_checkpoint_path: str = Field(
        default="../HydroPredict-model/checkpoints/version_010_20260216_104439/hydropredict-epoch=epoch=08-val_loss=val_loss=1.6287.ckpt",
        description="Path to model checkpoint"
    )
    model_config_path: str = Field(
        default="../HydroPredict-model/configs/model_config.json",
        description="Path to model configuration"
    )
    historical_data_path: str = Field(
        default="../HydroPredict-model/data/input/hourly-data-2024-2025.csv",
        description="Path to historical data"
    )
    
    # Weatherbit API
    weatherbit_config_path: str = Field(
        default="../HydroPredict-model/configs/weatherbit.json",
        description="Path to Weatherbit configuration"
    )
    weatherbit_api_key: Optional[str] = Field(default=None, description="Weatherbit API key")
    
    # Database
    database_url: Optional[str] = Field(default=None, description="PostgreSQL connection URL")
    
    # Redis
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "*"],
        description="Allowed CORS origins"
    )
    
    # Scheduler
    scheduler_enabled: bool = Field(default=True, description="Enable hourly scheduler")
    scheduler_interval_seconds: int = Field(default=3600, description="Scheduler interval in seconds")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for JWT")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

