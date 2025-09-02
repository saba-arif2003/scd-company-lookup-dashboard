import os

# Load .env file manually
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')
    except FileNotFoundError:
        pass

# Load environment variables
load_env()

# Basic Settings
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

ALLOWED_HOSTS = [
    "localhost", 
    "127.0.0.1",
    "0.0.0.0"
]

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

# External APIs
SEC_EDGAR_BASE_URL = "https://data.sec.gov"
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "Company Lookup Dashboard/2.0 (sabaarif2003@gmail.com)")

# API Keys (replace with real keys for production)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
FMP_API_KEY = os.getenv("FMP_API_KEY", "demo")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "demo")

# Cache and timeouts
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Search settings - Updated for dynamic search
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "20"))  # Increased for better results
MIN_SEARCH_QUERY_LENGTH = 2
DEFAULT_FILINGS_LIMIT = 10
MAX_FILINGS_PER_REQUEST = 50

# API rate limiting settings
API_RATE_LIMITS = {
    "yahoo": 0.5,      # 0.5 seconds between requests
    "sec": 1.0,        # 1 second between requests
    "alpha_vantage": 12.0,  # Free tier: 5 requests per minute
    "fmp": 1.0,        # Free tier limitation
    "finnhub": 1.0,    # Free tier limitation
    "polygon": 1.0     # Free tier limitation
}

# Multiple data sources configuration
DATA_SOURCES = {
    "primary": ["yahoo", "sec"],           # Always try these first
    "secondary": ["fmp", "finnhub"],       # Try if primary sources don't have enough results
    "fallback": ["polygon", "alpha_vantage"]  # Last resort
}

# International exchange mappings
EXCHANGE_SUFFIXES = {
    "KS": "Karachi Stock Exchange (Pakistan)",
    "NS": "National Stock Exchange (India)", 
    "BO": "Bombay Stock Exchange (India)",
    "L": "London Stock Exchange",
    "TO": "Toronto Stock Exchange",
    "AX": "Australian Securities Exchange",
    "HK": "Hong Kong Stock Exchange",
    "SS": "Shanghai Stock Exchange",
    "SZ": "Shenzhen Stock Exchange"
}

# Company search patterns for better matching
SEARCH_PATTERNS = {
    "pakistan": {
        "banks": ["bank", "habib", "mcb", "ubl", "abl"],
        "companies": ["engro", "lucky", "cement", "oil", "gas"]
    },
    "india": {
        "tech": ["tcs", "infosys", "wipro", "tech mahindra"],
        "banks": ["hdfc", "icici", "sbi", "axis"]
    },
    "general": {
        "suffixes": ["limited", "ltd", "inc", "corporation", "corp", "company", "co"],
        "types": ["bank", "technology", "oil", "gas", "cement", "steel"]
    }
}

# App info
APP_NAME = "Company Lookup Dashboard"
API_V1_PREFIX = "/api/v1"
VERSION = "2.0.0"

# Feature flags
ENABLE_CACHING = True
ENABLE_RATE_LIMITING = True
ENABLE_INTERNATIONAL_SEARCH = True
ENABLE_ALTERNATIVE_EXCHANGES = True

# Create settings object for compatibility
class Settings:
    def __init__(self):
        for key, value in globals().items():
            if not key.startswith('_') and key.isupper():
                setattr(self, key, value)

settings = Settings()