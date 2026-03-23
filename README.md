# HydroPredict Backend

FastAPI backend service for the HydroPredict water level forecasting system.

## Overview

This backend serves the Temporal Fusion Transformer (TFT) model for water level and density predictions. It provides a REST API designed for integration with the HydroPredict Dashboard web application.

## Features

- **Real-time forecasts:** 240-hour (10-day) water level and density predictions
- **Confidence intervals:** Probabilistic forecasting with uncertainty quantification
- **Canal configuration:** Custom scenario analysis with canal/pump activation settings
- **Weather integration:** Automatic Weatherbit API integration for meteorological data
- **Hourly scheduler:** Automatic forecast refresh with latest weather data
- **Caching:** In-memory caching with configurable TTL

## Project Structure

```
HydroPredict-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── forecast.py  # Forecast endpoints
│   │       ├── weather.py   # Weather endpoints
│   │       ├── admin.py     # Admin endpoints
│   │       └── health.py    # Health check
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Settings & configuration
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py        # Common schemas
│   │   ├── forecast.py      # Forecast schemas
│   │   ├── weather.py       # Weather schemas
│   │   └── admin.py         # Admin schemas
│   └── services/
│       ├── __init__.py
│       ├── model_service.py     # Model inference
│       ├── weather_service.py   # Weather API
│       ├── forecast_service.py  # Forecast generation
│       └── scheduler_service.py # Hourly scheduler
├── data/
│   ├── input/
│   └── output/
├── requirements.txt
├── run.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### General
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /model/info` - Model information

### Forecast (v1)
- `GET /api/v1/forecast/latest` - Get latest forecast
- `POST /api/v1/forecast/custom` - Generate custom forecast with canal config
- `GET /api/v1/forecast/history` - Get forecast history
- `POST /api/v1/forecast/refresh` - Manual forecast refresh

### Weather (v1)
- `GET /api/v1/weather/forecast` - Get weather forecast

### Admin (v1)
- `GET /api/v1/admin/settings` - Get system settings
- `PUT /api/v1/admin/settings` - Update settings
- `GET /api/v1/admin/scheduler/status` - Scheduler status
- `POST /api/v1/admin/scheduler/trigger` - Manual scheduler trigger

## Quick Start

### Prerequisites

- Python 3.10+
- Access to HydroPredict-model files
- (Optional) Weatherbit API key

### Installation

1. Create and activate virtual environment:
```bash
cd HydroPredict-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build and run
docker-compose up --build

# Or build only
docker build -t hydropredict-backend .
docker run -p 8000:8000 hydropredict-backend
```

## Configuration

Configuration is managed via environment variables. See `.env.example` for all options.

Key settings:
- `MODEL_CHECKPOINT_PATH` - Path to model checkpoint
- `MODEL_CONFIG_PATH` - Path to model configuration
- `HISTORICAL_DATA_PATH` - Path to historical data CSV
- `WEATHERBIT_CONFIG_PATH` - Path to Weatherbit config
- `WEATHERBIT_API_KEY` - Weatherbit API key

## Dashboard Integration

This backend is designed to work with the HydroPredict Dashboard. Update the dashboard's API configuration:

```javascript
// In dashboard src/config/api.js
export const API_BASE_URL = 'http://localhost:8000';
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running in Development Mode

```bash
DEBUG=true python run.py
```

This enables:
- Auto-reload on file changes
- Detailed error messages
- Debug logging

### Testing

```bash
pytest tests/
```

## Production Deployment

For production deployment, consider:

1. **Use proper secrets management** for API keys
2. **Enable Redis caching** for better performance
3. **Set up PostgreSQL** for forecast history persistence
4. **Configure proper CORS origins**
5. **Use HTTPS** with proper certificates
6. **Set up monitoring** with Prometheus/Grafana

## License

MIT License - See LICENSE file for details.

