"""
Forecast Service
Handles forecast generation, caching, and history management
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd

from app.services.model_service import model_service
from app.services.weather_service import weather_service
from app.schemas.forecast import ForecastDataPoint, ForecastResponse

logger = logging.getLogger(__name__)


class ForecastService:
    """Service for forecast generation and management"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []
        self.max_history = 100
        self.cache_ttl_seconds = 3600
    
    def generate_forecast(
        self,
        hours: int = 240,
        include_confidence: bool = True,
        canal_config: Optional[Dict[str, int]] = None,
        historical_data_path: Optional[str] = None,
        weatherbit_config_path: Optional[str] = None,
        use_weather: bool = True
    ) -> ForecastResponse:
        """
        Generate a forecast
        
        Args:
            hours: Number of hours to forecast
            include_confidence: Include confidence intervals
            canal_config: Canal activation configuration
            historical_data_path: Path to historical data CSV
            weatherbit_config_path: Path to Weatherbit config
            use_weather: Whether to use weather data for alignment
            
        Returns:
            ForecastResponse with predictions
        """
        if not model_service.is_loaded:
            raise RuntimeError("Model not loaded")
        
        # Load historical data
        if not historical_data_path:
            raise ValueError("Historical data path required")
        
        if not Path(historical_data_path).exists():
            raise FileNotFoundError(f"Historical data not found: {historical_data_path}")
        
        df = pd.read_csv(historical_data_path, low_memory=False)
        df['measurement_date'] = pd.to_datetime(df['measurement_date'])
        
        # Apply canal config if provided
        if canal_config:
            df = model_service.apply_canal_config(df, canal_config)
        
        # Fetch weather and generate predictions
        weather_df = None
        if use_weather and weatherbit_config_path:
            weather_df = weather_service.fetch_weather_forecast(
                config_path=weatherbit_config_path,
                hours=hours
            )
        
        if weather_df is not None:
            predictions_df = model_service.predict_with_weather(df, weather_df, hours)
        else:
            predictions_df = model_service.predict_future(df, hours)
        
        # Build response
        forecast_id = str(uuid.uuid4())
        generated_at = datetime.now()
        
        data_points = []
        for _, row in predictions_df.head(hours).iterrows():
            point = ForecastDataPoint(
                timestamp=pd.to_datetime(row.get('forecast_date', generated_at)),
                water_level_m=row.get('water_level_m_mice_pred', 0),
                water_density_kg_m3=row.get('water_density_kg_m3_mice_pred', 0),
                water_level_lower=row.get('water_level_m_mice_q10') if include_confidence else None,
                water_level_upper=row.get('water_level_m_mice_q90') if include_confidence else None,
                water_density_lower=row.get('water_density_kg_m3_mice_q10') if include_confidence else None,
                water_density_upper=row.get('water_density_kg_m3_mice_q90') if include_confidence else None,
                confidence=0.95 if include_confidence else None,
            )
            data_points.append(point)
        
        response = ForecastResponse(
            forecast_id=forecast_id,
            generated_at=generated_at,
            forecast_start=data_points[0].timestamp if data_points else generated_at,
            forecast_end=data_points[-1].timestamp if data_points else generated_at,
            num_predictions=len(data_points),
            model_version="TFT-v1.0",
            canal_config_used=canal_config,
            data=data_points,
        )
        
        # Add to history
        self._add_to_history(response, predictions_df, source="api")
        
        return response
    
    def get_latest_forecast(
        self,
        hours: int = 240,
        include_confidence: bool = True,
        historical_data_path: Optional[str] = None,
        weatherbit_config_path: Optional[str] = None,
    ) -> ForecastResponse:
        """
        Get the latest forecast, using cache if available
        
        Returns cached forecast if < 1 hour old, otherwise generates new
        """
        # Check cache
        cache_key = f"forecast_latest_{hours}_{include_confidence}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            age = (datetime.now() - cached['generated_at']).total_seconds()
            if age < self.cache_ttl_seconds:
                return cached['response']
        
        # Generate new forecast
        response = self.generate_forecast(
            hours=hours,
            include_confidence=include_confidence,
            historical_data_path=historical_data_path,
            weatherbit_config_path=weatherbit_config_path,
            use_weather=True
        )
        
        # Cache it
        self.cache[cache_key] = {
            'response': response,
            'generated_at': datetime.now()
        }
        
        return response
    
    def _add_to_history(
        self,
        response: ForecastResponse,
        predictions_df: pd.DataFrame,
        source: str = "api"
    ):
        """Add forecast to history"""
        history_entry = {
            "forecast_id": response.forecast_id,
            "generated_at": response.generated_at.isoformat(),
            "forecast_start": response.forecast_start.isoformat() if response.forecast_start else None,
            "forecast_end": response.forecast_end.isoformat() if response.forecast_end else None,
            "num_predictions": response.num_predictions,
            "model_version": response.model_version,
            "source": source,
            "summary": {
                "water_level_mean": float(predictions_df['water_level_m_mice_pred'].mean()) if 'water_level_m_mice_pred' in predictions_df.columns else None,
                "water_level_min": float(predictions_df['water_level_m_mice_pred'].min()) if 'water_level_m_mice_pred' in predictions_df.columns else None,
                "water_level_max": float(predictions_df['water_level_m_mice_pred'].max()) if 'water_level_m_mice_pred' in predictions_df.columns else None,
                "water_density_mean": float(predictions_df['water_density_kg_m3_mice_pred'].mean()) if 'water_density_kg_m3_mice_pred' in predictions_df.columns else None,
            },
            "data": [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "water_level_m": p.water_level_m,
                    "water_density_kg_m3": p.water_density_kg_m3,
                    "water_level_lower": p.water_level_lower,
                    "water_level_upper": p.water_level_upper,
                }
                for p in response.data
            ],
        }
        
        self.history.insert(0, history_entry)
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
    
    def get_history(self, limit: int = 24, include_data: bool = False) -> Dict[str, Any]:
        """Get forecast history"""
        entries = self.history[:limit]
        
        if not include_data:
            entries = [
                {k: v for k, v in entry.items() if k != "data"}
                for entry in entries
            ]
        
        return {
            "total": len(self.history),
            "limit": limit,
            "entries": entries,
        }
    
    def clear_cache(self):
        """Clear forecast cache"""
        self.cache.clear()


# Global forecast service instance
forecast_service = ForecastService()

