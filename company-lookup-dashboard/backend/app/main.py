from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import aiohttp
import yfinance as yf
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
search_cache = {}
session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    print("Starting Enhanced Company Lookup API with AI Analysis...")
    
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    session = aiohttp.ClientSession(timeout=timeout, headers=headers)
    
    yield
    
    if session:
        await session.close()
    print("Shutting down API...")

app = FastAPI(
    title="Enhanced Company Lookup API with AI Analysis",
    description="Search companies with SEC filings and comprehensive AI investment insights",
    version="5.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache functions
def get_cache_key(operation: str, query: str) -> str:
    return f"{operation}:{query.lower().strip()}"

def is_cache_valid(cache_entry: Dict, max_age_seconds: int = 300) -> bool:
    if not cache_entry or "timestamp" not in cache_entry:
        return False
    age = time.time() - cache_entry["timestamp"]
    return age < max_age_seconds

def set_cache(key: str, data) -> None:
    search_cache[key] = {
        "data": data,
        "timestamp": time.time()
    }

def get_cache(key: str) -> Optional[Dict]:
    if key in search_cache and is_cache_valid(search_cache[key]):
        return search_cache[key]["data"]
    return None

# Stock quote function
def get_stock_quote_sync(ticker: str) -> Optional[Dict]:
    """Get stock quote with fallback methods"""
    try:
        stock = yf.Ticker(ticker)
        time.sleep(random.uniform(0.5, 1.0))
        
        try:
            info = stock.info
            if info and info.get('regularMarketPrice'):
                current_price = info.get('regularMarketPrice')
                previous_close = info.get('regularMarketPreviousClose', current_price)
                change = current_price - previous_close if previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                return {
                    "symbol": ticker.upper(),
                    "price": round(current_price, 2),
                    "currency": info.get('currency', 'USD'),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": info.get('regularMarketVolume'),
                    "market_cap": info.get('marketCap'),
                    "last_updated": datetime.utcnow().isoformat(),
                    "market_state": info.get('marketState', 'UNKNOWN')
                }
        except Exception as e:
            logger.warning(f"YFinance info failed for {ticker}: {e}")
        
        # Fallback: try direct Yahoo API
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                chart = data.get('chart', {})
                result = chart.get('result', [])
                
                if result:
                    meta = result[0].get('meta', {})
                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose')
                    
                    if current_price:
                        change = current_price - previous_close if previous_close else 0
                        change_percent = (change / previous_close * 100) if previous_close else 0
                        
                        return {
                            "symbol": ticker.upper(),
                            "price": round(current_price, 2),
                            "currency": meta.get('currency', 'USD'),
                            "change": round(change, 2),
                            "change_percent": round(change_percent, 2),
                            "volume": meta.get('regularMarketVolume'),
                            "market_cap": None,
                            "last_updated": datetime.utcnow().isoformat(),
                            "market_state": "UNKNOWN"
                        }
        except Exception as e:
            logger.warning(f"Yahoo direct API failed for {ticker}: {e}")
        
        return None
        
    except Exception as e:
        logger.warning(f"Stock quote failed for {ticker}: {e}")
        return None

# SEC Filings functions
async def get_sec_filings(cik: str, limit: int = 10) -> List[Dict]:
    """Get SEC filings for a company"""
    if not cik or cik == "0000000000":
        return []
    
    try:
        global session
        cik_clean = str(int(cik)).zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_clean}.json"
        
        headers = {
            "User-Agent": "CompanyLookupDashboard/5.1 (sabaarif2003@gmail.com)",
            "Accept": "application/json"
        }
        
        await asyncio.sleep(1.0)  # Rate limiting
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                filings = data.get('filings', {}).get('recent', {})
                
                forms = filings.get('form', [])
                dates = filings.get('filingDate', [])
                accessions = filings.get('accessionNumber', [])
                
                results = []
                for i in range(min(limit, len(forms))):
                    if i < len(dates) and i < len(accessions):
                        acc_no = accessions[i].replace('-', '')
                        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no}/{accessions[i]}-index.html"
                        
                        results.append({
                            "form": forms[i],
                            "filing_date": dates[i],
                            "accession_number": accessions[i],
                            "filing_url": filing_url
                        })
                
                logger.info(f"Retrieved {len(results)} SEC filings for CIK {cik}")
                return results
            else:
                logger.warning(f"SEC API returned status {response.status} for CIK {cik}")
                
    except Exception as e:
        logger.warning(f"SEC filings failed for CIK {cik}: {e}")
    
    return []

# Search functions
def calculate_match_score(query: str, company_name: str, ticker: str) -> float:
    """Calculate relevance score"""
    query_lower = query.lower().strip()
    name_lower = company_name.lower()
    ticker_lower = ticker.lower()
    
    if query_lower == ticker_lower:
        return 1.0
    if query_lower == name_lower:
        return 0.95
    if ticker_lower.startswith(query_lower):
        return 0.9
    if name_lower.startswith(query_lower):
        return 0.85
    if query_lower in name_lower:
        return 0.8
    
    name_words = name_lower.split()
    for word in name_words:
        if word.startswith(query_lower):
            return 0.75
    
    return 0.0

async def search_sec_database(query: str) -> List[Dict]:
    """Search SEC database for US companies with correct CIKs"""
    global session
    
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            "User-Agent": "CompanyLookupDashboard/5.1 (sabaarif2003@gmail.com)",
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
                    
                    score = calculate_match_score(query, company_name, ticker)
                    
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

async def search_yahoo_finance(query: str) -> List[Dict]:
    """Search Yahoo Finance"""
    global session
    
    try:
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
                        score = calculate_match_score(query, name, symbol)
                        results.append({
                            "name": name,
                            "ticker": symbol,
                            "cik": "0000000000",  # Yahoo doesn't provide CIK
                            "exchange": exchange,
                            "match_score": score
                        })
                
                return results
                
    except Exception as e:
        logger.warning(f"Yahoo Finance search failed for '{query}': {e}")
    
    return []

# Advanced AI Analysis
async def generate_comprehensive_ai_analysis(company_data: Dict, stock_data: Optional[Dict], filings_data: List[Dict]) -> Dict:
    """Generate comprehensive AI investment analysis"""
    
    analysis = {
        "summary": {
            "company_name": company_data.get("name", "Unknown"),
            "ticker": company_data.get("ticker", "N/A"),
            "analysis_date": datetime.utcnow().isoformat(),
            "educational_sentiment": "neutral",
            "confidence_level": "moderate"
        },
        "risk_assessment": {
            "overall_risk_level": "moderate",
            "risk_factors": [],
            "positive_factors": [],
            "risk_score": 5
        },
        "technical_analysis": {
            "price_trend": "neutral",
            "volatility_assessment": "moderate",
            "volume_analysis": "average"
        },
        "fundamental_insights": {
            "market_position": "unknown",
            "financial_health": "unknown",
            "growth_prospects": "unknown"
        },
        "recent_developments": [],
        "educational_considerations": [
            "This analysis is for educational purposes only - not financial advice",
            "Always consult with qualified financial professionals before investing",
            "Consider your personal risk tolerance and investment timeline",
            "Diversification is crucial for managing portfolio risk",
            "Past performance does not guarantee future results"
        ],
        "disclaimer": "Educational analysis only. This is not investment advice. Always consult licensed financial advisors before making investment decisions."
    }
    
    # Analyze stock data if available
    if stock_data:
        price = stock_data.get("price", 0)
        change_percent = stock_data.get("change_percent", 0)
        market_cap = stock_data.get("market_cap", 0)
        volume = stock_data.get("volume", 0)
        
        # Price trend analysis
        if change_percent > 5:
            analysis["technical_analysis"]["price_trend"] = "strong_positive"
            analysis["risk_assessment"]["positive_factors"].append("Strong positive price momentum (+{:.1f}%)".format(change_percent))
            analysis["summary"]["educational_sentiment"] = "optimistic"
        elif change_percent > 2:
            analysis["technical_analysis"]["price_trend"] = "positive"
            analysis["risk_assessment"]["positive_factors"].append("Positive price momentum (+{:.1f}%)".format(change_percent))
        elif change_percent < -5:
            analysis["technical_analysis"]["price_trend"] = "strong_negative"
            analysis["risk_assessment"]["risk_factors"].append("Significant price decline ({:.1f}%)".format(change_percent))
            analysis["risk_assessment"]["risk_score"] += 2
            analysis["summary"]["educational_sentiment"] = "cautious"
        elif change_percent < -2:
            analysis["technical_analysis"]["price_trend"] = "negative"
            analysis["risk_assessment"]["risk_factors"].append("Recent price weakness ({:.1f}%)".format(change_percent))
            analysis["risk_assessment"]["risk_score"] += 1
        
        # Volatility assessment
        if abs(change_percent) > 5:
            analysis["technical_analysis"]["volatility_assessment"] = "high"
            analysis["risk_assessment"]["risk_factors"].append("High price volatility observed")
            analysis["risk_assessment"]["risk_score"] += 1
        elif abs(change_percent) < 1:
            analysis["technical_analysis"]["volatility_assessment"] = "low"
            analysis["risk_assessment"]["positive_factors"].append("Low price volatility - more stable")
        
        # Market cap analysis
        if market_cap:
            if market_cap > 200_000_000_000:  # >$200B
                analysis["fundamental_insights"]["market_position"] = "mega_cap_leader"
                analysis["risk_assessment"]["positive_factors"].append("Mega-cap company with strong market position")
                analysis["risk_assessment"]["risk_score"] -= 2
            elif market_cap > 50_000_000_000:  # >$50B
                analysis["fundamental_insights"]["market_position"] = "large_cap"
                analysis["risk_assessment"]["positive_factors"].append("Large-cap stability and institutional backing")
                analysis["risk_assessment"]["risk_score"] -= 1
            elif market_cap > 10_000_000_000:  # >$10B
                analysis["fundamental_insights"]["market_position"] = "established_company"
                analysis["risk_assessment"]["positive_factors"].append("Well-established company with proven track record")
            elif market_cap < 2_000_000_000:  # <$2B
                analysis["fundamental_insights"]["market_position"] = "small_cap"
                analysis["risk_assessment"]["risk_factors"].append("Small-cap volatility and liquidity risks")
                analysis["risk_assessment"]["risk_score"] += 2
        
        # Volume analysis
        if volume and volume > 10_000_000:
            analysis["technical_analysis"]["volume_analysis"] = "high"
            analysis["risk_assessment"]["positive_factors"].append("High trading volume indicates strong investor interest")
        elif volume and volume < 1_000_000:
            analysis["technical_analysis"]["volume_analysis"] = "low"
            analysis["risk_assessment"]["risk_factors"].append("Low trading volume may indicate limited liquidity")
    
    # Analyze SEC filings
    if filings_data:
        recent_8k = []
        recent_10k = []
        recent_10q = []
        
        for filing in filings_data:
            form = filing.get("form", "").upper()
            if form in ["8-K", "8-K/A"]:
                recent_8k.append(filing)
            elif form in ["10-K", "10-K/A"]:
                recent_10k.append(filing)
            elif form in ["10-Q", "10-Q/A"]:
                recent_10q.append(filing)
        
        # 8-K analysis (material events)
        if recent_8k:
            if len(recent_8k) > 3:
                analysis["risk_assessment"]["risk_factors"].append("Multiple recent 8-K filings may indicate significant corporate changes")
                analysis["recent_developments"].append(f"Multiple material events reported ({len(recent_8k)} 8-K filings)")
            else:
                analysis["recent_developments"].append(f"Recent material events reported ({len(recent_8k)} 8-K filing{'s' if len(recent_8k) > 1 else ''})")
        
        # 10-K analysis (annual reports)
        if recent_10k:
            latest_10k = recent_10k[0]
            filing_date = latest_10k.get("filing_date", "")
            if filing_date:
                try:
                    filing_datetime = datetime.strptime(filing_date, "%Y-%m-%d")
                    days_since = (datetime.now() - filing_datetime).days
                    
                    if days_since < 90:
                        analysis["risk_assessment"]["positive_factors"].append("Recent annual report filed - up-to-date financial disclosure")
                        analysis["recent_developments"].append("Recent 10-K annual report filed")
                    elif days_since > 450:  # Over 15 months
                        analysis["risk_assessment"]["risk_factors"].append("Annual reporting appears overdue")
                except:
                    pass
        
        # 10-Q analysis (quarterly reports)
        if recent_10q:
            analysis["risk_assessment"]["positive_factors"].append("Regular quarterly reporting demonstrates good corporate governance")
            analysis["recent_developments"].append(f"Recent quarterly filings ({len(recent_10q)} 10-Q reports)")
        
        # Overall filing activity
        total_filings = len(filings_data)
        if total_filings > 20:
            analysis["risk_assessment"]["positive_factors"].append("Comprehensive SEC filing history shows transparency")
        elif total_filings < 5:
            analysis["risk_assessment"]["risk_factors"].append("Limited SEC filing history")
    else:
        # No SEC filings available
        if company_data.get("cik") == "0000000000":
            analysis["recent_developments"].append("No SEC filings available - may be non-US company or recent IPO")
        else:
            analysis["risk_assessment"]["risk_factors"].append("SEC filings not accessible for analysis")
    
    # Final risk assessment
    risk_score = analysis["risk_assessment"]["risk_score"]
    positive_count = len(analysis["risk_assessment"]["positive_factors"])
    risk_count = len(analysis["risk_assessment"]["risk_factors"])
    
    if risk_score >= 8 or (risk_count > positive_count + 1):
        analysis["risk_assessment"]["overall_risk_level"] = "high"
        analysis["summary"]["educational_sentiment"] = "cautious"
        analysis["educational_considerations"].insert(0, "Higher risk factors identified - requires careful consideration of risk tolerance")
    elif risk_score <= 3 and positive_count > risk_count:
        analysis["risk_assessment"]["overall_risk_level"] = "low"
        if analysis["summary"]["educational_sentiment"] == "neutral":
            analysis["summary"]["educational_sentiment"] = "optimistic"
        analysis["educational_considerations"].insert(0, "Lower risk profile identified, but diversification remains important")
    
    # Confidence level
    has_stock_data = stock_data is not None
    has_filings_data = len(filings_data) > 0
    
    if has_stock_data and has_filings_data:
        analysis["summary"]["confidence_level"] = "high"
    elif has_stock_data or has_filings_data:
        analysis["summary"]["confidence_level"] = "moderate"
    else:
        analysis["summary"]["confidence_level"] = "low"
        analysis["educational_considerations"].insert(0, "Limited data available - analysis confidence is low")
    
    return analysis

# FastAPI Endpoints
@app.get("/")
async def root():
    return {
        "message": "Enhanced Company Lookup API with AI Analysis v5.1",
        "status": "running",
        "features": [
            "Dynamic company search with SEC database integration",
            "Comprehensive AI investment analysis (educational only)",
            "Real-time stock quotes with multiple fallbacks", 
            "SEC filings integration with proper CIK mapping",
            "Advanced risk assessment and technical analysis"
        ]
    }

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "service": "Enhanced Company Lookup API"}

@app.get("/api/v1/health/simple")
async def health_simple():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/search")
async def search_companies(q: str = Query(...)):
    """Search companies with prioritized SEC database results"""
    try:
        start_time = time.time()
        logger.info(f"Search request: {q}")
        
        # Check cache
        cache_key = get_cache_key("search", q)
        cached = get_cache(cache_key)
        if cached:
            return {
                "status": "success",
                "message": f"Found {cached.get('total_results', 0)} companies (cached)",
                "data": cached
            }
        
        # Search both SEC database and Yahoo Finance concurrently
        sec_task = search_sec_database(q)
        yahoo_task = search_yahoo_finance(q)
        
        sec_results, yahoo_results = await asyncio.gather(
            sec_task, yahoo_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(sec_results, Exception):
            logger.warning(f"SEC search failed: {sec_results}")
            sec_results = []
        if isinstance(yahoo_results, Exception):
            logger.warning(f"Yahoo search failed: {yahoo_results}")
            yahoo_results = []
        
        # Prioritize SEC results (they have correct CIKs)
        seen_tickers = set()
        final_results = []
        
        # Add SEC results first (higher priority)
        for result in sec_results:
            ticker = result.get("ticker", "").upper()
            if ticker and ticker not in seen_tickers:
                final_results.append(result)
                seen_tickers.add(ticker)
        
        # Add Yahoo results for tickers not found in SEC
        for result in yahoo_results:
            ticker = result.get("ticker", "").upper()
            if ticker and ticker not in seen_tickers:
                final_results.append(result)
                seen_tickers.add(ticker)
        
        # Sort by relevance score
        final_results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        response_data = {
            "query": q,
            "results": final_results[:15],
            "total_results": len(final_results),
            "took_ms": elapsed_ms,
            "suggestions": []
        }
        
        set_cache(cache_key, response_data)
        
        logger.info(f"Found {len(final_results)} companies for '{q}' in {elapsed_ms}ms")
        
        return {
            "status": "success",
            "message": f"Found {len(final_results)} companies",
            "data": response_data
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "status": "success",
            "message": "Search completed",
            "data": {
                "query": q,
                "results": [],
                "total_results": 0,
                "took_ms": 0,
                "suggestions": []
            }
        }

@app.get("/api/v1/search/suggestions")
async def search_suggestions(q: str = Query(...), limit: int = Query(5)):
    """Get search suggestions"""
    try:
        search_result = await search_companies(q)
        search_data = search_result.get("data", {})
        results = search_data.get("results", [])
        
        suggestions = []
        for result in results[:limit]:
            suggestions.append({
                "text": result["name"],
                "ticker": result["ticker"],
                "type": "company"
            })
        
        if not suggestions:
            suggestions = [
                {"text": f"{q.title()} Inc", "ticker": "", "type": "suggestion"},
                {"text": f"{q.upper()}", "ticker": "", "type": "ticker"}
            ]
        
        return {
            "status": "success",
            "data": {"suggestions": suggestions[:limit]}
        }
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return {
            "status": "success",
            "data": {"suggestions": []}
        }

@app.get("/api/v1/company/lookup")
async def lookup_company(q: str = Query(...)):
    """Company lookup with comprehensive AI analysis and SEC filings"""
    try:
        logger.info(f"Company lookup: {q}")
        
        # Search for company
        search_response = await search_companies(q)
        search_data = search_response.get("data", {})
        results = search_data.get("results", [])
        
        if not results:
            raise HTTPException(status_code=404, detail="No company found")
        
        best_match = results[0]
        logger.info(f"Best match: {best_match['name']} ({best_match['ticker']}) CIK: {best_match.get('cik')}")
        
        # Get stock quote and SEC filings concurrently
        loop = asyncio.get_event_loop()
        stock_task = loop.run_in_executor(None, get_stock_quote_sync, best_match["ticker"])
        filings_task = get_sec_filings(best_match.get("cik", ""), limit=15)
        
        stock_quote, sec_filings = await asyncio.gather(
            stock_task, filings_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(stock_quote, Exception):
            logger.warning(f"Stock quote failed: {stock_quote}")
            stock_quote = None
        if isinstance(sec_filings, Exception):
            logger.warning(f"SEC filings failed: {sec_filings}")
            sec_filings = []
        
        # Generate comprehensive AI analysis
        company_data = {
            "name": best_match["name"],
            "ticker": best_match["ticker"],
            "cik": best_match.get("cik", ""),
            "exchange": best_match.get("exchange", "")
        }
        
        ai_analysis = await generate_comprehensive_ai_analysis(company_data, stock_quote, sec_filings)
        
        response_data = {
            "company": company_data,
            "stock_quote": stock_quote,
            "recent_filings": sec_filings,
            "investment_analysis": ai_analysis,
            "last_updated": datetime.utcnow().isoformat(),
            "data_sources": {
                "company_info": "SEC Database (prioritized) + Yahoo Finance",
                "stock_quote": "Yahoo Finance with fallback methods",
                "filings": "SEC EDGAR API",
                "ai_analysis": "Comprehensive Educational AI Analyzer"
            }
        }
        
        return {
            "status": "success",
            "message": f"Company information with comprehensive AI analysis retrieved for {best_match['name']}",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lookup error: {e}")
        raise HTTPException(status_code=500, detail=f"Lookup failed: {str(e)}")

@app.get("/api/v1/test/{query}")
async def test_search(query: str):
    """Test endpoint"""
    try:
        result = await search_companies(query)
        data = result.get("data", {})
        return {
            "query": query,
            "found": len(data.get("results", [])),
            "companies": data.get("results", [])[:3],
            "status": "working",
            "has_sec_integration": True,
            "has_comprehensive_ai": True
        }
    except Exception as e:
        return {"error": str(e), "query": query, "status": "failed"}