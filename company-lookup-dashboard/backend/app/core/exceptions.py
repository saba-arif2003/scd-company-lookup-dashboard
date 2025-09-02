from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union, Dict, Any, List
import logging
from datetime import datetime

from app.models.common import APIResponse, ErrorDetail, ErrorType, APIStatus

logger = logging.getLogger(__name__)


class CompanyLookupException(Exception):
    """Base exception for company lookup operations"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.INTERNAL_SERVER_ERROR,
        code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_type = error_type
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class CompanyNotFoundError(CompanyLookupException):
    """Exception raised when a company is not found"""
    
    def __init__(self, message: str, query: str = None):
        super().__init__(
            message=message,
            error_type=ErrorType.NOT_FOUND,
            code="COMPANY_NOT_FOUND",
            details={"query": query} if query else None
        )


class StockNotFoundError(CompanyLookupException):
    """Exception raised when stock data is not found"""
    
    def __init__(self, message: str, symbol: str = None):
        super().__init__(
            message=message,
            error_type=ErrorType.NOT_FOUND,
            code="STOCK_NOT_FOUND", 
            details={"symbol": symbol} if symbol else None
        )


class SECAPIError(CompanyLookupException):
    """Exception raised when SEC EDGAR API fails"""
    
    def __init__(self, message: str, cik: str = None, status_code: int = None):
        super().__init__(
            message=message,
            error_type=ErrorType.EXTERNAL_API_ERROR,
            code="SEC_API_ERROR",
            details={
                "cik": cik,
                "status_code": status_code
            } if cik or status_code else None
        )


class ExternalAPIError(CompanyLookupException):
    """Exception raised when external API calls fail"""
    
    def __init__(self, message: str, service: str = None, status_code: int = None):
        super().__init__(
            message=message,
            error_type=ErrorType.EXTERNAL_API_ERROR,
            code="EXTERNAL_API_ERROR",
            details={
                "service": service,
                "status_code": status_code
            } if service or status_code else None
        )


class RateLimitExceededError(CompanyLookupException):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(
            message=message,
            error_type=ErrorType.RATE_LIMIT_EXCEEDED,
            code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after} if retry_after else None
        )


class ValidationError(CompanyLookupException):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": value
            } if field or value else None
        )


def create_error_response(
    status: APIStatus,
    message: str,
    errors: List[ErrorDetail] = None,
    request_id: str = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    return APIResponse(
        status=status,
        message=message,
        data=None,
        errors=errors or [],
        metadata={
            "error_occurred": True,
            "timestamp": datetime.utcnow().isoformat()
        },
        request_id=request_id
    ).dict()


async def company_lookup_exception_handler(
    request: Request, 
    exc: CompanyLookupException
) -> JSONResponse:
    """Handle custom company lookup exceptions"""
    
    # Log the error
    logger.error(
        f"CompanyLookupException: {exc.message}",
        extra={
            "error_type": exc.error_type.value,
            "error_code": exc.code,
            "details": exc.details,
            "path": str(request.url)
        }
    )
    
    # Map exception types to HTTP status codes
    status_code_mapping = {
        ErrorType.NOT_FOUND: 404,
        ErrorType.VALIDATION_ERROR: 400,
        ErrorType.RATE_LIMIT_EXCEEDED: 429,
        ErrorType.EXTERNAL_API_ERROR: 502,
        ErrorType.TIMEOUT_ERROR: 504,
        ErrorType.AUTHENTICATION_ERROR: 401,
        ErrorType.AUTHORIZATION_ERROR: 403,
        ErrorType.INTERNAL_SERVER_ERROR: 500
    }
    
    status_code = status_code_mapping.get(exc.error_type, 500)
    
    # Create error detail
    error_detail = ErrorDetail(
        type=exc.error_type,
        message=exc.message,
        code=exc.code,
        details=exc.details
    )
    
    # Determine API status
    if exc.error_type == ErrorType.NOT_FOUND:
        api_status = APIStatus.ERROR
    elif exc.error_type in [ErrorType.EXTERNAL_API_ERROR, ErrorType.TIMEOUT_ERROR]:
        api_status = APIStatus.PARTIAL
    else:
        api_status = APIStatus.ERROR
    
    response_data = create_error_response(
        status=api_status,
        message=exc.message,
        errors=[error_detail],
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors"""
    
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "path": str(request.url),
            "errors": exc.errors()
        }
    )
    
    # Convert validation errors to our format
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else "body"
        
        error_detail = ErrorDetail(
            type=ErrorType.VALIDATION_ERROR,
            message=error["msg"],
            code="VALIDATION_ERROR",
            field=field,
            details={
                "input_value": error.get("input"),
                "error_type": error["type"]
            }
        )
        error_details.append(error_detail)
    
    response_data = create_error_response(
        status=APIStatus.ERROR,
        message="Validation failed",
        errors=error_details,
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=422,
        content=response_data
    )


async def http_exception_handler(
    request: Request,
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """Handle HTTP exceptions"""
    
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )
    
    # Map HTTP status codes to error types
    error_type_mapping = {
        400: ErrorType.VALIDATION_ERROR,
        401: ErrorType.AUTHENTICATION_ERROR,
        403: ErrorType.AUTHORIZATION_ERROR,
        404: ErrorType.NOT_FOUND,
        429: ErrorType.RATE_LIMIT_EXCEEDED,
        500: ErrorType.INTERNAL_SERVER_ERROR,
        502: ErrorType.EXTERNAL_API_ERROR,
        504: ErrorType.TIMEOUT_ERROR
    }
    
    error_type = error_type_mapping.get(exc.status_code, ErrorType.INTERNAL_SERVER_ERROR)
    
    error_detail = ErrorDetail(
        type=error_type,
        message=str(exc.detail),
        code=f"HTTP_{exc.status_code}"
    )
    
    response_data = create_error_response(
        status=APIStatus.ERROR,
        message=str(exc.detail),
        errors=[error_detail],
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": str(request.url),
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    error_detail = ErrorDetail(
        type=ErrorType.INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        code="INTERNAL_SERVER_ERROR"
    )
    
    response_data = create_error_response(
        status=APIStatus.ERROR,
        message="Internal server error",
        errors=[error_detail],
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app"""
    
    # Custom exception handlers
    app.add_exception_handler(CompanyLookupException, company_lookup_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers configured")