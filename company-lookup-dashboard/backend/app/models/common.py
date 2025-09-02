from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum


class APIStatus(str, Enum):
    """API status enumeration"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


class ErrorType(str, Enum):
    """Error type enumeration"""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    EXTERNAL_API_ERROR = "external_api_error"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"


class ErrorDetail(BaseModel):
    """Detailed error information model"""
    type: ErrorType = Field(..., description="Error type classification")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Error code for programmatic handling")
    field: Optional[str] = Field(None, description="Field name if validation error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "validation_error",
                "message": "Invalid ticker symbol format",
                "code": "INVALID_TICKER",
                "field": "ticker",
                "details": {
                    "provided": "tesla",
                    "expected_format": "1-5 uppercase letters"
                }
            }
        }


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    status: APIStatus = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Union[Dict[str, Any], List[Any]]] = Field(None, description="Response data")
    errors: Optional[List[ErrorDetail]] = Field(None, description="List of errors if any")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Data retrieved successfully",
                "data": {"company": "Tesla Inc.", "ticker": "TSLA"},
                "errors": None,
                "metadata": {"source": "SEC EDGAR", "cache_hit": True},
                "timestamp": "2024-08-27T10:30:00Z",
                "request_id": "req_abc123xyz"
            }
        }


class HealthCheck(BaseModel):
    """Health check model"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field("1.0.0", description="API version")
    uptime_seconds: Optional[float] = Field(None, description="Server uptime in seconds")
    
    # Service dependencies health
    dependencies: Dict[str, str] = Field(
        default_factory=lambda: {
            "sec_edgar_api": "unknown",
            "yahoo_finance": "unknown"
        },
        description="External service dependencies status"
    )
    
    # System metrics
    system_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="System performance metrics"
    )
    
    # Environment info
    environment: str = Field("production", description="Deployment environment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-08-27T10:30:00Z",
                "version": "1.0.0",
                "uptime_seconds": 86400.5,
                "dependencies": {
                    "sec_edgar_api": "healthy",
                    "yahoo_finance": "healthy"
                },
                "system_metrics": {
                    "memory_usage_mb": 256.7,
                    "cpu_usage_percent": 15.3,
                    "active_connections": 42
                },
                "environment": "production"
            }
        }


class PaginationInfo(BaseModel):
    """Pagination information model"""
    page: int = Field(1, description="Current page number", ge=1)
    page_size: int = Field(10, description="Number of items per page", ge=1, le=100)
    total_items: int = Field(0, description="Total number of items", ge=0)
    total_pages: int = Field(0, description="Total number of pages", ge=0)
    has_next: bool = Field(False, description="Whether there are more pages")
    has_previous: bool = Field(False, description="Whether there are previous pages")
    
    @model_validator(mode='after')
    def calculate_derived_fields(self):
        """Calculate pagination derived fields"""
        if self.total_items > 0:
            self.total_pages = (self.total_items - 1) // self.page_size + 1
            self.has_next = self.page < self.total_pages
            self.has_previous = self.page > 1
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 2,
                "page_size": 10,
                "total_items": 45,
                "total_pages": 5,
                "has_next": True,
                "has_previous": True
            }
        }


class SearchMetadata(BaseModel):
    """Search operation metadata"""
    query: str = Field(..., description="Original search query")
    total_results: int = Field(0, description="Total number of results found")
    took_ms: int = Field(..., description="Search time in milliseconds")
    cached: bool = Field(False, description="Whether results came from cache")
    suggestions: Optional[List[str]] = Field(None, description="Alternative search suggestions")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters that were applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "tesla motors",
                "total_results": 3,
                "took_ms": 245,
                "cached": False,
                "suggestions": ["Tesla Inc", "Tesla Motors Inc"],
                "filters_applied": {"min_match_score": 0.5}
            }
        }