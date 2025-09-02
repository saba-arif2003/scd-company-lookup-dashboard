// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

// API Endpoints
export const API_ENDPOINTS = {
  // Health endpoints
  HEALTH: '/health',
  HEALTH_SIMPLE: '/health/simple',
  HEALTH_DEPENDENCIES: '/health/dependencies',
  
  // Search endpoints
  SEARCH: '/search',
  SEARCH_SUGGESTIONS: '/search/suggestions',
  SEARCH_VALIDATE: '/search/validate',
  
  // Company endpoints
  COMPANY_LOOKUP: '/company/lookup',
  COMPANY_BY_TICKER: '/company',
  
  // Stock endpoints
  STOCK_QUOTE: '/stock',
  STOCK_BATCH: '/stock/batch',
  
  // SEC filings endpoints
  FILINGS: '/filings',
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
};

// API Response Status
export const API_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  PARTIAL: 'partial',
};

// Error Types
export const ERROR_TYPES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  API_ERROR: 'API_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  RATE_LIMIT: 'RATE_LIMIT',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

// Cache Configuration
export const CACHE_CONFIG = {
  DEFAULT_TTL: 5 * 60 * 1000, // 5 minutes
  SEARCH_TTL: 2 * 60 * 1000, // 2 minutes
  COMPANY_TTL: 10 * 60 * 1000, // 10 minutes
  STOCK_TTL: 1 * 60 * 1000, // 1 minute
  FILINGS_TTL: 30 * 60 * 1000, // 30 minutes
};

// Request Headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Stock Market Status
export const MARKET_STATUS = {
  REGULAR: 'REGULAR',
  CLOSED: 'CLOSED',
  PRE: 'PRE',
  POST: 'POST',
  UNKNOWN: 'UNKNOWN',
};

// Filing Form Types
export const FILING_FORMS = {
  '10-K': {
    name: 'Annual Report',
    description: 'Annual report with comprehensive business information',
    color: 'primary',
  },
  '10-Q': {
    name: 'Quarterly Report',
    description: 'Quarterly financial report',
    color: 'blue',
  },
  '8-K': {
    name: 'Current Report',
    description: 'Report of major events or corporate changes',
    color: 'green',
  },
  'DEF 14A': {
    name: 'Proxy Statement',
    description: 'Information for shareholder voting',
    color: 'purple',
  },
  'S-1': {
    name: 'Registration Statement',
    description: 'Registration of new securities',
    color: 'orange',
  },
  '4': {
    name: 'Insider Trading',
    description: 'Statement of changes in beneficial ownership',
    color: 'red',
  },
};

// Search Configuration
export const SEARCH_CONFIG = {
  MIN_QUERY_LENGTH: 2,
  MAX_QUERY_LENGTH: 100,
  DEBOUNCE_DELAY: 300, // milliseconds
  MAX_SUGGESTIONS: 5,
  MAX_RESULTS: 10,
};

// UI Configuration
export const UI_CONFIG = {
  TOAST_DURATION: 5000, // 5 seconds
  LOADING_DELAY: 500, // Show loading after 500ms
  ANIMATION_DURATION: 200, // milliseconds
  MOBILE_BREAKPOINT: 768, // pixels
};

// Local Storage Keys
export const STORAGE_KEYS = {
  RECENT_SEARCHES: 'company_lookup_recent_searches',
  USER_PREFERENCES: 'company_lookup_user_preferences',
  CACHE_PREFIX: 'company_lookup_cache_',
};

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'MMM dd, yyyy',
  ISO: 'yyyy-MM-dd',
  LONG: 'MMMM dd, yyyy',
  SHORT: 'MM/dd/yyyy',
  TIME: 'HH:mm:ss',
  DATETIME: 'MMM dd, yyyy HH:mm',
};

// Color Schemes
export const COLORS = {
  PRIMARY: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  SUCCESS: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  DANGER: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
};

// Feature Flags
export const FEATURES = {
  ENABLE_DARK_MODE: process.env.REACT_APP_ENABLE_DARK_MODE === 'true',
  ENABLE_CHARTS: process.env.REACT_APP_ENABLE_CHARTS !== 'false',
  ENABLE_EXPORT: process.env.REACT_APP_ENABLE_EXPORT !== 'false',
  ENABLE_FAVORITES: process.env.REACT_APP_ENABLE_FAVORITES !== 'false',
  DEBUG_MODE: process.env.NODE_ENV === 'development',
};

// Application Metadata
export const APP_INFO = {
  NAME: 'Company Lookup Dashboard',
  VERSION: process.env.REACT_APP_VERSION || '1.0.0',
  DESCRIPTION: 'Professional dashboard for company information, stock prices, and SEC filings',
  AUTHOR: 'Company Lookup Team',
  CONTACT_EMAIL: 'support@companylookup.com',
  GITHUB_URL: 'https://github.com/company-lookup/dashboard',
};