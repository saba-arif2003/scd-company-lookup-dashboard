import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import time
import random

# Import only the stock service, avoid the problematic models for now
from .stock_service import StockService
from .sec_service import SECService
from app.config import settings
from app.core.exceptions import CompanyNotFoundError, ExternalAPIError

logger = logging.getLogger(__name__)


class SimplifiedCompanyService:
    """Simplified company service without Pydantic models to avoid recursion issues"""
    
    def __init__(self):
        self.stock_service = StockService()
        try:
            self.sec_service = SECService()
        except:
            self.sec_service = None
            logger.warning("SECService initialization failed, continuing without SEC filings")
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=5)
        
        # Rate limiting
        self._last_api_call = {}
        self._api_delays = {
            "sec": 1.0,
            "yahoo": 0.5,
            "fmp": 1.0,
        }
    
    async def __aenter__(self):
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_cache_key(self, operation: str, *args) -> str:
        return f"{operation}:{':'.join(str(arg) for arg in args)}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        if "timestamp" not in cache_entry:
            return False
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        return datetime.utcnow() - cache_time < self._cache_ttl
    
    def _set_cache(self, key: str, data: Any) -> None:
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_cache(self, key: str) -> Optional[Any]:
        if key in self._cache and self._is_cache_valid(self._cache[key]):
            return self._cache[key]["data"]
        return None
    
    async def _rate_limit(self, api_name: str):
        """Apply rate limiting per API"""
        delay = self._api_delays.get(api_name, 1.0)
        now = time.time()
        if api_name in self._last_api_call:
            elapsed = now - self._last_api_call[api_name]
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed + random.uniform(0.1, 0.5))
        self._last_api_call[api_name] = time.time()
    
    async def _search_yahoo_finance(self, query: str) -> List[Dict]:
        """Search using Yahoo Finance Search API"""
        try:
            await self._rate_limit("yahoo")
            session = await self._get_session()
            
            url = "https://query1.finance.yahoo.com/v1/finance/search"
            params = {
                "q": query,
                "lang": "en-US",
                "region": "US",
                "quotesCount": 10,
                "newsCount": 0
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quotes = data.get("quotes", [])
                    
                    results = []
                    for quote in quotes:
                        symbol = quote.get("symbol", "")
                        name = quote.get("longname") or quote.get("shortname", "")
                        exchange = quote.get("exchange", "")
                        
                        if symbol and name:
                            score = self._calculate_match_score(query, name, symbol)
                            
                            results.append({
                                "name": name,
                                "ticker": symbol,
                                "cik": "0000000000",
                                "exchange": exchange,
                                "match_score": score
                            })
                    
                    return results
                    
        except Exception as e:
            logger.warning(f"Yahoo Finance search failed for '{query}': {e}")
        
        return []
    
    async def _search_sec_database(self, query: str) -> List[Dict]:
        """Search SEC database"""
        try:
            await self._rate_limit("sec")
            session = await self._get_session()
            
            url = "https://www.sec.gov/files/company_tickers.json"
            headers = {
                "User-Agent": "CompanyLookupDashboard/1.0 (sabaarif2003@gmail.com)",
                "Accept": "application/json"
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    query_lower = query.lower().strip()
                    
                    for entry_key, company_data in data.items():
                        if not isinstance(company_data, dict):
                            continue
                            
                        company_name = company_data.get('title', '')
                        ticker = company_data.get('ticker', '').upper()
                        cik_str = str(company_data.get('cik_str', '')).zfill(10)
                        
                        if not company_name or not ticker:
                            continue
                        
                        score = self._calculate_match_score(query, company_name, ticker)
                        
                        if score > 0.3:
                            results.append({
                                "name": company_name,
                                "ticker": ticker,
                                "cik": cik_str,
                                "exchange": 'NASDAQ',
                                "match_score": score
                            })
                    
                    return sorted(results, key=lambda x: x.get("match_score", 0), reverse=True)[:10]
                    
        except Exception as e:
            logger.warning(f"SEC search failed for '{query}': {e}")
        
        return []
    
    def _calculate_match_score(self, query: str, company_name: str, ticker: str) -> float:
        """Calculate match score between query and company"""
        query_lower = query.lower().strip()
        name_lower = company_name.lower()
        ticker_lower = ticker.lower()
        
        # Exact ticker match
        if query_lower == ticker_lower:
            return 1.0
        
        # Exact name match
        if query_lower == name_lower:
            return 0.95
        
        # Ticker starts with query
        if ticker_lower.startswith(query_lower):
            return 0.9
        
        # Company name starts with query
        if name_lower.startswith(query_lower):
            return 0.85
        
        # Query is in company name
        if query_lower in name_lower:
            return 0.8
        
        # Any word in company name starts with query
        name_words = name_lower.split()
        for word in name_words:
            if word.startswith(query_lower):
                return 0.75
        
        return 0.0
    
    async def search_companies(self, query: str) -> Dict:
        """Search companies using multiple APIs"""
        start_time = datetime.utcnow()
        
        if not query or len(query.strip()) < 1:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "took_ms": 0,
                "suggestions": []
            }
        
        # Check cache
        cache_key = self._get_cache_key("search", query)
        cached_result = self._get_cache(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for: {query}")
            return cached_result
        
        try:
            logger.info(f"Starting search for: '{query}'")
            
            # Search multiple sources concurrently
            yahoo_task = self._search_yahoo_finance(query)
            sec_task = self._search_sec_database(query)
            
            # Execute searches
            yahoo_results, sec_results = await asyncio.gather(
                yahoo_task, sec_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(yahoo_results, Exception):
                logger.warning(f"Yahoo search failed: {yahoo_results}")
                yahoo_results = []
            if isinstance(sec_results, Exception):
                logger.warning(f"SEC search failed: {sec_results}")
                sec_results = []
            
            # Combine results
            all_results = list(yahoo_results) + list(sec_results)
            
            # Deduplicate by ticker
            seen_tickers = set()
            final_results = []
            
            for result in all_results:
                ticker_key = result.get("ticker", "").upper()
                if ticker_key and ticker_key not in seen_tickers:
                    final_results.append(result)
                    seen_tickers.add(ticker_key)
            
            # Sort by match score
            final_results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            
            # Generate suggestions
            suggestions = []
            if not final_results:
                suggestions = [
                    f"Try searching with ticker symbol",
                    f"Include company suffix (Ltd, Inc, Corporation)",
                    f"Check spelling and try again"
                ]
            
            elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            response = {
                "query": query,
                "results": final_results[:20],  # Limit results
                "total_results": len(final_results),
                "took_ms": elapsed_ms,
                "suggestions": suggestions[:3]
            }
            
            logger.info(f"Search for '{query}': {len(final_results)} companies found")
            
            # Cache the result
            self._set_cache(cache_key, response)
            return response
            
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}", exc_info=True)
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "took_ms": 0,
                "suggestions": ["Search failed, please try again"]
            }
    
    async def get_company_lookup(self, query: str) -> Dict:
        """Get complete company information"""
        cache_key = self._get_cache_key("lookup", query)
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Search for company first
            search_results = await self.search_companies(query)
            
            if not search_results.get("results"):
                raise CompanyNotFoundError(f"No company found for query: {query}")
            
            best_match = search_results["results"][0]
            
            # Create company dict (no Pydantic model)
            company = {
                "name": best_match["name"],
                "ticker": best_match["ticker"],
                "cik": best_match["cik"],
                "exchange": best_match.get("exchange", "UNKNOWN")
            }
            
            # Get stock quote
            stock_quote = None
            try:
                stock_quote_obj = await self.stock_service.get_stock_quote(best_match["ticker"])
                if stock_quote_obj:
                    stock_quote = {
                        "symbol": stock_quote_obj.symbol,
                        "price": stock_quote_obj.price,
                        "currency": stock_quote_obj.currency,
                        "change": stock_quote_obj.change,
                        "change_percent": stock_quote_obj.change_percent,
                        "volume": stock_quote_obj.volume,
                        "market_cap": stock_quote_obj.market_cap,
                        "last_updated": stock_quote_obj.last_updated.isoformat(),
                        "market_state": stock_quote_obj.market_state
                    }
            except Exception as e:
                logger.warning(f"Stock quote failed for {best_match['ticker']}: {e}")
            
            # Get SEC filings (skip if service not available)
            filings = []
            try:
                if self.sec_service and best_match["cik"] != "0000000000":
                    filings = await self.sec_service.get_recent_filings(best_match["cik"], limit=5)
            except Exception as e:
                logger.warning(f"SEC filings failed: {e}")
            
            response = {
                "company": company,
                "stock_quote": stock_quote,
                "recent_filings": filings or [],
                "last_updated": datetime.utcnow().isoformat(),
                "data_sources": {
                    "company_info": "Multiple APIs (Yahoo Finance, SEC)",
                    "stock_quote": "Yahoo Finance",
                    "filings": "SEC EDGAR API"
                }
            }
            
            self._set_cache(cache_key, response)
            return response
            
        except CompanyNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Company lookup failed: {e}", exc_info=True)
            raise ExternalAPIError(f"Company lookup failed: {str(e)}")