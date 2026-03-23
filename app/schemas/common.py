"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    device: str
    timestamp: datetime
    uptime_seconds: Optional[float] = None
    cache_status: Optional[str] = None


class CanalActivationConfig(BaseModel):
    """
    Canal activation configuration for custom inference
    Each canal can be set to 0 (inactive) or 1 (active)
    """
    water_pumpe_moret2: Optional[int] = Field(0, ge=0, le=1, description="Moret2 pump status (0=off, 1=on)")
    water_pumpe_moret3: Optional[int] = Field(0, ge=0, le=1, description="Moret3 pump status (0=off, 1=on)")
    water_pumpe_moret4: Optional[int] = Field(0, ge=0, le=1, description="Moret4 pump status (0=off, 1=on)")
    water_pumpe_moret5: Optional[int] = Field(0, ge=0, le=1, description="Moret5 pump status (0=off, 1=on)")
    water_pumpe_warman: Optional[int] = Field(0, ge=0, le=1, description="Warman pump status (0=off, 1=on)")
    canal_bahralouane_km16: Optional[int] = Field(0, ge=0, le=1, description="Bahralouane km16 canal (0=closed, 1=open)")
    canal_bahralouane_pontagricole: Optional[int] = Field(0, ge=0, le=1, description="Bahralouane pont agricole canal (0=closed, 1=open)")
    canal_e1: Optional[int] = Field(0, ge=0, le=1, description="E1 canal (0=closed, 1=open)")
    canal_e4: Optional[int] = Field(0, ge=0, le=1, description="E4 canal (0=closed, 1=open)")

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary for model input"""
        return {
            "water_pumpe_moret2": self.water_pumpe_moret2,
            "water_pumpe_moret3": self.water_pumpe_moret3,
            "water_pumpe_moret4": self.water_pumpe_moret4,
            "water_pumpe_moret5": self.water_pumpe_moret5,
            "water_pumpe_warman": self.water_pumpe_warman,
            "canal_bahralouane_km16": self.canal_bahralouane_km16,
            "canal_bahralouane_pontagricole": self.canal_bahralouane_pontagricole,
            "canal_e1": self.canal_e1,
            "canal_e4": self.canal_e4,
        }

    model_config = {
        "json_schema_extra": {
            "example": {
                "water_pumpe_moret2": 1,
                "water_pumpe_moret3": 0,
                "water_pumpe_moret4": 1,
                "water_pumpe_moret5": 0,
                "water_pumpe_warman": 1,
                "canal_bahralouane_km16": 1,
                "canal_bahralouane_pontagricole": 0,
                "canal_e1": 1,
                "canal_e4": 0
            }
        }
    }


class ModelInfo(BaseModel):
    """Model information"""
    model_type: str
    version: str = "1.0.0"
    checkpoint_path: str
    config_path: str
    max_encoder_length: int
    max_prediction_length: int
    target_variables: List[str]
    num_features: int
    num_parameters: Optional[int] = None
    device: str
    trained_on: Optional[str] = None
    accuracy_metrics: Optional[Dict[str, float]] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime

