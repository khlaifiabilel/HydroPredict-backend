#!/usr/bin/env python
"""
Run the HydroPredict Backend API server
"""

import uvicorn
from app.core.config import settings


def main():
    """Run the API server"""
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()

