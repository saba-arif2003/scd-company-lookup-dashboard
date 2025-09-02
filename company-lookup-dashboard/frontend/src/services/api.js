import axios from 'axios';
import { 
  API_CONFIG, 
  API_ENDPOINTS, 
  HTTP_STATUS, 
  ERROR_TYPES,
  DEFAULT_HEADERS,
  CACHE_CONFIG,
  STORAGE_KEYS 
} from './constants';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: DEFAULT_HEADERS,
});

// In-memory cache for API responses
const cache = new Map();

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp to requests
    config.metadata = { startTime: new Date() };
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = generateRequestId();
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      data: config.data,
    });
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime;
    
    console.log(`✅ API Response: ${response.status} ${response.config.url}`, {
      duration: `${duration}ms`,
      data: response.data,
    });
    
    return response;
  },
  (error) => {
    const duration = error.config?.metadata ? 
      new Date() - error.config.metadata.startTime : 0;
    
    console.error(`❌ API Error: ${error.response?.status || 'Network'} ${error.config?.url}`, {
      duration: `${duration}ms`,
      message: error.message,
      response: error.response?.data,
    });
    
    return Promise.reject(transformError(error));
  }
);

// Utility Functions
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function getCacheKey(url, params = {}) {
  const paramString = Object.keys(params)
    .sort()
    .map(key => `${key}=${params[key]}`)
    .join('&');
  return `${url}${paramString ? `?${paramString}` : ''}`;
}

function isValidCacheEntry(entry, ttl) {
  return entry && (Date.now() - entry.timestamp) < ttl;
}

function setCache(key, data, ttl = CACHE_CONFIG.DEFAULT_TTL) {
  cache.set(key, {
    data,
    timestamp: Date.now(),
    ttl,
  });
}

function getCache(key, ttl = CACHE_CONFIG.DEFAULT_TTL) {
  const entry = cache.get(key);
  if (isValidCacheEntry(entry, ttl)) {
    return entry.data;
  }
  cache.delete(key);
  return null;
}

function transformError(error) {
  // Network error
  if (!error.response) {
    return {
      type: ERROR_TYPES.NETWORK_ERROR,
      message: 'Network error. Please check your internet connection.',
      originalError: error,
    };
  }
  
  const { status, data } = error.response;
  
  // Transform based on status code
  switch (status) {
    case HTTP_STATUS.BAD_REQUEST:
      return {
        type: ERROR_TYPES.VALIDATION_ERROR,
        message: data?.message || 'Invalid request parameters.',
        errors: data?.errors || [],
        originalError: error,
      };
      
    case HTTP_STATUS.NOT_FOUND:
      return {
        type: ERROR_TYPES.NOT_FOUND,
        message: data?.message || 'The requested resource was not found.',
        originalError: error,
      };
      
    case HTTP_STATUS.TOO_MANY_REQUESTS:
      return {
        type: ERROR_TYPES.RATE_LIMIT,
        message: data?.message || 'Too many requests. Please try again later.',
        retryAfter: error.response.headers['retry-after'],
        originalError: error,
      };
      
    case HTTP_STATUS.INTERNAL_SERVER_ERROR:
    case HTTP_STATUS.BAD_GATEWAY:
    case HTTP_STATUS.SERVICE_UNAVAILABLE:
    case HTTP_STATUS.GATEWAY_TIMEOUT:
      return {
        type: ERROR_TYPES.SERVER_ERROR,
        message: data?.message || 'Server error. Please try again later.',
        originalError: error,
      };
      
    default:
      return {
        type: ERROR_TYPES.API_ERROR,
        message: data?.message || `Request failed with status ${status}.`,
        originalError: error,
      };
  }
}

// Retry mechanism
async function retryRequest(requestFn, maxRetries = API_CONFIG.RETRY_ATTEMPTS) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on certain error types
      if (error.type === ERROR_TYPES.VALIDATION_ERROR || 
          error.type === ERROR_TYPES.NOT_FOUND ||
          error.originalError?.response?.status === HTTP_STATUS.BAD_REQUEST) {
        throw error;
      }
      
      // Wait before retrying (exponential backoff)
      if (attempt < maxRetries) {
        const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, attempt - 1);
        await new Promise(resolve => setTimeout(resolve, delay));
        console.log(`🔄 Retrying request (attempt ${attempt + 1}/${maxRetries}) after ${delay}ms`);
      }
    }
  }
  
  throw lastError;
}

// API Service Class
class ApiService {
  // Health endpoints
  async checkHealth() {
    const response = await apiClient.get(API_ENDPOINTS.HEALTH);
    return response.data;
  }
  
  async checkHealthSimple() {
    const response = await apiClient.get(API_ENDPOINTS.HEALTH_SIMPLE);
    return response.data;
  }
  
  // Search endpoints
  async searchCompanies(query, options = {}) {
    const { limit, useCache = true } = options;
    const params = { q: query };
    if (limit) params.limit = limit;
    
    const cacheKey = getCacheKey(`search:${query}`, params);
    
    // Check cache first
    if (useCache) {
      const cached = getCache(cacheKey, CACHE_CONFIG.SEARCH_TTL);
      if (cached) {
        console.log('📦 Cache hit for search:', query);
        return cached;
      }
    }
    
    // Make API request with retry
    const response = await retryRequest(() => 
      apiClient.get(API_ENDPOINTS.SEARCH, { params })
    );
    
    const result = response.data;
    
    // Cache successful results
    if (useCache && result.status === 'success') {
      setCache(cacheKey, result, CACHE_CONFIG.SEARCH_TTL);
    }
    
    return result;
  }
  
  async getSearchSuggestions(query, options = {}) {
    const { limit = 5 } = options;
    const params = { q: query, limit };
    
    const response = await apiClient.get(API_ENDPOINTS.SEARCH_SUGGESTIONS, { params });
    return response.data;
  }
  
  async validateSearchQuery(query) {
    const params = { q: query };
    
    const response = await apiClient.get(API_ENDPOINTS.SEARCH_VALIDATE, { params });
    return response.data;
  }
  
  // Company endpoints
  async lookupCompany(query, options = {}) {
    const { 
      includeStock = true, 
      includeFilings = true, 
      filingsLimit = 5,
      useCache = true 
    } = options;
    
    const params = {
      q: query,
      include_stock: includeStock,
      include_filings: includeFilings,
      filings_limit: filingsLimit,
    };
    
    const cacheKey = getCacheKey(`lookup:${query}`, params);
    
    // Check cache first
    if (useCache) {
      const cached = getCache(cacheKey, CACHE_CONFIG.COMPANY_TTL);
      if (cached) {
        console.log('📦 Cache hit for company lookup:', query);
        return cached;
      }
    }
    
    // Make API request with retry
    const response = await retryRequest(() => 
      apiClient.get(API_ENDPOINTS.COMPANY_LOOKUP, { params })
    );
    
    const result = response.data;
    
    // Cache successful results
    if (useCache && result.status === 'success') {
      setCache(cacheKey, result, CACHE_CONFIG.COMPANY_TTL);
    }
    
    return result;
  }
  
  async getCompanyByTicker(ticker, options = {}) {
    const { useCache = true } = options;
    const url = `${API_ENDPOINTS.COMPANY_BY_TICKER}/${ticker}`;
    
    const cacheKey = getCacheKey(`company:${ticker}`);
    
    // Check cache first
    if (useCache) {
      const cached = getCache(cacheKey, CACHE_CONFIG.COMPANY_TTL);
      if (cached) {
        console.log('📦 Cache hit for company:', ticker);
        return cached;
      }
    }
    
    const response = await retryRequest(() => apiClient.get(url));
    const result = response.data;
    
    // Cache successful results
    if (useCache && result.status === 'success') {
      setCache(cacheKey, result, CACHE_CONFIG.COMPANY_TTL);
    }
    
    return result;
  }
  
  // Stock endpoints
  async getStockQuote(ticker, options = {}) {
    const { detailed = false, useCache = true } = options;
    const url = `${API_ENDPOINTS.STOCK_QUOTE}/${ticker}`;
    const params = { detailed };
    
    const cacheKey = getCacheKey(`stock:${ticker}`, params);
    
    // Check cache first (shorter TTL for stock data)
    if (useCache) {
      const cached = getCache(cacheKey, CACHE_CONFIG.STOCK_TTL);
      if (cached) {
        console.log('📦 Cache hit for stock:', ticker);
        return cached;
      }
    }
    
    const response = await retryRequest(() => 
      apiClient.get(url, { params })
    );
    
    const result = response.data;
    
    // Cache successful results
    if (useCache && result.status === 'success') {
      setCache(cacheKey, result, CACHE_CONFIG.STOCK_TTL);
    }
    
    return result;
  }
  
  async getBatchStockQuotes(tickers, options = {}) {
    const { useCache = false } = options; // Disable cache for batch requests
    const params = { tickers };
    
    const response = await retryRequest(() => 
      apiClient.get(API_ENDPOINTS.STOCK_BATCH, { params })
    );
    
    return response.data;
  }
  
  // SEC filings endpoints
  async getCompanyFilings(cik, options = {}) {
    const { formTypes, limit = 10, useCache = true } = options;
    const url = `${API_ENDPOINTS.FILINGS}/${cik}`;
    const params = { limit };
    
    if (formTypes && formTypes.length > 0) {
      params.form_types = formTypes;
    }
    
    const cacheKey = getCacheKey(`filings:${cik}`, params);
    
    // Check cache first
    if (useCache) {
      const cached = getCache(cacheKey, CACHE_CONFIG.FILINGS_TTL);
      if (cached) {
        console.log('📦 Cache hit for filings:', cik);
        return cached;
      }
    }
    
    const response = await retryRequest(() => 
      apiClient.get(url, { params })
    );
    
    const result = response.data;
    
    // Cache successful results
    if (useCache && result.status === 'success') {
      setCache(cacheKey, result, CACHE_CONFIG.FILINGS_TTL);
    }
    
    return result;
  }
  
  // Utility methods
  clearCache() {
    cache.clear();
    console.log('🗑️ API cache cleared');
  }
  
  getCacheStats() {
    return {
      size: cache.size,
      entries: Array.from(cache.entries()).map(([key, value]) => ({
        key,
        age: Date.now() - value.timestamp,
        ttl: value.ttl,
      })),
    };
  }
  
  // Save recent searches to localStorage
  saveRecentSearch(query) {
    try {
      const recent = this.getRecentSearches();
      const updated = [query, ...recent.filter(q => q !== query)].slice(0, 10);
      localStorage.setItem(STORAGE_KEYS.RECENT_SEARCHES, JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to save recent search:', error);
    }
  }
  
  getRecentSearches() {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.RECENT_SEARCHES);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.warn('Failed to load recent searches:', error);
      return [];
    }
  }
  
  clearRecentSearches() {
    try {
      localStorage.removeItem(STORAGE_KEYS.RECENT_SEARCHES);
    } catch (error) {
      console.warn('Failed to clear recent searches:', error);
    }
  }
}

// Export singleton instance
const apiService = new ApiService();

export default apiService;

// Export individual methods for convenience
export const {
  checkHealth,
  checkHealthSimple,
  searchCompanies,
  getSearchSuggestions,
  validateSearchQuery,
  lookupCompany,
  getCompanyByTicker,
  getStockQuote,
  getBatchStockQuotes,
  getCompanyFilings,
  clearCache,
  getCacheStats,
  saveRecentSearch,
  getRecentSearches,
  clearRecentSearches,
} = apiService;