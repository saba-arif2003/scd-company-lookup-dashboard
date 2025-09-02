import { format, parseISO, isValid, formatDistanceToNow } from 'date-fns';
import { NUMBER_FORMATS, DATE_FORMATS } from '../services/constants';

/**
 * Format currency values
 */
export const formatCurrency = (value, options = {}) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }

  const {
    currency = 'USD',
    minimumFractionDigits = 2,
    maximumFractionDigits = 2,
    compact = false,
  } = options;

  // For very large numbers, use compact notation
  if (compact || Math.abs(value) >= 1000000) {
    if (Math.abs(value) >= 1000000000000) {
      return `$${(value / 1000000000000).toFixed(1)}T`;
    } else if (Math.abs(value) >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (Math.abs(value) >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (Math.abs(value) >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
  }

  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits,
      maximumFractionDigits,
    }).format(value);
  } catch (error) {
    console.warn('Currency formatting error:', error);
    return `$${value.toFixed(2)}`;
  }
};

/**
 * Format percentage values
 */
export const formatPercentage = (value, options = {}) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }

  const {
    minimumFractionDigits = 2,
    maximumFractionDigits = 2,
    showSign = false,
  } = options;

  try {
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits,
      maximumFractionDigits,
    }).format(value / 100);

    if (showSign && value > 0) {
      return `+${formatted}`;
    }

    return formatted;
  } catch (error) {
    console.warn('Percentage formatting error:', error);
    const sign = showSign && value > 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  }
};

/**
 * Format large numbers with K, M, B, T suffixes
 */
export const formatLargeNumber = (value, options = {}) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }

  const { decimals = 1, forceDecimals = false } = options;

  const abs = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (abs >= 1000000000000) {
    const formatted = (value / 1000000000000).toFixed(decimals);
    return `${sign}${forceDecimals ? formatted : parseFloat(formatted)}T`;
  } else if (abs >= 1000000000) {
    const formatted = (value / 1000000000).toFixed(decimals);
    return `${sign}${forceDecimals ? formatted : parseFloat(formatted)}B`;
  } else if (abs >= 1000000) {
    const formatted = (value / 1000000).toFixed(decimals);
    return `${sign}${forceDecimals ? formatted : parseFloat(formatted)}M`;
  } else if (abs >= 1000) {
    const formatted = (value / 1000).toFixed(decimals);
    return `${sign}${forceDecimals ? formatted : parseFloat(formatted)}K`;
  }

  return value.toLocaleString('en-US');
};

/**
 * Format regular numbers
 */
export const formatNumber = (value, options = {}) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }

  const {
    minimumFractionDigits = 0,
    maximumFractionDigits = 2,
    useGrouping = true,
  } = options;

  try {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits,
      maximumFractionDigits,
      useGrouping,
    }).format(value);
  } catch (error) {
    console.warn('Number formatting error:', error);
    return value.toString();
  }
};

/**
 * Format dates
 */
export const formatDate = (dateInput, formatString = DATE_FORMATS.DISPLAY) => {
  if (!dateInput) {
    return 'N/A';
  }

  try {
    let date;
    
    if (typeof dateInput === 'string') {
      date = parseISO(dateInput);
    } else if (dateInput instanceof Date) {
      date = dateInput;
    } else {
      return 'Invalid Date';
    }

    if (!isValid(date)) {
      return 'Invalid Date';
    }

    return format(date, formatString);
  } catch (error) {
    console.warn('Date formatting error:', error);
    return 'Invalid Date';
  }
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (dateInput) => {
  if (!dateInput) {
    return 'N/A';
  }

  try {
    let date;
    
    if (typeof dateInput === 'string') {
      date = parseISO(dateInput);
    } else if (dateInput instanceof Date) {
      date = dateInput;
    } else {
      return 'Invalid Date';
    }

    if (!isValid(date)) {
      return 'Invalid Date';
    }

    return formatDistanceToNow(date, { addSuffix: true });
  } catch (error) {
    console.warn('Relative time formatting error:', error);
    return 'Invalid Date';
  }
};

/**
 * Format stock change with color and sign
 */
export const formatStockChange = (change, changePercent) => {
  if (change === null || change === undefined || isNaN(change)) {
    return {
      value: 'N/A',
      percent: 'N/A',
      color: 'neutral',
      isPositive: false,
      isNegative: false,
    };
  }

  const isPositive = change > 0;
  const isNegative = change < 0;
  const color = isPositive ? 'positive' : isNegative ? 'negative' : 'neutral';

  const formattedValue = formatCurrency(Math.abs(change));
  const formattedPercent = formatPercentage(Math.abs(changePercent || 0));

  const sign = isPositive ? '+' : isNegative ? '-' : '';

  return {
    value: `${sign}${formattedValue}`,
    percent: `${sign}${formattedPercent}`,
    color,
    isPositive,
    isNegative,
    isNeutral: !isPositive && !isNegative,
  };
};

/**
 * Format market cap with appropriate suffix
 */
export const formatMarketCap = (value) => {
  return formatLargeNumber(value, { decimals: 2 });
};

/**
 * Format volume numbers
 */
export const formatVolume = (value) => {
  return formatLargeNumber(value, { decimals: 1 });
};

/**
 * Format P/E ratio
 */
export const formatPERatio = (value) => {
  if (value === null || value === undefined || isNaN(value) || value <= 0) {
    return 'N/A';
  }

  return formatNumber(value, { maximumFractionDigits: 2 });
};

/**
 * Format ticker symbol
 */
export const formatTicker = (ticker) => {
  if (!ticker) return '';
  return ticker.toUpperCase();
};

/**
 * Format company name
 */
export const formatCompanyName = (name, maxLength = 50) => {
  if (!name) return '';
  
  if (name.length <= maxLength) return name;
  
  return `${name.substring(0, maxLength - 3)}...`;
};

/**
 * Format filing form type with color
 */
export const formatFilingForm = (form) => {
  if (!form) return { text: 'N/A', color: 'gray' };

  const formUpper = form.toUpperCase();
  
  const colorMap = {
    '10-K': 'blue',
    '10-Q': 'green',
    '8-K': 'yellow',
    'DEF 14A': 'purple',
    'S-1': 'orange',
    '4': 'red',
    '3': 'red',
    '5': 'red',
  };

  return {
    text: form,
    color: colorMap[formUpper] || 'gray',
  };
};

/**
 * Format file size
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return 'N/A';

  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  if (i === 0) return `${bytes} ${sizes[i]}`;
  
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  
  if (text.length <= maxLength) return text;
  
  return `${text.substring(0, maxLength - 3)}...`;
};

/**
 * Format search query for display
 */
export const formatSearchQuery = (query) => {
  if (!query) return '';
  
  // Clean and normalize the query
  return query.trim().replace(/\s+/g, ' ');
};

/**
 * Format error messages for display
 */
export const formatErrorMessage = (error) => {
  if (!error) return 'An unknown error occurred';
  
  if (typeof error === 'string') return error;
  
  if (error.message) return error.message;
  
  return 'An error occurred while processing your request';
};

/**
 * Format API response time
 */
export const formatResponseTime = (milliseconds) => {
  if (!milliseconds || milliseconds < 0) return 'N/A';
  
  if (milliseconds < 1000) {
    return `${Math.round(milliseconds)}ms`;
  }
  
  return `${(milliseconds / 1000).toFixed(1)}s`;
};

// Export all formatters as a single object for convenience
export const formatters = {
  currency: formatCurrency,
  percentage: formatPercentage,
  largeNumber: formatLargeNumber,
  number: formatNumber,
  date: formatDate,
  relativeTime: formatRelativeTime,
  stockChange: formatStockChange,
  marketCap: formatMarketCap,
  volume: formatVolume,
  peRatio: formatPERatio,
  ticker: formatTicker,
  companyName: formatCompanyName,
  filingForm: formatFilingForm,
  fileSize: formatFileSize,
  truncateText,
  searchQuery: formatSearchQuery,
  errorMessage: formatErrorMessage,
  responseTime: formatResponseTime,
};