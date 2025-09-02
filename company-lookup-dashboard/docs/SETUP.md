# Company Lookup Dashboard - Setup Instructions

This guide will help you set up the Company Lookup Dashboard on your local machine or server.

## 🏗️ System Requirements

### Minimum Requirements
- **Operating System**: Linux, macOS, or Windows 10+
- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Network**: Internet connection for external APIs

### Recommended Development Environment
- **OS**: Ubuntu 22.04 LTS, macOS Monterey+, or Windows 11
- **Python**: 3.11+
- **Node.js**: 18 LTS
- **Editor**: VS Code with Python and JavaScript extensions
- **Docker**: Latest version (optional but recommended)

## 📦 Prerequisites

### Install Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS (using Homebrew)
brew install python@3.11

# Windows
# Download from https://python.org and install
```

### Install Node.js
```bash
# Ubuntu/Debian (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS (using Homebrew)
brew install node@18

# Windows
# Download from https://nodejs.org and install
```

### Install Git
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
xcode-select --install

# Windows
# Download from https://git-scm.com
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd company-lookup-dashboard
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit environment variables (IMPORTANT!)
nano .env  # or use your preferred editor
```

**⚠️ Important**: Update the `.env` file with your email address:
```bash
SEC_USER_AGENT="Company Lookup Dashboard/1.0 (your-email@example.com)"
```

### 3. Frontend Setup
```bash
# Open new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit environment variables if needed
nano .env
```

### 4. Start the Application
```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate  # If not already activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

### 5. Verify Installation
- **Backend**: Visit http://localhost:8000/docs
- **Frontend**: Visit http://localhost:3000
- **Health Check**: http://localhost:8000/api/v1/health

## 🐳 Docker Setup (Alternative)

If you prefer using Docker:

### Prerequisites
```bash
# Install Docker and Docker Compose
# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop from docker.com
```

### Run with Docker Compose
```bash
# Clone repository
git clone <repository-url>
cd company-lookup-dashboard

# Copy and edit environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your email:
# SEC_USER_AGENT="Your App/1.0 (your-email@example.com)"

# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Docker Commands
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose build --no-cache

# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh
```

## ⚙️ Environment Configuration

### Backend Configuration (.env)
```bash
# Application Settings
DEBUG=true                    # Enable debug mode for development
HOST=0.0.0.0                 # Host to bind to
PORT=8000                    # Port to run on
LOG_LEVEL=INFO               # Logging level

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60     # Requests per minute per IP
RATE_LIMIT_PER_HOUR=1000     # Requests per hour per IP

# Cache Settings
CACHE_TTL_SECONDS=300        # Cache time-to-live in seconds

# Security
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
ALLOWED_HOSTS=["localhost","127.0.0.1","0.0.0.0"]

# SEC API (REQUIRED - Replace with your email)
SEC_USER_AGENT="Company Lookup Dashboard/1.0 (your-email@example.com)"

# External APIs
YAHOO_FINANCE_TIMEOUT=10     # Timeout for Yahoo Finance requests
REQUEST_TIMEOUT=30           # General request timeout

# Search Settings
MAX_SEARCH_RESULTS=10        # Maximum search results to return
MIN_SEARCH_QUERY_LENGTH=2    # Minimum query length
DEFAULT_