import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json
import logging
from urllib.parse import urlencode

from app.models.filing import Filing, FilingResponse, FilingSearchCriteria
from app.config import settings
from app.core.exceptions import ExternalAPIError, SECAPIError

logger = logging.getLogger(__name__)


class SECService:
    """Service for SEC EDGAR API operations"""
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        
        # In-memory cache for SEC data (in production, use Redis or similar)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(seconds=settings.CACHE_TTL_SECONDS * 2)  # Longer cache for SEC data
        
        # SEC API configuration
        self.base_url = settings.SEC_EDGAR_BASE_URL
        self.headers = {
            "User-Agent": settings.SEC_USER_AGENT,
            "Accept": "application/json",
            "Host": "data.sec.gov"
        }
        
        # Rate limiting (SEC allows 10 requests per second)
        self._last_request_time = datetime.min
        self._min_request_interval = 0.1  # 100ms between requests
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers
            )
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate cache key"""
        return f"sec:{operation}:{':'.join(str(arg) for arg in args)}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if "timestamp" not in cache_entry:
            return False
        
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        return datetime.utcnow() - cache_time < self._cache_ttl
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Set cache entry"""
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cache entry if valid"""
        if key in self._cache and self._is_cache_valid(self._cache[key]):
            return self._cache[key]["data"]
        return None
    
    async def _rate_limit(self):
        """Implement rate limiting for SEC API"""
        now = datetime.utcnow()
        time_since_last = (now - self._last_request_time).total_seconds()
        
        if time_since_last < self._min_request_interval:
            wait_time = self._min_request_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self._last_request_time = datetime.utcnow()
    
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to SEC API with rate limiting"""
        await self._rate_limit()
        
        session = await self._get_session()
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.warning(f"SEC API returned 404 for URL: {url}")
                    return {}
                elif response.status == 429:
                    logger.warning("SEC API rate limit exceeded")
                    # Wait a bit longer and retry once
                    await asyncio.sleep(1)
                    async with session.get(url, params=params) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            raise SECAPIError(f"SEC API error after retry: {retry_response.status}")
                else:
                    error_text = await response.text()
                    logger.error(f"SEC API error {response.status}: {error_text}")
                    raise SECAPIError(f"SEC API returned status {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error calling SEC API: {str(e)}")
            raise ExternalAPIError(f"Failed to connect to SEC API: {str(e)}")
        except asyncio.TimeoutError:
            logger.error("Timeout calling SEC API")
            raise ExternalAPIError("SEC API request timed out")
    
    def _normalize_cik(self, cik: str) -> str:
        """Normalize CIK to 10-digit format with leading zeros"""
        if not cik:
            return cik
        
        # Remove any non-digits
        digits_only = ''.join(filter(str.isdigit, cik))
        
        # Pad with leading zeros to make 10 digits
        return digits_only.zfill(10)
    
    def _parse_filing_data(self, filing_data: Dict[str, Any], cik: str) -> Filing:
        """Parse SEC API filing data into Filing model"""
        try:
            # Extract filing information
            accession_number = filing_data.get('accessionNumber', '').replace('-', '')
            if len(accession_number) == 18:
                # Format as XXX-XX-XXXXXX
                accession_formatted = f"{accession_number[:10]}-{accession_number[10:12]}-{accession_number[12:]}"
            else:
                accession_formatted = filing_data.get('accessionNumber', '')
            
            # Construct filing URL
            cik_normalized = self._normalize_cik(cik)
            accession_no_dashes = accession_formatted.replace('-', '')
            
            # Primary document filename
            primary_document = filing_data.get('primaryDocument', '')
            if not primary_document:
                # Fallback to common naming patterns
                form_type = filing_data.get('form', '').lower()
                primary_document = f"{form_type.replace('-', '')}.htm"
            
            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/{cik_normalized}/"
                f"{accession_no_dashes}/{primary_document}"
            )
            
            # Parse filing date
            filing_date_str = filing_data.get('filingDate', '')
            try:
                filing_date = datetime.strptime(filing_date_str, '%Y-%m-%d').date()
            except ValueError:
                filing_date = date.today()  # Fallback
            
            # Parse period end date if available
            period_end_date = None
            period_end_str = filing_data.get('reportDate') or filing_data.get('periodOfReport')
            if period_end_str:
                try:
                    period_end_date = datetime.strptime(period_end_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            return Filing(
                form=filing_data.get('form', ''),
                filing_date=filing_date,
                accession_number=accession_formatted,
                filing_url=filing_url,
                company_name=filing_data.get('entityName'),
                cik=cik_normalized,
                file_size=filing_data.get('size'),
                document_count=filing_data.get('documentCount'),
                period_end_date=period_end_date,
                description=filing_data.get('description'),
                is_xbrl=filing_data.get('isXBRL', False),
                is_inline_xbrl=filing_data.get('isInlineXBRL', False)
            )
            
        except Exception as e:
            logger.error(f"Error parsing filing data: {str(e)}")
            logger.error(f"Filing data: {filing_data}")
            raise
    
    async def get_company_filings(self, cik: str, limit: int = 10) -> List[Filing]:
        """Get SEC filings for a company by CIK"""
        cik_normalized = self._normalize_cik(cik)
        
        # Check cache first
        cache_key = self._get_cache_key("filings", cik_normalized, limit)
        cached_result = self._get_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for SEC filings: CIK {cik_normalized}")
            return cached_result
        
        try:
            # Construct API URL
            url = f"{self.base_url}/submissions/CIK{cik_normalized}.json"
            
            # Make request to SEC API
            data = await self._make_request(url)
            
            if not data or 'filings' not in data:
                logger.warning(f"No filings data found for CIK: {cik_normalized}")
                return []
            
            filings_data = data['filings']['recent']
            
            # Parse filings
            filings = []
            num_filings = min(len(filings_data.get('form', [])), limit)
            
            for i in range(num_filings):
                try:
                    filing_info = {
                        'form': filings_data['form'][i],
                        'filingDate': filings_data['filingDate'][i],
                        'accessionNumber': filings_data['accessionNumber'][i],
                        'primaryDocument': filings_data.get('primaryDocument', [None] * len(filings_data['form']))[i],
                        'reportDate': filings_data.get('reportDate', [None] * len(filings_data['form']))[i],
                        'size': filings_data.get('size', [None] * len(filings_data['form']))[i],
                        'isXBRL': filings_data.get('isXBRL', [False] * len(filings_data['form']))[i],
                        'isInlineXBRL': filings_data.get('isInlineXBRL', [False] * len(filings_data['form']))[i],
                        'entityName': data.get('entityName')
                    }
                    
                    filing = self._parse_filing_data(filing_info, cik_normalized)
                    filings.append(filing)
                    
                except Exception as e:
                    logger.warning(f"Error parsing filing {i} for CIK {cik_normalized}: {str(e)}")
                    continue
            
            # Cache the result
            self._set_cache(cache_key, filings)
            
            logger.info(f"Retrieved {len(filings)} filings for CIK {cik_normalized}")
            return filings
            
        except SECAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting company filings for CIK {cik_normalized}: {str(e)}")
            raise ExternalAPIError(f"Failed to retrieve SEC filings: {str(e)}")
    
    async def get_recent_filings(self, cik: str, limit: int = 5) -> List[Filing]:
        """Get recent SEC filings for a company"""
        return await self.get_company_filings(cik, limit)
    
    async def search_filings(self, criteria: FilingSearchCriteria) -> FilingResponse:
        """Search SEC filings based on criteria"""
        if not criteria.cik and not criteria.ticker:
            raise ValueError("Either CIK or ticker must be provided")
        
        cik = criteria.cik
        if not cik and criteria.ticker:
            # In production, you'd look up CIK by ticker from a database
            # For now, we'll return empty results
            return FilingResponse(
                cik="unknown",
                filings=[],
                total_filings=0
            )
        
        # Get all filings first
        all_filings = await self.get_company_filings(cik, limit=100)  # Get more for filtering
        
        # Apply filters
        filtered_filings = all_filings
        
        # Filter by form types
        if criteria.form_types:
            form_types_upper = [ft.upper() for ft in criteria.form_types]
            filtered_filings = [f for f in filtered_filings if f.form.upper() in form_types_upper]
        
        # Filter by date range
        if criteria.date_from:
            filtered_filings = [f for f in filtered_filings if f.filing_date >= criteria.date_from]
        
        if criteria.date_to:
            filtered_filings = [f for f in filtered_filings if f.filing_date <= criteria.date_to]
        
        # Apply limit
        limit = criteria.limit or settings.DEFAULT_FILINGS_LIMIT
        result_filings = filtered_filings[:limit]
        
        # Calculate date range
        date_range = None
        if result_filings:
            dates = [f.filing_date for f in result_filings]
            date_range = {
                "earliest": min(dates),
                "latest": max(dates)
            }
        
        return FilingResponse(
            cik=cik,
            company_name=result_filings[0].company_name if result_filings else None,
            filings=result_filings,
            total_filings=len(filtered_filings),
            date_range=date_range
        )
    
    async def get_filing_content(self, filing_url: str) -> Optional[str]:
        """Get the content of a specific SEC filing"""
        # This would fetch and parse the actual filing content
        # Implementation depends on whether you want HTML, XBRL, or text content
        
        cache_key = self._get_cache_key("content", filing_url)
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            session = await self._get_session()
            
            async with session.get(filing_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Cache the content (with longer TTL since filings don't change)
                    content_cache = {
                        "data": content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "ttl": 86400  # 24 hours for filing content
                    }
                    self._cache[cache_key] = content_cache
                    
                    return content
                else:
                    logger.warning(f"Failed to fetch filing content: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching filing content from {filing_url}: {str(e)}")
            return None
    
    def cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if "timestamp" in entry:
                cache_time = datetime.fromisoformat(entry["timestamp"])
                # Use custom TTL if available, otherwise use default
                ttl = timedelta(seconds=entry.get("ttl", self._cache_ttl.total_seconds()))
                
                if current_time - cache_time > ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired SEC cache entries")