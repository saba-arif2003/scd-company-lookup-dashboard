from fastapi import APIRouter, Query, Path, Request, Depends, HTTPException
from typing import Optional, List
import time
import logging

from app.models.company import CompanyLookupResponse, Company
from app.models.stock import StockQuote, StockData
from app.models.filing import FilingResponse, FilingSearchCriteria
from app.models.common import APIResponse, APIStatus
from app.services.company_service import CompanyService
from app.services.stock_service import StockService
from app.services.sec_service import SECService
from app.core.security import security_service
from app.core.exceptions import CompanyNotFoundError, ValidationError, StockNotFoundError
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


async def get_stock_service() -> StockService:
    """Dependency to get stock service instance"""
    service = StockService()
    try:
        yield service
    finally:
        await service.close()


async def get_sec_service() -> SECService:
    """Dependency to get SEC service instance"""
    service = SECService()
    try:
        yield service
    finally:
        await service.close()


@router.get("/company/lookup", response_model=APIResponse)
async def lookup_company(
    request: Request,
    q: str = Query(
        ..., 
        description="Company name or ticker to lookup", 
        example="tesla",
        min_length=settings.MIN_SEARCH_QUERY_LENGTH
    ),
    include_stock: Optional[bool] = Query(
        True,
        description="Include current stock quote in response"
    ),
    include_filings: Optional[bool] = Query(
        True,
        description="Include recent SEC filings in response"
    ),
    filings_limit: Optional[int] = Query(
        5,
        description="Number of recent filings to include",
        ge=1,
        le=20
    ),
    company_service: CompanyService = Depends(get_company_service)
):
    """
    Get complete company information
    
    This endpoint provides comprehensive company information including:
    - Basic company details (name, ticker, CIK)
    - Current stock quote (if available and requested)
    - Recent SEC filings (if requested)
    
    **Parameters:**
    - **q**: Company name or ticker symbol
    - **include_stock**: Whether to include stock quote (default: true)
    - **include_filings**: Whether to include SEC filings (default: true)  
    - **filings_limit**: Number of filings to include (default: 5, max: 20)
    
    **Returns:**
    - Complete company information with stock and filing data
    - Data source attribution
    - Last updated timestamps
    """
    start_time = time.time()
    request_id = security_service.generate_request_id(request)
    
    try:
        # Rate limiting
        security_service.check_rate_limit(request)
        
        # Input validation
        query = security_service.validate_search_query(q)
        
        logger.info(f"Company lookup request: query='{query}'", 
                   extra={"request_id": request_id})
        
        # Perform the lookup
        lookup_result = await company_service.get_company_lookup(query)
        
        # Filter response based on parameters
        if not include_stock:
            lookup_result.stock_quote = None
        
        if not include_filings:
            lookup_result.recent_filings = []
        elif filings_limit and lookup_result.recent_filings:
            lookup_result.recent_filings = lookup_result.recent_filings[:filings_limit]
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Determine data completeness for status
        has_stock = lookup_result.stock_quote is not None
        has_filings = bool(lookup_result.recent_filings)
        
        if has_stock and has_filings:
            status = APIStatus.SUCCESS
            message = f"Complete company information retrieved for {lookup_result.company.name}"
        elif has_stock or has_filings:
            status = APIStatus.PARTIAL
            message = f"Partial company information retrieved for {lookup_result.company.name}"
        else:
            status = APIStatus.SUCCESS  # Company info alone is still success
            message = f"Basic company information retrieved for {lookup_result.company.name}"
        
        logger.info(f"Lookup completed for {lookup_result.company.ticker} in {response_time}ms",
                   extra={"request_id": request_id})
        
        return APIResponse(
            status=status,
            message=message,
            data=lookup_result.dict(),
            metadata={
                "response_time_ms": response_time,
                "data_completeness": {
                    "company_info": True,
                    "stock_quote": has_stock,
                    "filings": has_filings
                }
            },
            request_id=request_id
        )
        
    except CompanyNotFoundError as e:
        logger.warning(f"Company not found: {e.message}",
                      extra={"request_id": request_id, "query": q})
        raise HTTPException(status_code=404, detail=e.message)
        
    except ValidationError as e:
        logger.warning(f"Lookup validation error: {e.message}",
                      extra={"request_id": request_id, "query": q})
        raise HTTPException(status_code=400, detail=e.message)
        
    except Exception as e:
        logger.error(f"Lookup error: {str(e)}", 
                    extra={"request_id": request_id, "query": q}, exc_info=True)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return APIResponse(
            status=APIStatus.ERROR,
            message=f"Company lookup failed: {str(e)}",
            data=None,
            metadata={
                "response_time_ms": response_time,
                "error": True
            },
            request_id=request_id
        )


@router.get("/company/{ticker}", response_model=APIResponse)
async def get_company_by_ticker(
    request: Request,
    ticker: str = Path(
        ..., 
        description="Stock ticker symbol",
        example="TSLA",
        regex=r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$"
    ),
    company_service: CompanyService = Depends(get_company_service)
):
    """
    Get company information by ticker symbol
    
    Retrieve basic company information using the stock ticker symbol.
    
    **Parameters:**
    - **ticker**: Stock ticker symbol (e.g., TSLA, BRK.A)
    
    **Returns:**
    - Basic company information
    """
    start_time = time.time()
    request_id = security_service.generate_request_id(request)
    
    try:
        # Rate limiting
        security_service.check_rate_limit(request)
        
        # Validate ticker
        validated_ticker = security_service.validate_ticker(ticker)
        
        logger.info(f"Get company by ticker: {validated_ticker}",
                   extra={"request_id": request_id})
        
        # Get company information
        company = await company_service.get_company_by_ticker(validated_ticker)
        
        if not company:
            raise CompanyNotFoundError(f"No company found for ticker: {validated_ticker}")
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message=f"Company information retrieved for {validated_ticker}",
            data=company.dict(),
            metadata={
                "response_time_ms": response_time,
                "source": "company_database"
            },
            request_id=request_id
        )
        
    except CompanyNotFoundError as e:
        logger.warning(f"Company not found for ticker {ticker}: {e.message}",
                      extra={"request_id": request_id})
        raise HTTPException(status_code=404, detail=e.message)
        
    except ValidationError as e:
        logger.warning(f"Ticker validation error: {e.message}",
                      extra={"request_id": request_id, "ticker": ticker})
        raise HTTPException(status_code=400, detail=e.message)
        
    except Exception as e:
        logger.error(f"Error getting company by ticker {ticker}: {str(e)}",
                    extra={"request_id": request_id}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve company: {str(e)}")


@router.get("/stock/{ticker}", response_model=APIResponse)
async def get_stock_quote(
    request: Request,
    ticker: str = Path(
        ...,
        description="Stock ticker symbol", 
        example="TSLA"
    ),
    detailed: Optional[bool] = Query(
        False,
        description="Return detailed stock data including metrics"
    ),
    stock_service: StockService = Depends(get_stock_service)
):
    """
    Get stock quote for a ticker
    
    Retrieve current stock price and market data for a given ticker symbol.
    
    **Parameters:**
    - **ticker**: Stock ticker symbol
    - **detailed**: Include additional metrics like P/E ratio, 52-week range, etc.
    
    **Returns:**
    - Current stock quote with price, change, and volume
    - Additional metrics if detailed=true
    """
    start_time = time.time()
    request_id = security_service.generate_request_id(request)
    
    try:
        # Rate limiting
        security_service.check_rate_limit(request)
        
        # Validate ticker
        validated_ticker = security_service.validate_ticker(ticker)
        
        logger.info(f"Get stock quote: {validated_ticker}, detailed={detailed}",
                   extra={"request_id": request_id})
        
        if detailed:
            # Get comprehensive stock data
            stock_data = await stock_service.get_stock_data(validated_ticker)
            if not stock_data:
                raise StockNotFoundError(f"No stock data found for: {validated_ticker}")
            
            response_data = stock_data.dict()
            message = f"Detailed stock data retrieved for {validated_ticker}"
        else:
            # Get basic quote only
            stock_quote = await stock_service.get_stock_quote(validated_ticker)
            if not stock_quote:
                raise StockNotFoundError(f"No stock quote found for: {validated_ticker}")
            
            response_data = stock_quote.dict()
            message = f"Stock quote retrieved for {validated_ticker}"
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message=message,
            data=response_data,
            metadata={
                "response_time_ms": response_time,
                "data_source": "yahoo_finance",
                "detailed": detailed
            },
            request_id=request_id
        )
        
    except StockNotFoundError as e:
        logger.warning(f"Stock not found for ticker {ticker}: {e.message}",
                      extra={"request_id": request_id})
        raise HTTPException(status_code=404, detail=e.message)
        
    except ValidationError as e:
        logger.warning(f"Stock ticker validation error: {e.message}",
                      extra={"request_id": request_id, "ticker": ticker})
        raise HTTPException(status_code=400, detail=e.message)
        
    except Exception as e:
        logger.error(f"Error getting stock quote for {ticker}: {str(e)}",
                    extra={"request_id": request_id}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stock data: {str(e)}")


@router.get("/filings/{cik}", response_model=APIResponse)
async def get_company_filings(
    request: Request,
    cik: str = Path(
        ...,
        description="SEC Central Index Key",
        example="0001318605"
    ),
    form_types: Optional[List[str]] = Query(
        None,
        description="Filter by form types (e.g., 10-K, 10-Q, 8-K)"
    ),
    limit: Optional[int] = Query(
        10,
        description="Maximum number of filings to return",
        ge=1,
        le=50
    ),
    sec_service: SECService = Depends(get_sec_service)
):
    """
    Get SEC filings for a company
    
    Retrieve SEC filings for a company using its CIK (Central Index Key).
    
    **Parameters:**
    - **cik**: SEC Central Index Key (10 digits)
    - **form_types**: Filter by specific form types (optional)
    - **limit**: Maximum number of filings (default: 10, max: 50)
    
    **Returns:**
    - List of SEC filings with form type, date, and URLs
    - Filing metadata and summary information
    """
    start_time = time.time()
    request_id = security_service.generate_request_id(request)
    
    try:
        # Rate limiting (more restrictive for SEC data)
        security_service.check_rate_limit(request, limit_per_minute=20, limit_per_hour=500)
        
        # Validate CIK
        validated_cik = security_service.validate_cik(cik)
        
        logger.info(f"Get SEC filings: CIK={validated_cik}, forms={form_types}, limit={limit}",
                   extra={"request_id": request_id})
        
        # Create search criteria
        criteria = FilingSearchCriteria(
            cik=validated_cik,
            form_types=form_types,
            limit=limit
        )
        
        # Get filings
        filing_response = await sec_service.search_filings(criteria)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return APIResponse(
            status=APIStatus.SUCCESS,
            message=f"Retrieved {filing_response.filings_returned} filings for CIK {validated_cik}",
            data=filing_response.dict(),
            metadata={
                "response_time_ms": response_time,
                "data_source": "sec_edgar",
                "filters_applied": {
                    "form_types": form_types,
                    "limit": limit
                }
            },
            request_id=request_id
        )
        
    except ValidationError as e:
        logger.warning(f"CIK validation error: {e.message}",
                      extra={"request_id": request_id, "cik": cik})
        raise HTTPException(status_code=400, detail=e.message)
        
    except Exception as e:
        logger.error(f"Error getting filings for CIK {cik}: {str(e)}",
                    extra={"request_id": request_id}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SEC filings: {str(e)}")


@router.get("/stock/batch", response_model=APIResponse)
async def get_multiple_stock_quotes(
    request: Request,
    tickers: List[str] = Query(
        ...,
        description="List of ticker symbols",
        example=["TSLA", "AAPL", "MSFT"]
    ),
    stock_service: StockService = Depends(get_stock_service)
):
    """
    Get stock quotes for multiple tickers
    
    Retrieve stock quotes for multiple ticker symbols in a single request.
    
    **Parameters:**
    - **tickers**: List of ticker symbols (max 20)
    
    **Returns:**
    - Dictionary of ticker symbols to stock quotes
    - Failed quotes are marked as null with error info
    """
    start_time = time.time()
    request_id = security_service.generate_request_id(request)
    
    try:
        # Rate limiting (more restrictive for batch requests)
        security_service.check_rate_limit(request, limit_per_minute=10, limit_per_hour=200)
        
        # Validate input
        if len(tickers) > 20:
            raise ValidationError("Maximum 20 tickers allowed in batch request")
        
        if not tickers:
            raise ValidationError("At least one ticker is required")
        
        # Validate all tickers
        validated_tickers = []
        for ticker in tickers:
            validated_tickers.append(security_service.validate_ticker(ticker))
        
        logger.info(f"Batch stock quotes request: {len(validated_tickers)} tickers",
                   extra={"request_id": request_id, "tickers": validated_tickers})
        
        # Get quotes for all tickers
        quotes = await stock_service.get_multiple_quotes(validated_tickers)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Count successful vs failed quotes
        successful_count = sum(1 for quote in quotes.values() if quote is not None)
        failed_count = len(quotes) - successful_count
        
        if successful_count == len(quotes):
            status = APIStatus.SUCCESS
            message = f"Retrieved quotes for all {successful_count} tickers"
        elif successful_count > 0:
            status = APIStatus.PARTIAL
            message = f"Retrieved {successful_count}/{len(quotes)} quotes successfully"
        else:
            status = APIStatus.ERROR
            message = "Failed to retrieve any stock quotes"
        
        return APIResponse(
            status=status,
            message=message,
            data={
                "quotes": quotes,
                "summary": {
                    "total_requested": len(quotes),
                    "successful": successful_count,
                    "failed": failed_count
                }
            },
            metadata={
                "response_time_ms": response_time,
                "batch_size": len(quotes)
            },
            request_id=request_id
        )
        
    except ValidationError as e:
        logger.warning(f"Batch quotes validation error: {e.message}",
                      extra={"request_id": request_id})
        raise HTTPException(status_code=400, detail=e.message)
        
    except Exception as e:
        logger.error(f"Batch quotes error: {str(e)}",
                    extra={"request_id": request_id}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch stock quotes failed: {str(e)}")