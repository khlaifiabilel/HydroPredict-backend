"""
Model Inference Service
Handles loading and inference of the TFT model from HydroPredict-model
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
import json
import torch

logger = logging.getLogger(__name__)


class ModelService:
    """Service for model loading and inference"""
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.config: Optional[Dict[str, Any]] = None
        self.checkpoint_path: Optional[str] = None
        self.config_path: Optional[str] = None
        self.device = "cpu"
        self._loaded = False
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded and self.model is not None
    
    def load_model(self, checkpoint_path: str, config_path: str) -> bool:
        """
        Load model from checkpoint
        
        Args:
            checkpoint_path: Path to model checkpoint
            config_path: Path to model configuration
            
        Returns:
            True if model loaded successfully
        """
        try:
            # Add HydroPredict-model to path for imports
            model_project_root = Path(checkpoint_path).parent.parent.parent
            if str(model_project_root) not in sys.path:
                sys.path.insert(0, str(model_project_root))
            
            # Import inference module from HydroPredict-model
            from src.inference.predict import ModelInference
            
            logger.info(f"Loading model from {checkpoint_path}")
            
            self.model = ModelInference(checkpoint_path, config_path)
            self.checkpoint_path = checkpoint_path
            self.config_path = config_path
            
            # Load config
            if config_path.endswith('.json'):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            self.device = str(self.model.device)
            self._loaded = True
            
            logger.info(f"Model loaded successfully on device: {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self._loaded = False
            return False
    
    def predict_future(
        self,
        historical_data: pd.DataFrame,
        forecast_hours: int = 240
    ) -> pd.DataFrame:
        """
        Generate future predictions
        
        Args:
            historical_data: Historical data DataFrame
            forecast_hours: Number of hours to forecast
            
        Returns:
            DataFrame with predictions
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        return self.model.predict_future(historical_data, forecast_hours)
    
    def predict_with_weather(
        self,
        historical_data: pd.DataFrame,
        weather_data: pd.DataFrame,
        forecast_hours: int = 240
    ) -> pd.DataFrame:
        """
        Generate predictions with weather forecast alignment
        
        Args:
            historical_data: Historical data DataFrame
            weather_data: Weather forecast DataFrame
            forecast_hours: Number of hours to forecast
            
        Returns:
            DataFrame with predictions
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        return self.model.predict_with_weather_forecast(
            historical_data, weather_data, forecast_hours
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.is_loaded:
            return {"error": "Model not loaded"}
        
        num_params = sum(p.numel() for p in self.model.model.parameters())
        
        return {
            "model_type": "Temporal Fusion Transformer",
            "version": "1.0.0",
            "checkpoint_path": str(self.checkpoint_path),
            "config_path": str(self.config_path),
            "max_encoder_length": self.config['time_series']['max_encoder_length'],
            "max_prediction_length": self.config['time_series']['max_prediction_length'],
            "target_variables": self.config['time_series']['target'],
            "num_features": len(self.config['time_series']['time_varying_known_reals']) +
                           len(self.config['time_series']['time_varying_unknown_reals']),
            "num_parameters": num_params,
            "device": self.device,
            "trained_on": "2026-02-10"
        }
    
    def apply_canal_config(
        self,
        data: pd.DataFrame,
        canal_config: Dict[str, int]
    ) -> pd.DataFrame:
        """Apply canal activation configuration to dataframe"""
        data = data.copy()
        for col, value in canal_config.items():
            if col in data.columns:
                data[col] = value
            else:
                data[col] = value
        return data


# Global model service instance
model_service = ModelService()

