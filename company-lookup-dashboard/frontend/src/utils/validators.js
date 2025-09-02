import { SEARCH_CONFIG } from '../services/constants';

/**
 * Validate stock ticker symbol
 */
export const validateTicker = (ticker) => {
  if (!ticker) {
    return { isValid: false, error: 'Ticker is required' };
  }

  const tickerStr = ticker.toString().trim().toUpperCase();

  // Basic format: 1-5 letters, optionally followed by dot and 1-2 letters
  const tickerPattern = /^[A-Z]{1,5}(\.[A-Z]{1,2})?$/;

  if (!tickerPattern.test(tickerStr)) {
    return { 
      isValid: false, 
      error: 'Invalid ticker format. Use 1-5 letters (e.g., TSLA, BRK.A)' 
    };
  }

  return { isValid: true, value: tickerStr };
};

/**
 * Validate SEC CIK (Central Index Key)
 */
export const validateCIK = (cik) => {
  if (!cik) {
    return { isValid: false, error: 'CIK is required' };
  }

  const cikStr = cik.toString().trim();

  // Remove any non-digit characters
  const digitsOnly = cikStr.replace(/\D/g, '');

  if (digitsOnly.length === 0) {
    return { isValid: false, error: 'CIK must contain digits' };
  }

  if (digitsOnly.length > 10) {
    return { isValid: false, error: 'CIK cannot be more than 10 digits' };
  }

  // Pad with leading zeros to make 10 digits
  const paddedCIK = digitsOnly.padStart(10, '0');

  return { isValid: true, value: paddedCIK };
};

/**
 * Validate search query
 */
export const validateSearchQuery = (query) => {
  if (!query) {
    return { isValid: false, error: 'Search query is required' };
  }

  const queryStr = query.toString().trim();

  if (queryStr.length < SEARCH_CONFIG.MIN_QUERY_LENGTH) {
    return { 
      isValid: false, 
      error: `Query must be at least ${SEARCH_CONFIG.MIN_QUERY_LENGTH} characters` 
    };
  }

  if (queryStr.length > SEARCH_CONFIG.MAX_QUERY_LENGTH) {
    return { 
      isValid: false, 
      error: `Query cannot exceed ${SEARCH_CONFIG.MAX_QUERY_LENGTH} characters` 
    };
  }

  // Check for suspicious patterns (basic XSS prevention)
  const suspiciousPatterns = [
    /<script[^>]*>/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe[^>]*>/i,
  ];

  for (const pattern of suspiciousPatterns) {
    if (pattern.test(queryStr)) {
      return { isValid: false, error: 'Query contains invalid characters' };
    }
  }

  return { isValid: true, value: queryStr };
};

/**
 * Validate email format
 */
export const validateEmail = (email) => {
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }

  const emailStr = email.toString().trim().toLowerCase();

  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  if (!emailPattern.test(emailStr)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  return { isValid: true, value: emailStr };
};

/**
 * Validate URL format
 */
export const validateURL = (url) => {
  if (!url) {
    return { isValid: false, error: 'URL is required' };
  }

  const urlStr = url.toString().trim();

  try {
    new URL(urlStr);
    
    // Additional check for http/https
    if (!urlStr.match(/^https?:\/\//)) {
      return { isValid: false, error: 'URL must start with http:// or https://' };
    }

    return { isValid: true, value: urlStr };
  } catch {
    return { isValid: false, error: 'Invalid URL format' };
  }
};

/**
 * Validate date string
 */
export const validateDate = (dateStr, format = 'YYYY-MM-DD') => {
  if (!dateStr) {
    return { isValid: false, error: 'Date is required' };
  }

  const dateString = dateStr.toString().trim();

  // Check ISO date format (YYYY-MM-DD)
  if (format === 'YYYY-MM-DD') {
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    
    if (!datePattern.test(dateString)) {
      return { isValid: false, error: 'Date must be in YYYY-MM-DD format' };
    }

    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      return { isValid: false, error: 'Invalid date' };
    }

    // Check if the date string matches the parsed date
    // This catches cases like "2024-02-30" which would be parsed as "2024-03-01"
    if (date.toISOString().substr(0, 10) !== dateString) {
      return { isValid: false, error: 'Invalid date' };
    }

    return { isValid: true, value: dateString };
  }

  return { isValid: false, error: 'Unsupported date format' };
};

/**
 * Validate date range
 */
export const validateDateRange = (startDate, endDate) => {
  const startValidation = validateDate(startDate);
  const endValidation = validateDate(endDate);

  if (!startValidation.isValid) {
    return { isValid: false, error: `Start date: ${startValidation.error}` };
  }

  if (!endValidation.isValid) {
    return { isValid: false, error: `End date: ${endValidation.error}` };
  }

  const start = new Date(startDate);
  const end = new Date(endDate);

  if (start > end) {
    return { isValid: false, error: 'Start date cannot be after end date' };
  }

  return { 
    isValid: true, 
    value: { 
      startDate: startValidation.value, 
      endDate: endValidation.value 
    } 
  };
};

/**
 * Validate numeric value
 */
export const validateNumber = (value, options = {}) => {
  const { 
    min, 
    max, 
    integer = false, 
    positive = false,
    required = true 
  } = options;

  if (!value && value !== 0) {
    if (required) {
      return { isValid: false, error: 'Value is required' };
    }
    return { isValid: true, value: null };
  }

  const num = parseFloat(value);

  if (isNaN(num)) {
    return { isValid: false, error: 'Value must be a number' };
  }

  if (integer && !Number.isInteger(num)) {
    return { isValid: false, error: 'Value must be an integer' };
  }

  if (positive && num <= 0) {
    return { isValid: false, error: 'Value must be positive' };
  }

  if (min !== undefined && num < min) {
    return { isValid: false, error: `Value must be at least ${min}` };
  }

  if (max !== undefined && num > max) {
    return { isValid: false, error: `Value cannot exceed ${max}` };
  }

  return { isValid: true, value: num };
};

/**
 * Validate filing form types
 */
export const validateFilingForm = (form) => {
  if (!form) {
    return { isValid: false, error: 'Filing form is required' };
  }

  const formStr = form.toString().trim().toUpperCase();

  // Common SEC form types
  const validForms = [
    '10-K', '10-Q', '8-K', 'DEF 14A', 'S-1', 'S-3', 'S-4', 'S-8',
    '3', '4', '5', 'SC 13G', 'SC 13D', '11-K', '20-F', 'DEFA14A'
  ];

  // Allow any form that matches basic pattern (letters, numbers, spaces, dashes)
  const formPattern = /^[A-Z0-9\s\/-]+$/;

  if (!formPattern.test(formStr)) {
    return { isValid: false, error: 'Invalid filing form format' };
  }

  return { isValid: true, value: formStr };
};

/**
 * Validate array of values
 */
export const validateArray = (arr, validator, options = {}) => {
  const { minLength, maxLength, required = true } = options;

  if (!arr || !Array.isArray(arr)) {
    if (required) {
      return { isValid: false, error: 'Array is required' };
    }
    return { isValid: true, value: [] };
  }

  if (minLength !== undefined && arr.length < minLength) {
    return { isValid: false, error: `Array must have at least ${minLength} items` };
  }

  if (maxLength !== undefined && arr.length > maxLength) {
    return { isValid: false, error: `Array cannot have more than ${maxLength} items` };
  }

  const validatedItems = [];
  const errors = [];

  for (let i = 0; i < arr.length; i++) {
    const validation = validator(arr[i]);
    if (validation.isValid) {
      validatedItems.push(validation.value);
    } else {
      errors.push(`Item ${i + 1}: ${validation.error}`);
    }
  }

  if (errors.length > 0) {
    return { isValid: false, error: errors.join('; ') };
  }

  return { isValid: true, value: validatedItems };
};

/**
 * Validate limit parameter for API calls
 */
export const validateLimit = (limit) => {
  return validateNumber(limit, {
    min: 1,
    max: 100,
    integer: true,
    positive: true,
    required: false,
  });
};

/**
 * Validate offset parameter for pagination
 */
export const validateOffset = (offset) => {
  return validateNumber(offset, {
    min: 0,
    integer: true,
    required: false,
  });
};

/**
 * Sanitize string input
 */
export const sanitizeString = (str) => {
  if (!str) return '';

  return str
    .toString()
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/['"]/g, '') // Remove quotes
    .replace(/\s+/g, ' '); // Normalize whitespace
};

/**
 * Validate and sanitize search input
 */
export const validateAndSanitizeSearch = (query) => {
  const validation = validateSearchQuery(query);
  
  if (!validation.isValid) {
    return validation;
  }

  const sanitized = sanitizeString(validation.value);
  
  return { isValid: true, value: sanitized };
};

/**
 * Check if value is empty (null, undefined, empty string, empty array)
 */
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

/**
 * Validate form data object
 */
export const validateFormData = (data, schema) => {
  const errors = {};
  const validatedData = {};

  for (const [field, validator] of Object.entries(schema)) {
    const value = data[field];
    
    if (typeof validator === 'function') {
      const validation = validator(value);
      
      if (!validation.isValid) {
        errors[field] = validation.error;
      } else {
        validatedData[field] = validation.value;
      }
    } else if (typeof validator === 'object' && validator.validate) {
      const validation = validator.validate(value);
      
      if (!validation.isValid) {
        errors[field] = validation.error;
      } else {
        validatedData[field] = validation.value;
      }
    }
  }

  const hasErrors = Object.keys(errors).length > 0;

  return {
    isValid: !hasErrors,
    errors: hasErrors ? errors : null,
    data: hasErrors ? null : validatedData,
  };
};

/**
 * Create a validator that checks if value is one of allowed options
 */
export const createEnumValidator = (allowedValues, fieldName = 'Value') => {
  return (value) => {
    if (!allowedValues.includes(value)) {
      return {
        isValid: false,
        error: `${fieldName} must be one of: ${allowedValues.join(', ')}`,
      };
    }

    return { isValid: true, value };
  };
};

/**
 * Create a validator that checks string length
 */
export const createLengthValidator = (min, max, fieldName = 'Value') => {
  return (value) => {
    if (!value) {
      return { isValid: false, error: `${fieldName} is required` };
    }

    const str = value.toString().trim();

    if (str.length < min) {
      return { 
        isValid: false, 
        error: `${fieldName} must be at least ${min} characters` 
      };
    }

    if (max && str.length > max) {
      return { 
        isValid: false, 
        error: `${fieldName} cannot exceed ${max} characters` 
      };
    }

    return { isValid: true, value: str };
  };
};

/**
 * Create a validator that uses regex pattern
 */
export const createPatternValidator = (pattern, errorMessage) => {
  return (value) => {
    if (!value) {
      return { isValid: false, error: 'Value is required' };
    }

    const str = value.toString().trim();

    if (!pattern.test(str)) {
      return { isValid: false, error: errorMessage };
    }

    return { isValid: true, value: str };
  };
};

/**
 * Combine multiple validators
 */
export const combineValidators = (...validators) => {
  return (value) => {
    for (const validator of validators) {
      const result = validator(value);
      if (!result.isValid) {
        return result;
      }
    }

    return { isValid: true, value };
  };
};

/**
 * Common validation schemas
 */
export const validationSchemas = {
  searchForm: {
    query: validateSearchQuery,
    limit: validateLimit,
  },

  companyForm: {
    ticker: validateTicker,
    cik: validateCIK,
  },

  dateRangeForm: {
    startDate: validateDate,
    endDate: validateDate,
  },

  contactForm: {
    email: validateEmail,
    name: createLengthValidator(2, 50, 'Name'),
    message: createLengthValidator(10, 500, 'Message'),
  },
};

// Export all validators as a single object
export const validators = {
  ticker: validateTicker,
  cik: validateCIK,
  searchQuery: validateSearchQuery,
  email: validateEmail,
  url: validateURL,
  date: validateDate,
  dateRange: validateDateRange,
  number: validateNumber,
  filingForm: validateFilingForm,
  array: validateArray,
  limit: validateLimit,
  offset: validateOffset,
  formData: validateFormData,
  sanitizeString,
  validateAndSanitizeSearch,
  isEmpty,
  createEnumValidator,
  createLengthValidator,
  createPatternValidator,
  combineValidators,
  schemas: validationSchemas,
};