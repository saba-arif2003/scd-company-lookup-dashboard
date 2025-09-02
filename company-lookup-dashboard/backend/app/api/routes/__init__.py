"""
API Routes package for Company Lookup Dashboard

This package contains all individual route modules organized by functionality.
"""

# Import all route modules
from . import health
from . import search  
from . import company

# Route module metadata
ROUTE_MODULES = {
    'health': {
        'module': health,
        'router': health.router,
        'prefix': '',
        'tags': ['Health'],
        'description': 'Health check and system status endpoints'
    },
    'search': {
        'module': search,
        'router': search.router, 
        'prefix': '',
        'tags': ['Search'],
        'description': 'Company search and suggestion endpoints'
    },
    'company': {
        'module': company,
        'router': company.router,
        'prefix': '',
        'tags': ['Company'],
        'description': 'Company information, stock data, and SEC filings endpoints'
    }
}

# Export all routers for easy import
__all__ = [
    "health",
    "search", 
    "company",
    "ROUTE_MODULES"
]