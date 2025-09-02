"""
Test suite for Company Lookup Dashboard API

This package contains comprehensive tests for all API endpoints, services, and utilities.
"""

import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_API_BASE_URL = "http://testserver"

# Common test data
SAMPLE_COMPANIES = {
    "TESLA": {
        "name": "Tesla Inc.",
        "ticker": "TSLA", 
        "cik": "0001318605",
        "exchange": "NASDAQ"
    },
    "APPLE": {
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "cik": "0000320193", 
        "exchange": "NASDAQ"
    },
    "MICROSOFT": {
        "name": "Microsoft Corporation",
        "ticker": "MSFT",
        "cik": "0000789019",
        "exchange": "NASDAQ"
    }
}

SAMPLE_STOCK_QUOTES = {
    "TSLA": {
        "symbol": "TSLA",
        "price": 248.50,
        "currency": "USD",
        "change": -5.25,
        "change_percent": -2.07,
        "volume": 45234567
    }
}

SAMPLE_SEC_FILINGS = [
    {
        "form": "10-Q",
        "filing_date": "2024-07-24",
        "accession_number": "0001628280-24-027353",
        "filing_url": "https://www.sec.gov/Archives/edgar/data/1318605/000162828024027353/tsla-20240630.htm"
    }
]