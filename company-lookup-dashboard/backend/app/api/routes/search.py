from fastapi import APIRouter, Query, Request, Depends, HTTPException
from typing import Optional
import time
import logging
from datetime import datetime

from app.models.company import CompanySearchResponse
from app.models.common import APIResponse, APIStatus
from app.services.company_service import CompanyService
from app.core.security import security_service
from app.core.exceptions import CompanyNotFoundError, ValidationError
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_company_service() -> CompanyService:
    """Dependency to get company service instance"""
    service = CompanyService()
    try:
        yield service
    finally:
        await service.close()


@router.get("/search", response_model=APIResponse)
async def search_companies(
    request: Request,
    q: str = Query(
        ..., 
        description="Search query (company name or ticker)", 
        min_length=1,
        max_length=100,
        example="microsoft"
    ),
    limit: Optional[int] = Query(
        None,
        description="Maximum number of results to return",
        ge=1,
        le=settings.MAX_SEARCH_RESULTS,
        example=10
    ),
    company_service: CompanyService = Depends(get_company_service)
):
    """
    Search for companies by name or ticker symbol
    """
    start_time = time.time()
    
    # Generate request ID for tracking
    request_id = f"search_{int(time.time() * 1000)}"
    
    try:
        logger.info(f"Search request for: '{q}'", extra={"request_id": request_id})
        
        # Basic validation
        if not q or len(q.strip()) < 1:
            return APIResponse(
                status=APIStatus.ERROR,
                message="Search query is required",
                data=None,
                request_id=request_id
            )
        
        query = q.strip()
        search_limit = limit or settings.MAX_SEARCH_RESULTS
        
        # Perform the search
        search_results = await company_service.search_companies(query)
        
        # Apply limit if results exceed requested amount
        if search_limit < len(search_results.results):
            search_results.results = search_results.results[:search_limit]
            search_results.total_results = len(search_results.results)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Determine response status
        if search_results.results:
            status = APIStatus.SUCCESS
            message = f"Found {len(search_results.results)} matching companies"
        else:
            status = APIStatus.SUCCESS  # Empty results are still successful
            message = "No companies found matching your search"
        
        logger.info(f"Search completed: {len(search_results.results)} results in {response_time}ms",
                   extra={"request_id": request_id, "query": query})
        
        return APIResponse(
            status=status,
            message=message,
            data=search_results.dict(),
            metadata={
                "response_time_ms": response_time,
                "search_algorithm": "enhanced_fuzzy_match",
                "data_sources": ["yahoo_finance", "sec_edgar"]
            },
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", 
                    extra={"request_id": request_id, "query": q}, exc_info=True)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return APIResponse(
            status=APIStatus.ERROR,
            message=f"Search failed: {str(e)}",
            data=CompanySearchResponse(
                query=q,
                results=[],
                total_results=0,
                took_ms=int(response_time),
                suggestions=[f"Try searching for '{q.upper()}' ticker", "Check spelling and try again"]
            ).dict(),
            metadata={
                "response_time_ms": response_time,
                "error": True
            },
            request_id=request_id
        )


@router.get("/search/suggestions")
async def get_search_suggestions(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: Optional[int] = Query(5, description="Max suggestions", ge=1, le=10),
    company_service: CompanyService = Depends(get_company_service)
):
    """Get search suggestions for autocomplete"""
    try:
        search_result = await company_service.search_companies(q)
        
        suggestions = []
        for result in search_result.results[:limit]:
            suggestions.append({
                "text": result.name,
                "ticker": result.ticker,
                "type": "company"
            })
        
        return {
            "status": "success",
            "data": {"suggestions": suggestions}
        }
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        return {
            "status": "error", 
            "data": {"suggestions": []}
        }


@router.get("/search/validate")
async def validate_search_query(
    request: Request,
    q: str = Query(..., description="Query to validate", example="MSFT")
):
    """
    Validate a search query
    """
    request_id = f"validate_{int(time.time() * 1000)}"
    
    try:
        validation_results = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "query_type": "unknown"
        }
        
        # Check query length
        if not q or len(q.strip()) < 1:
            validation_results["is_valid"] = False
            validation_results["issues"].append("Query cannot be empty")
        
        if len(q) > 100:
            validation_results["is_valid"] = False
            validation_results["issues"].append("Query too long (maximum 100 characters)")
        
        # Determine query type
        query_stripped = q.strip().upper()
        
        # Check if it looks like a ticker
        if query_stripped.isalpha() and len(query_stripped) <= 5:
            validation_results["query_type"] = "ticker"
        # Check if it looks like a CIK
        elif query_stripped.isdigit():
            validation_results["query_type"] = "cik"
        # Otherwise assume company name
        else:
            validation_results["query_type"] = "company_name"
        
        # Provide suggestions for improvement
        if not validation_results["is_valid"]:
            if validation_results["query_type"] == "ticker":
                validation_results["suggestions"].append(
                    "Use 1-5 uppercase letters for ticker symbols (e.g., MSFT, AAPL)"
                )
            elif validation_results["query_type"] == "company_name":
                validation_results["suggestions"].append(
                    "Try using the company's common name or stock ticker"
                )
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message="Query validation completed",
            data=validation_results,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", 
                    extra={"request_id": request_id, "query": q}, exc_info=True)
        
        return APIResponse(
            status=APIStatus.ERROR,
            message=f"Validation failed: {str(e)}",
            data={
                "is_valid": False,
                "issues": ["Validation service error"],
                "suggestions": []
            },
            request_id=request_id
        )


# Debug endpoint for testing
@router.get("/debug/test")
async def debug_test():
    """Debug endpoint to test backend connectivity"""
    return {
        "status": "working",
        "message": "Backend search API is running correctly", 
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            "/api/v1/search?q=microsoft",
            "/api/v1/search/suggestions?q=mic",
            "/api/v1/company/lookup?q=apple"
        ]
    }


# ADDED: Health endpoint to fix 404 errors
@router.get("/health/simple")
async def health_simple():
    """Simple health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "search_api"
    }


# ADDED: Test SEC API endpoint
@router.get("/test-sec")
async def test_sec_api():
    """Test SEC API directly"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = "https://www.sec.gov/files/company_tickers.json"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Find Microsoft specifically
                    microsoft_found = []
                    for key, company in data.items():
                        if isinstance(company, dict):
                            name = company.get('title', '').lower()
                            ticker = company.get('ticker', '').upper()
                            if 'microsoft' in name or ticker == 'MSFT':
                                microsoft_found.append(company)
                    
                    return {
                        "status": "success",
                        "total_companies": len(data),
                        "microsoft_found": microsoft_found,
                        "sample_company": list(data.values())[0] if data else None
                    }
                else:
                    return {"status": "error", "message": f"SEC API returned {response.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}