# Company Lookup Dashboard

A professional web application for company intelligence, real-time stock data, and SEC filings analysis. Built with FastAPI (backend) and React (frontend).

![Company Lookup Dashboard](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

### 🏢 Company Intelligence
- **Smart Search**: Intelligent fuzzy search with autocomplete suggestions
- **Company Profiles**: Comprehensive company information and metrics
- **Business Intelligence**: Industry, sector, and competitive analysis

### 📈 Real-Time Stock Data
- **Live Stock Quotes**: Real-time price data via Yahoo Finance
- **Market Analysis**: Price changes, volume, market cap, and trends
- **Extended Metrics**: P/E ratios, 52-week ranges, and financial ratios
- **Batch Quotes**: Multiple stock quotes in a single request

### 📋 SEC Filings
- **Complete EDGAR Integration**: Access to all SEC filings
- **Filing Analysis**: 10-K, 10-Q, 8-K, and other regulatory documents
- **Search & Filter**: Advanced filtering by form type and date range
- **Direct Links**: One-click access to official SEC documents

### 🛡️ Enterprise Features
- **Rate Limiting**: Configurable API rate limiting
- **Caching**: Intelligent caching for improved performance  
- **Error Handling**: Comprehensive error handling and recovery
- **Health Monitoring**: Built-in health checks and system monitoring
- **Security**: Input validation, CORS protection, and secure headers

## 🏗️ Architecture

```
company-lookup-dashboard/
├── 📁 backend/                 # Python FastAPI
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── models/            # Pydantic data models
│   │   ├── services/          # Business logic
│   │   ├── api/routes/        # API endpoints
│   │   ├── core/              # Core functionality
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
├── 📁 frontend/               # React + Tailwind CSS
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   ├── hooks/             # Custom React hooks
│   │   └── utils/             # Utility functions
│   └── package.json           # Node.js dependencies
├── 📁 docs/                   # Documentation
└── 📁 scripts/               # Deployment scripts
```

## ⚡ Quick Start

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- Docker (optional)

### 🚀 Automated Setup
```bash
# Clone the repository
git clone <repository-url>
cd company-lookup-dashboard

# Run the automated setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 🐳 Docker Setup (Recommended)
```bash
# Clone and start with Docker Compose
git clone <repository-url>
cd company-lookup-dashboard

# Copy and edit environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# IMPORTANT: Edit backend/.env with your email
# SEC_USER_AGENT="Your App Name/1.0 (your-email@example.com)"

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 🔧 Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration (especially SEC_USER_AGENT)

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm run dev
```

## 🌐 API Documentation

Once the backend is running, comprehensive API documentation is available at:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v1/health` | GET | System health check |
| `/api/v1/search?q={query}` | GET | Search companies |
| `/api/v1/company/lookup?q={query}` | GET | Complete company data |
| `/api/v1/stock/{ticker}` | GET | Stock quote |
| `/api/v1/filings/{cik}` | GET | SEC filings |

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Tests
```bash
# Run full test suite
./scripts/test.sh
```

## 🚀 Deployment

### Production Deployment
```bash
# Deploy to production
./scripts/deploy.sh production --tag v1.0.0

# Deploy to staging
./scripts/deploy.sh staging
```

### Cloud Deployment

The application supports deployment to:
- **Docker** (recommended)
- **AWS** (ECS, Elastic Beanstalk)
- **Google Cloud** (Cloud Run, GKE) 
- **Azure** (Container Instances, AKS)
- **Traditional servers** (Ubuntu, CentOS)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guides.

## 📊 Performance

### Benchmarks
- **API Response Time**: < 200ms average
- **Search Performance**: < 100ms for company search
- **Concurrent Users**: 500+ supported
- **Uptime**: 99.9% target

### Optimization Features
- Intelligent caching with configurable TTL
- Connection pooling for external APIs
- Async/await for high concurrency
- CDN support for static assets
- Database query optimization

## 🔒 Security

### Security Features
- Rate limiting (60 req/min, 1000 req/hour by default)
- Input validation and sanitization
- CORS protection with configurable origins
- Secure HTTP headers
- Request logging and monitoring

### Security Best Practices
- All user inputs are validated and sanitized
- Environment variables for sensitive configuration
- HTTPS enforced in production
- Regular security updates and monitoring

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest` and `npm test`)
6. Format code (`black` for Python, `prettier` for JavaScript)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Style
- **Python**: Black formatter, flake8 linting, type hints
- **JavaScript**: Prettier formatter, ESLint, modern ES6+ syntax
- **Documentation**: Comprehensive docstrings and comments

## 📋 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000

# SEC API (REQUIRED)
SEC_USER_AGENT="Your App Name/1.0 (your-email@example.com)"

# Performance
CACHE_TTL_SECONDS=300
RATE_LIMIT_PER_MINUTE=60

# Security
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENV=development
```

## 🐛 Troubleshooting

### Common Issues

**"SEC API returns 403 Forbidden"**
- Ensure `SEC_USER_AGENT` in backend/.env includes your email address
- SEC requires proper User-Agent header with contact information

**"Module not found" errors**
- Backend: Ensure virtual environment is activated
- Frontend: Run `npm install` to install dependencies

**"Port already in use"**
- Backend: Change port in .env or kill process using port 8000
- Frontend: Vite will automatically try port 3001 if 3000 is busy

See [docs/SETUP.md](docs/SETUP.md) for comprehensive troubleshooting.

## 📚 Documentation

- [📖 API Documentation](docs/API.md) - Complete API reference
- [🛠️ Setup Guide](docs/SETUP.md) - Detailed setup instructions  
- [🚀 Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [🧪 Testing Guide](docs/TESTING.md) - Testing methodology

## 🛣️ Roadmap

### Version 1.1
- [ ] Advanced charting and visualization
- [ ] Portfolio tracking and watchlists
- [ ] Email alerts and notifications
- [ ] Advanced filtering and search options

### Version 1.2  
- [ ] AI-powered financial analysis
- [ ] Comparison tools and benchmarking
- [ ] Historical data analysis
- [ ] Mobile app (React Native)

### Version 2.0
- [ ] Multi-language support
- [ ] White-label solutions
- [ ] Advanced analytics dashboard
- [ ] Machine learning predictions

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/your-username/company-lookup-dashboard?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/company-lookup-dashboard?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/company-lookup-dashboard)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-username/company-lookup-dashboard)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SEC EDGAR API** for providing comprehensive filing data
- **Yahoo Finance** for real-time stock market data
- **FastAPI** team for the excellent Python web framework
- **React** team for the powerful frontend library
- **Tailwind CSS** for the utility-first CSS framework



## ⭐ Show Your Support

Give a ⭐️ if this project helped you!