import yfinance as yf
import asyncio
import time
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.models.stock import StockQuote, StockData, StockHistoricalData
from app.config import settings
from app.core.exceptions import ExternalAPIError, StockNotFoundError

logger = logging.getLogger(__name__)


class StockService:
    """Service for stock price and market data operations"""
    
    def __init__(self):
        # In-memory cache for stock data (in production, use Redis or similar)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(seconds=300)  # 5 minutes cache for stock data
        
        # Thread pool for running synchronous yfinance calls
        self._executor = ThreadPoolExecutor(max_workers=5)  # Reduced for rate limiting
        
        # Rate limiting
        self._last_request_time = {}
        self._min_request_interval = 1.5  # Minimum 1.5 seconds between requests
        
        # Setup session with retries
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with proper headers and retries"""
        self.session = requests.Session()
        
        # Add retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[426, 429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Better headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        })
    
    async def _rate_limit(self, symbol: str):
        """Apply rate limiting per symbol"""
        now = time.time()
        if symbol in self._last_request_time:
            elapsed = now - self._last_request_time[symbol]
            if elapsed < self._min_request_interval:
                sleep_time = self._min_request_interval - elapsed + random.uniform(0.1, 0.5)
                await asyncio.sleep(sleep_time)
        self._last_request_time[symbol] = time.time()
    
    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate cache key"""
        return f"stock:{operation}:{':'.join(str(arg).upper() for arg in args)}"
    
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
    
    def _run_in_executor(self, func, *args):
        """Run synchronous function in executor"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self._executor, func, *args)
    
    def _fetch_ticker_data_safe(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Safely fetch ticker data with fallbacks"""
        try:
            # Method 1: Use yfinance with session
            ticker = yf.Ticker(symbol, session=self.session)
            
            # Add delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            # Try to get basic info first
            try:
                info = ticker.info
                if info and isinstance(info, dict) and info.get('symbol'):
                    return {"ticker": ticker, "info": info, "method": "yfinance_info"}
            except Exception as e:
                logger.warning(f"yfinance info failed for {symbol}: {e}")
            
            # Method 2: Try history-based approach
            try:
                hist = ticker.history(period="2d", interval="1d", timeout=10)
                if not hist.empty:
                    latest = hist.iloc[-1]
                    return {
                        "ticker": ticker,
                        "history": hist,
                        "latest_price": float(latest['Close']),
                        "method": "yfinance_history"
                    }
            except Exception as e:
                logger.warning(f"yfinance history failed for {symbol}: {e}")
            
            # Method 3: Fallback to Yahoo Finance direct API
            try:
                return self._fetch_yahoo_direct(symbol)
            except Exception as e:
                logger.warning(f"Yahoo direct API failed for {symbol}: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"All methods failed for {symbol}: {e}")
            return None
    
    def _fetch_yahoo_direct(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Direct Yahoo Finance API call as fallback"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                chart = data.get('chart', {})
                result = chart.get('result', [])
                
                if result:
                    result_data = result[0]
                    meta = result_data.get('meta', {})
                    
                    return {
                        "price": meta.get('regularMarketPrice'),
                        "previous_close": meta.get('previousClose'),
                        "currency": meta.get('currency', 'USD'),
                        "symbol": meta.get('symbol', symbol),
                        "method": "yahoo_direct"
                    }
            
        except Exception as e:
            logger.error(f"Yahoo direct API error for {symbol}: {e}")
        
        return None
    
    async def get_stock_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get current stock quote for a symbol with better error handling"""
        symbol = symbol.upper().strip()
        
        # Check cache first
        cache_key = self._get_cache_key("quote", symbol)
        cached_result = self._get_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for stock quote: {symbol}")
            return cached_result
        
        # Apply rate limiting
        await self._rate_limit(symbol)
        
        try:
            # Fetch data with multiple fallback methods
            data = await self._run_in_executor(self._fetch_ticker_data_safe, symbol)
            
            if not data:
                logger.warning(f"No stock data available for {symbol}")
                return None
            
            # Process based on method used
            if data.get("method") == "yahoo_direct":
                return await self._process_direct_data(symbol, data)
            elif data.get("method") == "yfinance_history":
                return await self._process_history_data(symbol, data)
            elif data.get("method") == "yfinance_info":
                return await self._process_info_data(symbol, data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting stock quote for {symbol}: {e}")
            # Don't raise exception, return None to allow graceful degradation
            return None
    
    async def _process_direct_data(self, symbol: str, data: Dict) -> Optional[StockQuote]:
        """Process data from direct Yahoo API"""
        try:
            current_price = data.get('price')
            previous_close = data.get('previous_close')
            
            if not current_price:
                return None
            
            change = None
            change_percent = None
            
            if previous_close and previous_close > 0:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            
            stock_quote = StockQuote(
                symbol=symbol,
                price=round(current_price, 2),
                currency=data.get('currency', 'USD').upper(),
                change=round(change, 2) if change is not None else None,
                change_percent=round(change_percent, 2) if change_percent is not None else None,
                volume=None,  # Not available from this endpoint
                market_cap=None,
                last_updated=datetime.utcnow(),
                market_state="UNKNOWN"
            )
            
            # Cache the result
            self._set_cache(self._get_cache_key("quote", symbol), stock_quote)
            
            logger.info(f"Retrieved stock quote via direct API for {symbol}: ${current_price}")
            return stock_quote
            
        except Exception as e:
            logger.error(f"Error processing direct data for {symbol}: {e}")
            return None
    
    async def _process_history_data(self, symbol: str, data: Dict) -> Optional[StockQuote]:
        """Process data from yfinance history"""
        try:
            hist = data.get('history')
            current_price = data.get('latest_price')
            
            if hist is None or current_price is None:
                return None
            
            # Calculate change from previous day if available
            change = None
            change_percent = None
            
            if len(hist) >= 2:
                previous_close = float(hist.iloc[-2]['Close'])
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            
            # Get volume from latest day
            volume = None
            if not hist.empty:
                volume = int(hist.iloc[-1]['Volume'])
            
            stock_quote = StockQuote(
                symbol=symbol,
                price=round(current_price, 2),
                currency='USD',  # Default, would need separate call to get exact currency
                change=round(change, 2) if change is not None else None,
                change_percent=round(change_percent, 2) if change_percent is not None else None,
                volume=volume,
                market_cap=None,
                last_updated=datetime.utcnow(),
                market_state="UNKNOWN"
            )
            
            # Cache the result
            self._set_cache(self._get_cache_key("quote", symbol), stock_quote)
            
            logger.info(f"Retrieved stock quote via history for {symbol}: ${current_price}")
            return stock_quote
            
        except Exception as e:
            logger.error(f"Error processing history data for {symbol}: {e}")
            return None
    
    async def _process_info_data(self, symbol: str, data: Dict) -> Optional[StockQuote]:
        """Process data from yfinance info"""
        try:
            info = data.get('info', {})
            
            # Extract quote data
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            previous_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
            
            if current_price is None:
                return None
            
            # Calculate change and change percentage
            change = None
            change_percent = None
            
            if previous_close is not None and previous_close > 0:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            
            # Get additional data
            volume = info.get('regularMarketVolume') or info.get('volume')
            market_cap = info.get('marketCap')
            currency = info.get('currency', 'USD')
            
            stock_quote = StockQuote(
                symbol=symbol,
                price=round(current_price, 2),
                currency=currency.upper(),
                change=round(change, 2) if change is not None else None,
                change_percent=round(change_percent, 2) if change_percent is not None else None,
                volume=volume,
                market_cap=market_cap,
                last_updated=datetime.utcnow(),
                market_state=self._determine_market_state(info)
            )
            
            # Cache the result
            self._set_cache(self._get_cache_key("quote", symbol), stock_quote)
            
            logger.info(f"Retrieved stock quote via info for {symbol}: ${current_price}")
            return stock_quote
            
        except Exception as e:
            logger.error(f"Error processing info data for {symbol}: {e}")
            return None
    
    def _determine_market_state(self, info: Dict[str, Any]) -> str:
        """Determine current market state based on ticker info"""
        market_state = info.get('marketState', 'UNKNOWN')
        if market_state in ['REGULAR', 'CLOSED', 'PRE', 'POST']:
            return market_state
        
        # Fallback logic based on other indicators
        if info.get('regularMarketPrice'):
            return 'REGULAR'
        elif info.get('preMarketPrice'):
            return 'PRE'
        elif info.get('postMarketPrice'):
            return 'POST'
        else:
            return 'CLOSED'
    
    async def validate_symbol(self, symbol: str) -> bool:
        """Validate if a stock symbol exists"""
        try:
            quote = await self.get_stock_quote(symbol)
            return quote is not None
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False
    
    def cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if "timestamp" in entry:
                cache_time = datetime.fromisoformat(entry["timestamp"])
                if current_time - cache_time > self._cache_ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def close(self):
        """Clean up resources"""
        self._executor.shutdown(wait=True)
        if hasattr(self, 'session'):
            self.session.close()
        self.cleanup_cache()
        logger.info("Stock service resources cleaned up")