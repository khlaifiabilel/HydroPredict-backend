"""
Weather Service
Handles fetching weather forecasts from Weatherbit API
"""

import os
import sys
import logging
import math
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import pandas as pd

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather data fetching and caching"""
    
    def __init__(self):
        self.cache: Optional[Dict[str, Any]] = None
        self.cache_time: Optional[datetime] = None
        self.cache_ttl_seconds = 3600  # 1 hour
    
    def fetch_weather_forecast(
        self,
        config_path: str = "configs/weatherbit.json",
        hours: int = 240
    ) -> Optional[pd.DataFrame]:
        """
        Fetch live weather forecast from Weatherbit API
        
        Args:
            config_path: Path to weatherbit config JSON
            hours: Number of hours to forecast
            
        Returns:
            DataFrame with weather forecast data, or None on failure
        """
        try:
            # Add HydroPredict-model to path for imports
            model_project_root = Path(config_path).parent.parent
            if str(model_project_root) not in sys.path:
                sys.path.insert(0, str(model_project_root))
            
            from data.weather_forecast_hourly import load_weatherbit_config, get_hourly_forecast
            
            config = load_weatherbit_config(config_path)
            if not config:
                logger.warning(f"Failed to load weatherbit config from {config_path}")
                return None
            
            api_key = config.get('api_key') or os.environ.get('WEATHERBIT_API_KEY')
            if not api_key:
                logger.warning("No Weatherbit API key found")
                return None
            
            city = config.get('location', {}).get('city')
            lat = config.get('location', {}).get('lat')
            lon = config.get('location', {}).get('lon')
            
            logger.info(f"Fetching weather forecast for {city} (lat={lat}, lon={lon}), {hours}h")
            
            forecast_data = get_hourly_forecast(
                api_key=api_key, city=city, lat=lat, lon=lon, hours=hours
            )
            
            if not forecast_data:
                logger.warning("Failed to fetch weather forecast from Weatherbit API")
                return None
            
            # Store raw response in cache
            self.cache = {
                "data": forecast_data,
                "fetched_at": datetime.now().isoformat(),
                "city": city,
                "lat": lat,
                "lon": lon,
            }
            self.cache_time = datetime.now()
            
            # Convert to DataFrame
            rows = []
            for hour in forecast_data['data']:
                forecast_dt = datetime.strptime(hour['timestamp_utc'], '%Y-%m-%dT%H:%M:%S')
                rows.append({
                    'measurement_date': forecast_dt,
                    'hour_of_day': forecast_dt.hour,
                    'air_temperature_celsius': float(hour['temp']),
                    'humidity_percent': float(hour['rh']),
                    'precipitation_mm': float(hour['precip']),
                    'wind_speed_ms': float(hour['wind_spd']),
                    'wind_direction_degrees': int(hour['wind_dir']),
                    'cloud_coverage_percent': float(hour['clouds']),
                    'weather_description_text': hour['weather']['description'],
                    'atmospheric_pressure_hpa': float(hour['pres']),
                })
            
            weather_df = pd.DataFrame(rows)
            weather_df['measurement_date'] = pd.to_datetime(weather_df['measurement_date'])
            
            logger.info(f"Fetched {len(weather_df)} hourly weather forecasts")
            return weather_df
            
        except Exception as e:
            logger.warning(f"Weather forecast fetch failed: {e}")
            return None
    
    def get_cached_weather(self) -> Optional[Dict[str, Any]]:
        """Get cached weather data if still valid"""
        if self.cache and self.cache_time:
            age = (datetime.now() - self.cache_time).total_seconds()
            if age < self.cache_ttl_seconds:
                return self.cache
        return None
    
    def get_weather_api_response(
        self,
        hours: int = 240,
        config_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast in API response format
        Uses cache if available, otherwise fetches live data
        Falls back to demo data if API unavailable
        """
        # Check cache first
        cached = self.get_cached_weather()
        if cached:
            return self._format_cached_response(cached, hours)
        
        # Try to fetch live data
        if config_path:
            try:
                # Add HydroPredict-model to path
                model_project_root = Path(config_path).parent.parent
                if str(model_project_root) not in sys.path:
                    sys.path.insert(0, str(model_project_root))
                
                from data.weather_forecast_hourly import load_weatherbit_config, get_hourly_forecast
                
                config = load_weatherbit_config(config_path)
                if config:
                    api_key = config.get('api_key') or os.environ.get('WEATHERBIT_API_KEY')
                    if api_key:
                        city = config.get('location', {}).get('city')
                        lat = config.get('location', {}).get('lat')
                        lon = config.get('location', {}).get('lon')
                        
                        forecast_data = get_hourly_forecast(
                            api_key=api_key, city=city, lat=lat, lon=lon, hours=min(hours, 240)
                        )
                        
                        if forecast_data:
                            self.cache = {
                                "data": forecast_data,
                                "fetched_at": datetime.now().isoformat(),
                                "city": city,
                                "lat": lat,
                                "lon": lon,
                            }
                            self.cache_time = datetime.now()
                            return self._format_api_response(forecast_data, hours)
            except Exception as e:
                logger.warning(f"Weather API error: {e}")
        
        # Fallback to demo data
        return self.generate_demo_weather(min(hours, 240))
    
    def _format_cached_response(self, cached: Dict, hours: int) -> Dict[str, Any]:
        """Format cached data as API response"""
        forecast_data = cached["data"]
        data_points = []
        
        for hour_data in forecast_data.get('data', [])[:hours]:
            data_points.append(self._format_hour_data(hour_data))
        
        return {
            'city': forecast_data.get('city_name', cached.get('city', '')),
            'country': forecast_data.get('country_code', ''),
            'lat': forecast_data.get('lat', cached.get('lat')),
            'lon': forecast_data.get('lon', cached.get('lon')),
            'timezone': forecast_data.get('timezone', ''),
            'num_hours': len(data_points),
            'data': data_points,
            'cached': True,
            'cached_at': cached["fetched_at"],
        }
    
    def _format_api_response(self, forecast_data: Dict, hours: int) -> Dict[str, Any]:
        """Format API response"""
        data_points = []
        for hour in forecast_data.get('data', [])[:hours]:
            data_points.append(self._format_hour_data(hour))
        
        return {
            'city': forecast_data.get('city_name', ''),
            'country': forecast_data.get('country_code', ''),
            'lat': forecast_data.get('lat'),
            'lon': forecast_data.get('lon'),
            'timezone': forecast_data.get('timezone', ''),
            'num_hours': len(data_points),
            'data': data_points,
        }
    
    def _format_hour_data(self, hour: Dict) -> Dict[str, Any]:
        """Format a single hour of weather data"""
        return {
            'timestamp': hour.get('timestamp_utc', ''),
            'temp': hour.get('temp'),
            'app_temp': hour.get('app_temp'),
            'humidity': hour.get('rh'),
            'precipitation': hour.get('precip', 0),
            'wind_speed': hour.get('wind_spd'),
            'wind_gust': hour.get('wind_gust_spd'),
            'wind_direction': hour.get('wind_dir'),
            'wind_cdir': hour.get('wind_cdir', ''),
            'pressure': hour.get('pres'),
            'sea_level_pressure': hour.get('slp'),
            'clouds': hour.get('clouds'),
            'cloud_low': hour.get('clouds_low', 0),
            'cloud_mid': hour.get('clouds_mid', 0),
            'cloud_high': hour.get('clouds_hi', 0),
            'visibility': hour.get('vis', 0),
            'dew_point': hour.get('dewpt'),
            'uv_index': hour.get('uv', 0),
            'solar_radiation': hour.get('solar_rad', 0),
            'ghi': hour.get('ghi', 0),
            'dni': hour.get('dni', 0),
            'dhi': hour.get('dhi', 0),
            'snow': hour.get('snow', 0),
            'snow_depth': hour.get('snow_depth', 0),
            'ozone': hour.get('ozone', 0),
            'weather_icon': hour.get('weather', {}).get('icon', ''),
            'weather_code': hour.get('weather', {}).get('code', 0),
            'weather_description': hour.get('weather', {}).get('description', ''),
            'pod': hour.get('pod', ''),
        }
    
    def generate_demo_weather(self, hours: int) -> Dict[str, Any]:
        """Generate realistic demo weather data for Zarzis, Tunisia"""
        random.seed(42)
        data_points = []
        base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        
        for h in range(hours):
            t = base_time + timedelta(hours=h)
            hour_of_day = t.hour
            day_frac = h / 24.0
            
            # Diurnal temperature cycle (Zarzis: ~15-28°C range)
            if 6 <= hour_of_day <= 18:
                temp_base = 21.5 + 6.5 * math.sin(math.pi * (hour_of_day - 6) / 12)
            else:
                temp_base = 16.0 + 2.0 * math.sin(math.pi * hour_of_day / 24)
            
            temp = temp_base + random.gauss(0, 1.2) + 1.5 * math.sin(2 * math.pi * day_frac / 7)
            humidity = max(20, min(95, 55 + 20 * math.cos(math.pi * (hour_of_day - 14) / 12) + random.gauss(0, 5)))
            wind = max(0, 4.5 + 2.5 * math.sin(2 * math.pi * hour_of_day / 24) + random.gauss(0, 1.5))
            gust = wind * (1.3 + random.random() * 0.4)
            
            is_day = 6 <= hour_of_day <= 18
            solar_factor = max(0, math.sin(math.pi * (hour_of_day - 6) / 12)) if is_day else 0
            clouds = max(0, min(100, 30 + 25 * math.sin(2 * math.pi * day_frac / 3) + random.gauss(0, 15)))
            cloud_factor = 1 - clouds / 100
            precip = max(0, random.gauss(-0.3, 0.4)) if clouds > 60 else 0
            
            wind_dir = int((180 + 45 * math.sin(2 * math.pi * h / 48) + random.gauss(0, 20)) % 360)
            
            weather_desc = ['Clear sky', 'Few clouds', 'Scattered clouds', 'Broken clouds'][int(clouds / 25) % 4]
            if precip > 0:
                weather_desc = 'Light rain'
            
            data_points.append({
                'timestamp': t.strftime('%Y-%m-%dT%H:%M:%S'),
                'temp': round(temp, 1),
                'app_temp': round(temp - 1.2 + 0.5 * wind / 10, 1),
                'humidity': round(humidity, 0),
                'precipitation': round(max(0, precip), 2),
                'wind_speed': round(wind, 1),
                'wind_gust': round(gust, 1),
                'wind_direction': wind_dir,
                'wind_cdir': directions[int(wind_dir / 22.5) % 16],
                'pressure': round(1013 + 3 * math.sin(2 * math.pi * h / 72) + random.gauss(0, 0.8), 1),
                'sea_level_pressure': round(1015 + 3 * math.sin(2 * math.pi * h / 72) + random.gauss(0, 0.8), 1),
                'clouds': round(clouds, 0),
                'cloud_low': round(max(0, clouds * 0.4 + random.gauss(0, 8)), 0),
                'cloud_mid': round(max(0, clouds * 0.3 + random.gauss(0, 8)), 0),
                'cloud_high': round(max(0, clouds * 0.2 + random.gauss(0, 5)), 0),
                'visibility': round(max(2, 10 - precip * 3 + random.gauss(0, 1)), 1),
                'dew_point': round(temp - (100 - humidity) / 5, 1),
                'uv_index': round(max(0, 10 * solar_factor * cloud_factor + random.gauss(0, 0.3)), 1),
                'solar_radiation': round(max(0, 900 * solar_factor * cloud_factor + random.gauss(0, 20)), 0),
                'ghi': round(max(0, 800 * solar_factor * cloud_factor + random.gauss(0, 15)), 0),
                'dni': round(max(0, 600 * solar_factor * cloud_factor * 0.85 + random.gauss(0, 15)), 0),
                'dhi': round(max(0, 200 * solar_factor * (0.3 + 0.7 * (1 - cloud_factor)) + random.gauss(0, 10)), 0),
                'snow': 0,
                'snow_depth': 0,
                'ozone': round(280 + random.gauss(0, 10), 0),
                'weather_icon': 'c02d' if is_day else 'c02n',
                'weather_code': 802,
                'weather_description': weather_desc,
                'pod': 'd' if is_day else 'n',
            })
        
        return {
            'city': 'Zarzis',
            'country': 'TN',
            'lat': 33.41,
            'lon': 11.04,
            'timezone': 'Africa/Tunis',
            'num_hours': len(data_points),
            'data': data_points,
            'demo': True,
        }


# Global weather service instance
weather_service = WeatherService()

