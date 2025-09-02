"""
API package for Company Lookup Dashboard

This package contains all API route definitions and related functionality.
"""

from .routes import health, search, company

# API version and metadata
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Import routers for easy access
health_router = health.router
search_router = search.router  
company_router = company.router

# List of all available routers
__all__ = [
    "health_router",
    "search_router", 
    "company_router",
    "API_VERSION",
    "API_PREFIX"
]