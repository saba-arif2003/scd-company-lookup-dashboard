""" Pydantic models for the Company Lookup Dashboard API """

# Import in a specific order to avoid circular dependencies
# Import common first as it has no dependencies
from .common import (
    APIResponse, 
    ErrorDetail, 
    HealthCheck, 
    APIStatus, 
    ErrorType,
    PaginationInfo,  # Added this - it was missing
    SearchMetadata   # Added this - it was missing
)

# Import individual models
from .stock import StockQuote, StockData, StockHistoricalData
from .filing import Filing, FilingResponse, FilingSearchCriteria, FilingFormType
from .company import (
    Company, 
    CompanySearchResult, 
    CompanyLookupResponse, 
    CompanySearchResponse
)

__all__ = [
    # Common models
    "APIResponse",
    "ErrorDetail", 
    "HealthCheck",
    "APIStatus",
    "ErrorType",
    "PaginationInfo",
    "SearchMetadata",
    
    # Stock models
    "StockQuote",
    "StockData",
    "StockHistoricalData",
    
    # Filing models
    "Filing",
    "FilingResponse", 
    "FilingSearchCriteria",
    "FilingFormType",
    
    # Company models
    "Company",
    "CompanySearchResult",
    "CompanyLookupResponse",
    "CompanySearchResponse"
]