"""
Company Lookup & SEC Filings Dashboard API

A FastAPI application for retrieving company information, stock prices, and SEC filings.
"""

__version__ = "1.0.0"
__author__ = "Company Lookup Dashboard Team"
__email__ = "support@company-lookup-dashboard.com"
__description__ = "Professional API for company intelligence and SEC filings data"

# Application metadata
APP_NAME = "Company Lookup Dashboard API"
APP_VERSION = __version__
APP_DESCRIPTION = __description__

# API versioning
API_V1_PREFIX = "/api/v1"

# Feature flags
FEATURES = {
    "ENABLE_RATE_LIMITING": True,
    "ENABLE_CACHING": True,
    "ENABLE_MONITORING": True,
    "ENABLE_CORS": True,
}

# Import main components for easy access
from .main import app
from .config import settings

__all__ = [
    "app",
    "settings", 
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "API_V1_PREFIX"
]