# Company Lookup Dashboard - Backend API

A professional FastAPI backend service that provides comprehensive company intelligence, real-time stock data, and SEC filings information.

## 🚀 Features

- **Company Search**: Intelligent fuzzy search with autocomplete suggestions
- **Stock Data**: Real-time stock quotes via Yahoo Finance API
- **SEC Filings**: Complete SEC EDGAR filings database integration
- **Rate Limiting**: Built-in rate limiting and security features
- **Caching**: In-memory caching for improved performance
- **Error Handling**: Comprehensive error handling with detailed responses
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Health Monitoring**: Health check endpoints with dependency status

## 📋 Requirements

- Python 3.9+
- FastAPI 0.104+
- aiohttp for async HTTP requests
- yfinance for stock data
- pydantic for data validation
- uvicorn as ASGI server

## 🛠 Installation

### Option 1: Local Development

```bash
# Clone the repository
git clone <repository-url>
cd company-lookup-dashboard/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker

```bash
# Build and run with Docker
docker build -t company-dashboard-api .
docker run -p 8000:8000 company-dashboard-api

# Or use Docker Compose
docker-compose up --build
```

## ⚙️ Configuration

Create a `.env` file in the backend directory:

```bash
# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# SEC API Settings (REQUIRED)
SEC_USER_AGENT="Your App Name/1.0 (your-email@example.com)"

# Cache Settings
CACHE_TTL_SECONDS=300

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000"]
```

**Important**: Update the `SEC_USER_AGENT` with your email address as required by the SEC API.

## 📖 API Documentation

Once the server is running, visit:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔌 API Endpoints

### Health Checks
- `GET /health` - Comprehensive health check
- `GET /health/simple` - Simple health check for load balancers
- `GET /health/dependencies` - Check external service status

### Company Search
- `GET /search?q={query}` - Search companies by name or ticker
- `GET /search/suggestions?q={query}` - Get search suggestions
- `GET /search/validate?q={query}` - Validate search query

### Company Information
- `GET /company/lookup?q={query}` - Complete company lookup
- `GET /company/{ticker}` - Get company by ticker symbol

### Stock Data
- `GET /stock/{ticker}` - Get stock quote
- `GET /stock/{ticker}?detailed=true` - Get detailed stock data
- `GET /stock/batch?tickers={tickers}` - Get multiple stock quotes

### SEC Filings
- `GET /filings/{cik}` - Get company SEC filings
- `GET /filings/{cik}?form_types=10-K,10-Q` - Filter by form types

## 📊 Response Format

All API responses follow a consistent format:

```json
{
  "status": "success|error|partial",
  "message": "Human-readable message",
  "data": {
    // Response data
  },
  "metadata": {
    "response_time_ms": 250,
    "cached": false
  },
  "request_id": "req_abc123"
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py -v

# Run specific test
pytest tests/test_main.py::TestHealthEndpoints::test_health_check -v
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── company.py       # Company models
│   │   ├── stock.py         # Stock models
│   │   └── filing.py        # SEC filing models
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── company_service.py
│   │   ├── stock_service.py
│   │   └── sec_service.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── search.py
│   │       └── company.py
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── exceptions.py    # Exception handling
│   │   └── security.py      # Security & validation
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_main.py
│   └── test_services.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔒 Security Features

- **Rate Limiting**: Configurable per-minute and per-hour limits
- **Input Validation**: Comprehensive input sanitization and validation
- **CORS Protection**: Configurable CORS policies
- **Request Logging**: All requests are logged with unique IDs
- **Error Handling**: Secure error messages without sensitive data exposure

## 📈 Performance

- **Async/Await**: Fully asynchronous for high concurrency
- **Caching**: In-memory caching with configurable TTL
- **Connection Pooling**: Efficient HTTP client connection management
- **Response Streaming**: Large data sets are streamed efficiently

## 🐛 Debugging

Enable debug mode in your `.env` file:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

This enables:
- Detailed error messages
- Request/response logging
- Interactive API documentation
- Hot reload for development

## 📦 Dependencies

### Core Dependencies
- `fastapi` - Modern Python web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation and serialization
- `aiohttp` - Async HTTP client

### Data Sources
- `yfinance` - Yahoo Finance stock data
- SEC EDGAR API - SEC filings (direct HTTP calls)

### Development
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Code linting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format code (`black app tests`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please:
1. Check the [API Documentation](http://localhost:8000/docs)
2. Review the test cases for usage examples
3. Open an issue on GitHub
4. Contact the development team

## 🚀 Deployment

See [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for detailed deployment instructions for various platforms including:
- Docker containers
- Cloud platforms (AWS, GCP, Azure)
- Traditional servers
- Kubernetes clusters