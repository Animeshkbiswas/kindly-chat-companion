#!/usr/bin/env python3
"""
Development server runner for the FastAPI therapy chat application
Use this for local development and testing
"""

import uvicorn
from core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level="info" if settings.environment == "development" else "warning",
        access_log=settings.environment == "development"
    )