"""
Scheduler Service
Handles hourly forecast refresh and background tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled forecast updates"""
    
    def __init__(self):
        self.state = {
            "running": False,
            "interval_seconds": 3600,  # 1 hour
            "last_run": None,
            "next_run": None,
            "run_count": 0,
            "last_error": None,
            "last_weather_fetch": None,
            "last_inference_run": None,
            "forecast_result_cache": None,
        }
        self._task: Optional[asyncio.Task] = None
    
    async def start(
        self,
        model_service,
        weather_service,
        forecast_service,
        historical_data_path: str,
        weatherbit_config_path: str
    ):
        """Start the scheduler"""
        if self._task and not self._task.done():
            logger.warning("Scheduler already running")
            return
        
        self._task = asyncio.create_task(
            self._scheduler_loop(
                model_service,
                weather_service,
                forecast_service,
                historical_data_path,
                weatherbit_config_path
            )
        )
        logger.info("Scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.state["running"] = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")
    
    async def _scheduler_loop(
        self,
        model_service,
        weather_service,
        forecast_service,
        historical_data_path: str,
        weatherbit_config_path: str
    ):
        """Background loop that runs hourly job"""
        logger.info(f"Hourly scheduler started (interval={self.state['interval_seconds']}s)")
        self.state["running"] = True
        
        # Run immediately on startup
        await self._run_hourly_job(
            model_service,
            weather_service,
            forecast_service,
            historical_data_path,
            weatherbit_config_path
        )
        
        while self.state["running"]:
            self.state["next_run"] = (
                datetime.now() + timedelta(seconds=self.state["interval_seconds"])
            ).isoformat()
            
            try:
                await asyncio.sleep(self.state["interval_seconds"])
            except asyncio.CancelledError:
                break
            
            if self.state["running"]:
                await self._run_hourly_job(
                    model_service,
                    weather_service,
                    forecast_service,
                    historical_data_path,
                    weatherbit_config_path
                )
        
        logger.info("Hourly scheduler stopped")
    
    async def _run_hourly_job(
        self,
        model_service,
        weather_service,
        forecast_service,
        historical_data_path: str,
        weatherbit_config_path: str
    ):
        """Execute one cycle: fetch weather + run inference"""
        logger.info("⏰ Hourly scheduler: starting weather fetch + inference cycle")
        self.state["last_run"] = datetime.now().isoformat()
        self.state["run_count"] += 1
        
        try:
            # 1) Fetch fresh weather forecast
            weather_df = weather_service.fetch_weather_forecast(
                config_path=weatherbit_config_path,
                hours=240
            )
            
            if weather_df is not None:
                self.state["last_weather_fetch"] = datetime.now().isoformat()
                logger.info(f"  ✅ Weather fetched: {len(weather_df)} hours")
            else:
                logger.warning("  ⚠️ Weather fetch returned None")
            
            # 2) Run inference if model is loaded
            if model_service.is_loaded:
                if Path(historical_data_path).exists():
                    response = forecast_service.generate_forecast(
                        hours=240,
                        include_confidence=True,
                        historical_data_path=historical_data_path,
                        weatherbit_config_path=weatherbit_config_path,
                        use_weather=True
                    )
                    
                    self.state["last_inference_run"] = datetime.now().isoformat()
                    self.state["forecast_result_cache"] = {
                        "forecast_id": response.forecast_id,
                        "num_predictions": response.num_predictions,
                        "generated_at": response.generated_at.isoformat(),
                    }
                    
                    # Update cache
                    for include_conf in [True, False]:
                        cache_key = f"forecast_latest_240_{include_conf}"
                        forecast_service.cache[cache_key] = {
                            "response": response,
                            "generated_at": datetime.now(),
                        }
                    
                    logger.info(f"  ✅ Inference done: {response.num_predictions} predictions cached")
                else:
                    logger.warning(f"  ⚠️ Historical data not found at {historical_data_path}")
            else:
                logger.warning("  ⚠️ Model not loaded, skipping inference")
            
            self.state["last_error"] = None
            
        except Exception as e:
            self.state["last_error"] = f"{type(e).__name__}: {str(e)}"
            logger.error(f"  ❌ Hourly scheduler error: {e}", exc_info=True)
    
    async def trigger_manual(
        self,
        model_service,
        weather_service,
        forecast_service,
        historical_data_path: str,
        weatherbit_config_path: str
    ) -> Dict[str, Any]:
        """Manually trigger a scheduler cycle"""
        await self._run_hourly_job(
            model_service,
            weather_service,
            forecast_service,
            historical_data_path,
            weatherbit_config_path
        )
        
        return {
            "status": "completed",
            "last_run": self.state["last_run"],
            "run_count": self.state["run_count"],
            "last_error": self.state["last_error"],
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.state["running"],
            "interval_seconds": self.state["interval_seconds"],
            "last_run": self.state["last_run"],
            "next_run": self.state["next_run"],
            "run_count": self.state["run_count"],
            "last_error": self.state["last_error"],
            "last_weather_fetch": self.state["last_weather_fetch"],
            "last_inference_run": self.state["last_inference_run"],
            "forecast_result_cache": self.state["forecast_result_cache"],
        }


# Global scheduler service instance
scheduler_service = SchedulerService()

