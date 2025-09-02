# Company Lookup Dashboard - API Documentation

## Overview

The Company Lookup Dashboard API provides comprehensive access to company information, real-time stock data, and SEC filings. This REST API is built with FastAPI and follows OpenAPI 3.0 specifications.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: Currently, no authentication is required (public API)

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success|error|partial|warning",
  "message": "Human-readable message",
  "data": {
    // Response data (varies by endpoint)
  },
  "errors": [
    {
      "type": "validation_error|not_found|rate_limit_exceeded|external_api_error",
      "message": "Detailed error description",
      "code": "ERROR_CODE",
      "field": "field_name", // For validation errors
      "details": {} // Additional context
    }
  ],
  "metadata": {
    "response_time_ms": 250,
    "cached": false,
    "data_sources": {
      "company_info": "SEC EDGAR",
      "stock_quote": "Yahoo Finance"
    }
  },
  "timestamp": "2024-08-27T10:30:00Z",
  "request_id": "req_abc123xyz"
}
```

## Status Codes

- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `502` - Bad Gateway (external API error)
- `504` - Gateway Timeout

## Rate Limiting

- **Default Limits**: 60 requests per minute, 1000 requests per hour
- **Headers**: Rate limit information is included in response headers
- **Exceeded**: Returns HTTP 429 with retry information

## Health Check Endpoints

### GET /health
Comprehensive health check with dependency status.

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "timestamp": "2024-08-27T10:30:00Z",
    "version": "1.0.0",
    "uptime_seconds": 3600.5,
    "dependencies": {
      "sec_edgar_api": "healthy",
      "yahoo_finance": "healthy"
    },
    "system_metrics": {
      "memory_usage_mb": 256.7,
      "cpu_usage_percent": 15.3,
      "active_connections": 42
    },
    "environment": "production"
  }
}
```

### GET /health/simple
Simple health check for load balancers.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-08-27T10:30:00Z",
  "uptime": 3600.5
}
```

## Search Endpoints

### GET /search
Search for companies by name or ticker symbol.

**Parameters:**
- `q` (required): Search query (min 2 characters, max 100)
- `limit` (optional): Maximum results (default: 10, max: 20)

**Example Request:**
```
GET /search?q=tesla&limit=5
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "query": "tesla",
    "results": [
      {
        "name": "Tesla Inc.",
        "ticker": "TSLA",
        "cik": "0001318605",
        "exchange": "NASDAQ",
        "match_score": 0.95
      }
    ],
    "total_results": 1,
    "took_ms": 150,
    "suggestions": ["Tesla Motors", "TSLA"]
  }
}
```

### GET /search/suggestions
Get search suggestions for autocomplete.

**Parameters:**
- `q` (required): Partial search query (min 1 character)
- `limit` (optional): Maximum suggestions (default: 5, max: 10)

**Response:**
```json
{
  "status": "success",
  "data": {
    "suggestions": [
      {
        "text": "Tesla Inc.",
        "type": "company_name",
        "ticker": "TSLA",
        "match_score": 0.85
      },
      {
        "text": "TSLA",
        "type": "ticker",
        "company_name": "Tesla Inc.",
        "match_score": 0.95
      }
    ]
  }
}
```

### GET /search/validate
Validate a search query.

**Parameters:**
- `q` (required): Query to validate

**Response:**
```json
{
  "status": "success",
  "data": {
    "is_valid": true,
    "issues": [],
    "suggestions": [],
    "query_type": "ticker"
  }
}
```

## Company Endpoints

### GET /company/lookup
Get complete company information including stock data and filings.

**Parameters:**
- `q` (required): Company name or ticker symbol
- `include_stock` (optional): Include stock quote (default: true)
- `include_filings` (optional): Include SEC filings (default: true)
- `filings_limit` (optional): Number of filings to include (default: 5, max: 20)

**Example Request:**
```
GET /company/lookup?q=TSLA&include_stock=true&include_filings=true&filings_limit=10
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "company": {
      "name": "Tesla Inc.",
      "ticker": "TSLA",
      "cik": "0001318605",
      "exchange": "NASDAQ",
      "industry": "Auto Manufacturers",
      "sector": "Consumer Cyclical",
      "description": "Tesla, Inc. designs, develops, manufactures...",
      "website": "https://www.tesla.com",
      "headquarters": "Austin, Texas",
      "market_cap": 789000000000,
      "employees": 127855
    },
    "stock_quote": {
      "symbol": "TSLA",
      "price": 248.50,
      "currency": "USD",
      "change": -5.25,
      "change_percent": -2.07,
      "volume": 45234567,
      "market_cap": 789123456789,
      "last_updated": "2024-08-27T15:30:00Z",
      "market_state": "REGULAR"
    },
    "recent_filings": [
      {
        "form": "10-Q",
        "filing_date": "2024-07-24",
        "accession_number": "0001628280-24-027353",
        "filing_url": "https://www.sec.gov/Archives/edgar/data/1318605/...",
        "company_name": "Tesla Inc",
        "cik": "0001318605",
        "file_size": 1234567,
        "period_end_date": "2024-06-30",
        "description": "Quarterly report pursuant to Section 13 or 15(d)"
      }
    ],
    "last_updated": "2024-08-27T10:30:00Z",
    "data_sources": {
      "company_info": "Internal Database",
      "stock_quote": "Yahoo Finance",
      "filings": "SEC EDGAR"
    }
  }
}
```

### GET /company/{ticker}
Get basic company information by ticker symbol.

**Parameters:**
- `ticker` (path): Stock ticker symbol (1-5 uppercase letters)

**Response:**
```json
{
  "status": "success",
  "data": {
    "name": "Tesla Inc.",
    "ticker": "TSLA",
    "cik": "0001318605",
    "exchange": "NASDAQ",
    "industry": "Technology",
    "sector": "Technology"
  }
}
```

## Stock Endpoints

### GET /stock/{ticker}
Get stock quote for a ticker symbol.

**Parameters:**
- `ticker` (path): Stock ticker symbol
- `detailed` (optional): Return detailed stock data (default: false)

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "TSLA",
    "price": 248.50,
    "currency": "USD",
    "change": -5.25,
    "change_percent": -2.07,
    "volume": 45234567,
    "market_cap": 789123456789,
    "last_updated": "2024-08-27T15:30:00Z",
    "market_state": "REGULAR"
  }
}
```

**Detailed Response (detailed=true):**
```json
{
  "status": "success",
  "data": {
    "quote": {
      // Same as above
    },
    "open_price": 252.10,
    "high_price": 254.30,
    "low_price": 246.80,
    "previous_close": 253.75,
    "avg_volume": 89567234,
    "fifty_two_week_high": 414.50,
    "fifty_two_week_low": 138.80,
    "pe_ratio": 62.45,
    "eps": 3.98,
    "beta": 2.24
  }
}
```

### GET /stock/batch
Get stock quotes for multiple ticker symbols.

**Parameters:**
- `tickers` (required): List of ticker symbols (max 20)

**Example Request:**
```
GET /stock/batch?tickers=TSLA&tickers=AAPL&tickers=MSFT
```

**Response:**
```json
{
  "status": "partial",
  "data": {
    "quotes": {
      "TSLA": {
        "symbol": "TSLA",
        "price": 248.50,
        // ... other quote data
      },
      "AAPL": {
        "symbol": "AAPL",
        "price": 189.25,
        // ... other quote data
      },
      "MSFT": null // Failed to retrieve
    },
    "summary": {
      "total_requested": 3,
      "successful": 2,
      "failed": 1
    }
  }
}
```

## SEC Filings Endpoints

### GET /filings/{cik}
Get SEC filings for a company by CIK.

**Parameters:**
- `cik` (path): SEC Central Index Key (10 digits)
- `form_types` (optional): Filter by form types (comma-separated)
- `limit` (optional): Maximum filings to return (default: 10, max: 50)

**Example Request:**
```
GET /filings/0001318605?form_types=10-K,10-Q&limit=5
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "cik": "0001318605",
    "company_name": "Tesla Inc",
    "filings": [
      {
        "form": "10-Q",
        "filing_date": "2024-07-24",
        "accession_number": "0001628280-24-027353",
        "filing_url": "https://www.sec.gov/Archives/edgar/data/1318605/...",
        "company_name": "Tesla Inc",
        "cik": "0001318605",
        "file_size": 1234567,
        "document_count": 15,
        "period_end_date": "2024-06-30",
        "description": "Quarterly report pursuant to Section 13 or 15(d)",
        "is_xbrl": true,
        "is_inline_xbrl": true
      }
    ],
    "total_filings": 245,
    "filings_returned": 1,
    "date_range": {
      "earliest": "2010-01-29",
      "latest": "2024-07-24"
    },
    "last_updated": "2024-08-27T10:30:00Z"
  }
}
```

## Error Responses

### Validation Error (400/422)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "type": "validation_error",
      "message": "Invalid ticker symbol format",
      "code": "INVALID_TICKER",
      "field": "ticker",
      "details": {
        "provided": "tesla",
        "expected_format": "1-5 uppercase letters"
      }
    }
  ]
}
```

### Not Found Error (404)
```json
{
  "status": "error",
  "message": "Company not found for query: NONEXISTENT",
  "errors": [
    {
      "type": "not_found",
      "message": "No company found for query: NONEXISTENT",
      "code": "COMPANY_NOT_FOUND",
      "details": {
        "query": "NONEXISTENT"
      }
    }
  ]
}
```

### Rate Limit Error (429)
```json
{
  "status": "error",
  "message": "Rate limit exceeded: 60 requests per minute",
  "errors": [
    {
      "type": "rate_limit_exceeded",
      "message": "Rate limit exceeded. Try again in 45 seconds",
      "code": "RATE_LIMIT_EXCEEDED",
      "details": {
        "retry_after": 45
      }
    }
  ]
}
```

## Data Models

### Company Model
```json
{
  "name": "string",
  "ticker": "string (1-5 chars)",
  "cik": "string (10 digits)",
  "exchange": "string",
  "industry": "string",
  "sector": "string",
  "description": "string",
  "website": "string (URL)",
  "headquarters": "string",
  "market_cap": "number",
  "employees": "integer"
}
```

### Stock Quote Model
```json
{
  "symbol": "string",
  "price": "number",
  "currency": "string",
  "change": "number",
  "change_percent": "number",
  "volume": "integer",
  "market_cap": "number",
  "last_updated": "string (ISO datetime)",
  "market_state": "string (REGULAR|PRE|POST|CLOSED)"
}
```

### SEC Filing Model
```json
{
  "form": "string",
  "filing_date": "string (YYYY-MM-DD)",
  "accession_number": "string",
  "filing_url": "string (URL)",
  "company_name": "string",
  "cik": "string",
  "file_size": "integer",
  "document_count": "integer",
  "period_end_date": "string (YYYY-MM-DD)",
  "description": "string",
  "is_xbrl": "boolean",
  "is_inline_xbrl": "boolean"
}
```

## Interactive Documentation

For interactive API exploration, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- View detailed parameter information
- Test API calls directly in the browser
- Download the OpenAPI specification

## SDKs and Client Libraries

Currently, no official SDKs are provided, but the API follows REST conventions and can be easily integrated with any HTTP client library:

### Python Example
```python
import requests

# Search for a company
response = requests.get('http://localhost:8000/api/v1/search?q=tesla')
companies = response.json()['data']['results']

# Get detailed company information
response = requests.get('http://localhost:8000/api/v1/company/lookup?q=TSLA')
company_data = response.json()['data']
```

### JavaScript Example
```javascript
// Search for a company
const searchResponse = await fetch('http://localhost:8000/api/v1/search?q=tesla');
const companies = await searchResponse.json();

// Get stock quote
const stockResponse = await fetch('http://localhost:8000/api/v1/stock/TSLA');
const stockData = await stockResponse.json();
```

## Changelog

### v1.0.0 (Current)
- Initial API release
- Company search and lookup
- Stock quote integration
- SEC filings support
- Rate limiting and security features