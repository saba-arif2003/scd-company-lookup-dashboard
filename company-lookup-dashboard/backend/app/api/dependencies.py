from fastapi import Request, Depends, HTTPException
from typing import Optional
import uuid
import time
import logging

from app.core.security import security_service
from app.core.exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)


async def add_request_id(request: Request):
    """Add unique request ID to request state"""
    request_id = security_service.generate_request_id(request)
    request.state.request_id = request_id
    security_service.log_request(request, request_id)
    return request_id


async def check_rate_limit(request: Request):
    """Check rate limits for the request"""
    try:
        security_service.check_rate_limit(request)
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail=e.message,
            headers={"Retry-After": str(e.details.get("retry_after", 60))}
        )


async def validate_content_type(request: Request):
    """Validate content type for POST/PUT requests"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        
        # Allow JSON content type
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=415,
                detail="Unsupported Media Type. Expected application/json"
            )


async def add_security_headers(request: Request):
    """Add security headers to response"""
    # This would typically be done in middleware
    # but can be used as a dependency for specific routes
    pass


class CommonQueryParams:
    """Common query parameters for API endpoints"""
    
    def __init__(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        format: Optional[str] = "json"
    ):
        self.limit = limit
        self.offset = offset
        self.format = format
        
        # Validate parameters
        if self.limit is not None and self.limit < 0:
            raise HTTPException(status_code=400, detail="Limit cannot be negative")
        
        if self.offset is not None and self.offset < 0:
            raise HTTPException(status_code=400, detail="Offset cannot be negative")
        
        if self.format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")


def get_common_params(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    format: Optional[str] = "json"
) -> CommonQueryParams:
    """Dependency for common query parameters"""
    return CommonQueryParams(limit=limit, offset=offset, format=format)