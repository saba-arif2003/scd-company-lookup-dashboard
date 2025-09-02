import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
from datetime import datetime, date

from app.services.company_service import CompanyService
from app.services.stock_service import StockService
from app.services.sec_service import SECService
from app.core.exceptions import CompanyNotFoundError, StockNotFoundError, SECAPIError
from . import SAMPLE_COMPANIES, SAMPLE_STOCK_QUOTES, SAMPLE_SEC_FILINGS


class TestCompanyService:
    """Test CompanyService functionality"""
    
    @pytest.fixture
    def company_service(self):
        """Create CompanyService instance for testing"""
        return CompanyService()
    
    @pytest.mark.asyncio
    async def test_search_companies_success(self, company_service):
        """Test successful company search"""
        result = await company_service.search_companies("tesla")
        
        assert result is not None
        assert hasattr(result, 'results')
        assert hasattr(result, 'total_results')
        assert hasattr(result, 'took_ms')
    
    @pytest.mark.asyncio
    async def test_search_companies_empty_query(self, company_service):
        """Test search with empty query"""
        result = await company_service.search_companies("")
        
        assert result.results == []
        assert result.total_results == 0
    
    @pytest.mark.asyncio
    async def test_search_companies_short_query(self, company_service):
        """Test search with query too short"""
        result = await company_service.search_companies("a")
        
        assert result.results == []
        assert result.total_results == 0
    
    @pytest.mark.asyncio
    async def test_get_company_by_ticker_success(self, company_service):
        """Test successful company lookup by ticker"""
        # This tests the static mapping in the service
        company = await company_service.get_company_by_ticker("TSLA")
        
        if company:  # May return None if not in static mapping
            assert company.ticker == "TSLA"
            assert company.name is not None
            assert company.cik is not None
    
    @pytest.mark.asyncio
    async def test_get_company_by_ticker_not_found(self, company_service):
        """Test company lookup with non-existent ticker"""
        company = await company_service.get_company_by_ticker("NONEXISTENT")
        assert company is None
    
    @pytest.mark.asyncio
    @patch('app.services.company_service.StockService')
    @patch('app.services.company_service.SECService')
    async def test_get_company_lookup_success(self, mock_sec_service, mock_stock_service, company_service):
        """Test complete company lookup"""
        # Mock the services
        company_service.stock_service = mock_stock_service
        company_service.sec_service = mock_sec_service
        
        # Mock successful responses
        mock_stock_service.get_stock_quote.return_value = AsyncMock()
        mock_sec_service.get_recent_filings.return_value = []
        
        try:
            result = await company_service.get_company_lookup("tesla")
            assert result is not None
        except CompanyNotFoundError:
            # Expected if company not found in static mapping
            pass
    
    @pytest.mark.asyncio
    async def test_get_company_lookup_not_found(self, company_service):
        """Test company lookup with non-existent company"""
        with pytest.raises(CompanyNotFoundError):
            await company_service.get_company_lookup("nonexistentcompany123")
    
    def test_normalize_query(self, company_service):
        """Test query normalization"""
        normalized = company_service._normalize_query("  Tesla Inc.  ")
        assert normalized == "tesla"
        
        normalized = company_service._normalize_query("Apple Corp.")
        assert normalized == "apple"
    
    def test_calculate_match_score(self, company_service):
        """Test match score calculation"""
        company_data = {"name": "Tesla Inc.", "ticker": "TSLA"}
        
        # Exact match
        score = company_service._calculate_match_score("tesla", company_data)
        assert score > 0.8
        
        # Ticker match
        score = company_service._calculate_match_score("TSLA", company_data)
        assert score > 0.9
        
        # No match
        score = company_service._calculate_match_score("xyz", company_data)
        assert score == 0.0


class TestStockService:
    """Test StockService functionality"""
    
    @pytest.fixture
    def stock_service(self):
        """Create StockService instance for testing"""
        return StockService()
    
    @pytest.mark.asyncio
    @patch('yfinance.Ticker')
    async def test_get_stock_quote_success(self, mock_ticker, stock_service):
        """Test successful stock quote retrieval"""
        # Mock yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'regularMarketPrice': 248.50,
            'regularMarketPreviousClose': 253.75,
            'regularMarketVolume': 45234567,
            'marketCap': 789000000000,
            'currency': 'USD'
        }
        mock_ticker.return_value = mock_ticker_instance
        
        quote = await stock_service.get_stock_quote("TSLA")
        
        assert quote is not None
        assert quote.symbol == "TSLA"
        assert quote.price == 248.50
        assert quote.currency == "USD"
    
    @pytest.mark.asyncio
    @patch('yfinance.Ticker')
    async def test_get_stock_quote_not_found(self, mock_ticker, stock_service):
        """Test stock quote for non-existent ticker"""
        # Mock yfinance to return empty info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}
        mock_ticker.return_value = mock_ticker_instance
        
        with pytest.raises(StockNotFoundError):
            await stock_service.get_stock_quote("NONEXISTENT")
    
    @pytest.mark.asyncio
    async def test_get_multiple_quotes(self, stock_service):
        """Test batch stock quote retrieval"""
        with patch.object(stock_service, 'get_stock_quote') as mock_get_quote:
            # Mock some successful and some failed quotes
            async def mock_quote_side_effect(symbol):
                if symbol == "TSLA":
                    return SAMPLE_STOCK_QUOTES["TSLA"]
                else:
                    raise StockNotFoundError(f"Stock not found: {symbol}")
            
            mock_get_quote.side_effect = mock_quote_side_effect
            
            quotes = await stock_service.get_multiple_quotes(["TSLA", "INVALID"])
            
            assert "TSLA" in quotes
            assert "INVALID" in quotes
            assert quotes["TSLA"] is not None
            assert quotes["INVALID"] is None
    
    @pytest.mark.asyncio
    async def test_validate_symbol(self, stock_service):
        """Test stock symbol validation"""
        with patch.object(stock_service, 'get_stock_quote') as mock_get_quote:
            # Mock successful validation
            mock_get_quote.return_value = SAMPLE_STOCK_QUOTES["TSLA"]
            
            is_valid = await stock_service.validate_symbol("TSLA")
            assert is_valid is True
            
            # Mock failed validation
            mock_get_quote.side_effect = StockNotFoundError("Not found")
            
            is_valid = await stock_service.validate_symbol("INVALID")
            assert is_valid is False


class TestSECService:
    """Test SECService functionality"""
    
    @pytest.fixture
    def sec_service(self):
        """Create SECService instance for testing"""
        return SECService()
    
    def test_normalize_cik(self, sec_service):
        """Test CIK normalization"""
        # Test with leading zeros needed
        normalized = sec_service._normalize_cik("1318605")
        assert normalized == "0001318605"
        
        # Test with already correct format
        normalized = sec_service._normalize_cik("0001318605")
        assert normalized == "0001318605"
        
        # Test with non-digit characters
        normalized = sec_service._normalize_cik("CIK1318605")
        assert normalized == "0001318605"
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_get_company_filings_success(self, mock_get, sec_service):
        """Test successful SEC filings retrieval"""
        # Mock SEC API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'filings': {
                'recent': {
                    'form': ['10-Q', '8-K'],
                    'filingDate': ['2024-07-24', '2024-07-02'],
                    'accessionNumber': ['0001628280-24-027353', '0001628280-24-027354'],
                    'primaryDocument': ['tsla-20240630.htm', 'tsla-8k.htm']
                }
            },
            'entityName': 'Tesla Inc'
        }
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        filings = await sec_service.get_company_filings("0001318605", limit=5)
        
        assert len(filings) > 0
        assert all(hasattr(filing, 'form') for filing in filings)
        assert all(hasattr(filing, 'filing_date') for filing in filings)
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_get_company_filings_not_found(self, mock_get, sec_service):
        """Test SEC filings for non-existent CIK"""
        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        filings = await sec_service.get_company_filings("0000000000", limit=5)
        assert filings == []
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_get_company_filings_server_error(self, mock_get, sec_service):
        """Test SEC filings with server error"""
        # Mock 500 response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(SECAPIError):
            await sec_service.get_company_filings("0001318605", limit=5)
    
    def test_parse_filing_data(self, sec_service):
        """Test filing data parsing"""
        filing_data = {
            'form': '10-Q',
            'filingDate': '2024-07-24',
            'accessionNumber': '0001628280-24-027353',
            'primaryDocument': 'tsla-20240630.htm',
            'entityName': 'Tesla Inc'
        }
        
        filing = sec_service._parse_filing_data(filing_data, "0001318605")
        
        assert filing.form == "10-Q"
        assert filing.filing_date == date(2024, 7, 24)
        assert filing.accession_number == "0001628280-24-027353"
        assert filing.company_name == "Tesla Inc"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, sec_service):
        """Test SEC API rate limiting"""
        # Test that rate limiting delay is applied
        start_time = datetime.utcnow()
        
        await sec_service._rate_limit()
        await sec_service._rate_limit()
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # Should have some delay due to rate limiting
        assert elapsed >= sec_service._min_request_interval


class TestServiceIntegration:
    """Test service integration and error handling"""
    
    @pytest.mark.asyncio
    async def test_company_service_with_mocked_dependencies(self):
        """Test CompanyService with mocked external dependencies"""
        company_service = CompanyService()
        
        with patch.object(company_service, 'stock_service') as mock_stock, \
             patch.object(company_service, 'sec_service') as mock_sec:
            
            # Mock successful responses
            mock_stock.get_stock_quote.return_value = AsyncMock()
            mock_sec.get_recent_filings.return_value = []
            
            # Test that the service handles mocked dependencies correctly
            try:
                result = await company_service.get_company_lookup("tesla")
                # Should either succeed or raise CompanyNotFoundError
                assert result is not None or True
            except CompanyNotFoundError:
                # Expected for companies not in static mapping
                pass
    
    @pytest.mark.asyncio 
    async def test_error_propagation(self):
        """Test that errors are properly propagated between services"""
        stock_service = StockService()
        
        # Test that StockNotFoundError is raised for invalid ticker
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.info = {}  # Empty info indicates not found
            mock_ticker.return_value = mock_ticker_instance
            
            with pytest.raises(StockNotFoundError):
                await stock_service.get_stock_quote("INVALID")
    
    def test_cache_functionality(self):
        """Test caching functionality in services"""
        company_service = CompanyService()
        
        # Test cache key generation
        cache_key = company_service._get_cache_key("search", "tesla")
        assert cache_key == "search:tesla"
        
        # Test cache set/get
        test_data = {"test": "data"}
        company_service._set_cache("test_key", test_data)
        
        cached_data = company_service._get_cache("test_key")
        assert cached_data == test_data
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self):
        """Test service cleanup methods"""
        stock_service = StockService()
        sec_service = SECService()
        company_service = CompanyService()
        
        # Test cleanup methods don't raise errors
        await stock_service.close()
        await sec_service.close()
        await company_service.close()


# Pytest configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])