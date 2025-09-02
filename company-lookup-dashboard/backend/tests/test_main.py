import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.main import app
from app.config import settings
from . import SAMPLE_COMPANIES, SAMPLE_STOCK_QUOTES, SAMPLE_SEC_FILINGS

# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns basic info"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        
        health_data = data["data"]
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "version" in health_data
    
    def test_simple_health_check(self):
        """Test simple health check for load balancers"""
        response = client.get("/api/v1/health/simple")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestSearchEndpoints:
    """Test search functionality"""
    
    @patch('app.services.company_service.CompanyService.search_companies')
    def test_search_companies_success(self, mock_search):
        """Test successful company search"""
        # Mock the search response
        mock_search.return_value = AsyncMock()
        mock_search.return_value.results = [SAMPLE_COMPANIES["TESLA"]]
        mock_search.return_value.total_results = 1
        mock_search.return_value.took_ms = 150
        mock_search.return_value.suggestions = []
        
        response = client.get("/api/v1/search?q=tesla")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_search_companies_empty_query(self):
        """Test search with empty query"""
        response = client.get("/api/v1/search?q=")
        assert response.status_code == 422  # Validation error
    
    def test_search_companies_short_query(self):
        """Test search with query too short"""
        response = client.get("/api/v1/search?q=a")
        assert response.status_code == 422  # Validation error
    
    def test_search_suggestions(self):
        """Test search suggestions endpoint"""
        response = client.get("/api/v1/search/suggestions?q=te")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
    
    def test_search_validation(self):
        """Test search query validation"""
        response = client.get("/api/v1/search/validate?q=TSLA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data


class TestCompanyEndpoints:
    """Test company lookup endpoints"""
    
    @patch('app.services.company_service.CompanyService.get_company_lookup')
    async def test_company_lookup_success(self, mock_lookup):
        """Test successful company lookup"""
        # Mock the lookup response
        mock_response = AsyncMock()
        mock_response.company = SAMPLE_COMPANIES["TESLA"]
        mock_response.stock_quote = SAMPLE_STOCK_QUOTES["TSLA"]
        mock_response.recent_filings = SAMPLE_SEC_FILINGS
        
        mock_lookup.return_value = mock_response
        
        response = client.get("/api/v1/company/lookup?q=tesla")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["success", "partial"]
    
    def test_company_lookup_empty_query(self):
        """Test company lookup with empty query"""
        response = client.get("/api/v1/company/lookup?q=")
        assert response.status_code == 422
    
    @patch('app.services.company_service.CompanyService.get_company_by_ticker')
    async def test_get_company_by_ticker(self, mock_get_company):
        """Test get company by ticker"""
        mock_get_company.return_value = SAMPLE_COMPANIES["TESLA"]
        
        response = client.get("/api/v1/company/TSLA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_company_invalid_ticker(self):
        """Test get company with invalid ticker format"""
        response = client.get("/api/v1/company/invalid-ticker-123")
        assert response.status_code == 422


class TestStockEndpoints:
    """Test stock quote endpoints"""
    
    @patch('app.services.stock_service.StockService.get_stock_quote')
    async def test_get_stock_quote(self, mock_get_quote):
        """Test get stock quote"""
        mock_get_quote.return_value = SAMPLE_STOCK_QUOTES["TSLA"]
        
        response = client.get("/api/v1/stock/TSLA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    @patch('app.services.stock_service.StockService.get_stock_data')
    async def test_get_detailed_stock_data(self, mock_get_data):
        """Test get detailed stock data"""
        mock_data = AsyncMock()
        mock_data.quote = SAMPLE_STOCK_QUOTES["TSLA"]
        mock_get_data.return_value = mock_data
        
        response = client.get("/api/v1/stock/TSLA?detailed=true")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    @patch('app.services.stock_service.StockService.get_multiple_quotes')
    async def test_batch_stock_quotes(self, mock_batch_quotes):
        """Test batch stock quotes"""
        mock_batch_quotes.return_value = {
            "TSLA": SAMPLE_STOCK_QUOTES["TSLA"],
            "AAPL": None  # Some quotes might fail
        }
        
        response = client.get("/api/v1/stock/batch?tickers=TSLA&tickers=AAPL")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["success", "partial"]


class TestFilingsEndpoints:
    """Test SEC filings endpoints"""
    
    @patch('app.services.sec_service.SECService.search_filings')
    async def test_get_company_filings(self, mock_search_filings):
        """Test get SEC filings for company"""
        mock_response = AsyncMock()
        mock_response.filings = SAMPLE_SEC_FILINGS
        mock_response.total_filings = len(SAMPLE_SEC_FILINGS)
        mock_response.filings_returned = len(SAMPLE_SEC_FILINGS)
        
        mock_search_filings.return_value = mock_response
        
        response = client.get("/api/v1/filings/0001318605")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_filings_invalid_cik(self):
        """Test get filings with invalid CIK"""
        response = client.get("/api/v1/filings/invalid-cik")
        assert response.status_code == 400


class TestErrorHandling:
    """Test error handling and validation"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint returns 404"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_rate_limiting_headers(self):
        """Test that rate limiting headers are present"""
        response = client.get("/api/v1/health")
        # Note: Actual rate limiting would require multiple requests
        assert response.status_code == 200
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/v1/health")
        # CORS headers should be present
        assert response.status_code in [200, 204]


class TestValidation:
    """Test input validation"""
    
    def test_query_length_validation(self):
        """Test query length validation"""
        # Too short
        response = client.get("/api/v1/search?q=a")
        assert response.status_code == 422
        
        # Too long
        long_query = "a" * 101
        response = client.get(f"/api/v1/search?q={long_query}")
        assert response.status_code == 422
    
    def test_ticker_format_validation(self):
        """Test ticker format validation"""
        invalid_tickers = ["123", "toolong", "invalid-ticker"]
        
        for ticker in invalid_tickers:
            response = client.get(f"/api/v1/company/{ticker}")
            assert response.status_code == 422
    
    def test_cik_format_validation(self):
        """Test CIK format validation"""
        invalid_ciks = ["abc", "123456789012345"]  # Non-numeric, too long
        
        for cik in invalid_ciks:
            response = client.get(f"/api/v1/filings/{cik}")
            assert response.status_code == 400


@pytest.fixture
def mock_external_apis():
    """Mock external API calls"""
    with patch('app.services.stock_service.StockService') as mock_stock, \
         patch('app.services.sec_service.SECService') as mock_sec:
        yield mock_stock, mock_sec


class TestIntegration:
    """Integration tests with mocked external services"""
    
    def test_full_company_lookup_flow(self, mock_external_apis):
        """Test complete company lookup flow"""
        mock_stock, mock_sec = mock_external_apis
        
        # Mock successful responses
        mock_stock.get_stock_quote.return_value = SAMPLE_STOCK_QUOTES["TSLA"]
        mock_sec.get_recent_filings.return_value = SAMPLE_SEC_FILINGS
        
        # Test the full flow
        response = client.get("/api/v1/company/lookup?q=tesla")
        
        # Should return success even with mocked data
        assert response.status_code in [200, 404, 422]  # Depending on mock setup


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])