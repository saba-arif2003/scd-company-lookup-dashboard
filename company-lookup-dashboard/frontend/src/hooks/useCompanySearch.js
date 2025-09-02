import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';
import { useDebounce } from './useDebounce';
import { SEARCH_CONFIG } from '../services/constants';

/**
 * Custom hook for company search functionality
 * Handles search state, debouncing, suggestions, and API calls
 * 
 * @param {Object} options - Configuration options
 * @returns {Object} - Search state and methods
 */
export function useCompanySearch(options = {}) {
  const {
    debounceDelay = SEARCH_CONFIG.DEBOUNCE_DELAY,
    minQueryLength = SEARCH_CONFIG.MIN_QUERY_LENGTH,
    maxResults = SEARCH_CONFIG.MAX_RESULTS,
    enableSuggestions = true,
    autoSearch = true,
  } = options;

  // Search state
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Debounced query for API calls
  const debouncedQuery = useDebounce(query, debounceDelay);

  // Search function
  const performSearch = useCallback(async (searchQuery, options = {}) => {
    if (!searchQuery || searchQuery.length < minQueryLength) {
      setResults([]);
      setError(null);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.searchCompanies(searchQuery, {
        limit: maxResults,
        ...options,
      });

      console.log('Full API response:', response);
      console.log('Response data:', response.data);

      if (response.status === 'success') {
        // FIXED: Access the results from the correct path
        const searchResults = response.data?.results || [];
        console.log('Search results:', searchResults);
        
        setResults(searchResults);
        setHasSearched(true);
        
        // Save successful search to recent searches
        if (searchResults.length > 0) {
          apiService.saveRecentSearch(searchQuery);
        }
      } else {
        setError(response.message || 'Search failed');
        setResults([]);
        setHasSearched(true);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'Search failed. Please try again.');
      setResults([]);
      setHasSearched(true);
    } finally {
      setLoading(false);
    }
  }, [minQueryLength, maxResults]);

  // Get search suggestions
  const getSuggestions = useCallback(async (searchQuery) => {
    if (!enableSuggestions || !searchQuery || searchQuery.length < minQueryLength) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await apiService.getSearchSuggestions(searchQuery, {
        limit: SEARCH_CONFIG.MAX_SUGGESTIONS,
      });

      console.log('Suggestions response:', response);

      if (response.status === 'success') {
        // Access suggestions from the correct path
        const suggestionList = response.data?.suggestions || [];
        console.log('Suggestions list:', suggestionList);
        setSuggestions(suggestionList);
      }
    } catch (err) {
      console.error('Suggestions error:', err);
      setSuggestions([]);
    }
  }, [enableSuggestions, minQueryLength]);

  // Auto search when debounced query changes
  useEffect(() => {
    if (autoSearch && debouncedQuery) {
      performSearch(debouncedQuery);
    }
  }, [debouncedQuery, autoSearch, performSearch]);

  // Get suggestions when query changes (faster than search)
  useEffect(() => {
    if (enableSuggestions && query && query !== debouncedQuery) {
      const timeoutId = setTimeout(() => {
        getSuggestions(query);
      }, 100); // Shorter delay for suggestions

      return () => clearTimeout(timeoutId);
    }
  }, [query, debouncedQuery, enableSuggestions, getSuggestions]);

  // Manual search function
  const search = useCallback((searchQuery = query, options = {}) => {
    return performSearch(searchQuery, options);
  }, [query, performSearch]);

  // Clear search results
  const clearSearch = useCallback(() => {
    setQuery('');
    setResults([]);
    setSuggestions([]);
    setError(null);
    setHasSearched(false);
  }, []);

  // Set query without triggering search
  const setQueryOnly = useCallback((newQuery) => {
    setQuery(newQuery);
  }, []);

  // Get recent searches from localStorage
  const getRecentSearches = useCallback(() => {
    return apiService.getRecentSearches();
  }, []);

  // Validate search query
  const validateQuery = useCallback(async (searchQuery = query) => {
    try {
      const response = await apiService.validateSearchQuery(searchQuery);
      return response.data || { is_valid: false };
    } catch (err) {
      console.error('Validation error:', err);
      return { is_valid: false, issues: ['Validation failed'] };
    }
  }, [query]);

  // Company lookup function (for detailed company info)
  const lookupCompany = useCallback(async (searchQuery = query) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.lookupCompany(searchQuery);
      console.log('Company lookup response:', response);
      
      if (response.status === 'success') {
        return response.data;
      } else {
        throw new Error(response.message || 'Company lookup failed');
      }
    } catch (err) {
      console.error('Company lookup error:', err);
      setError(err.message || 'Company lookup failed. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [query]);

  return {
    // State
    query,
    results,
    suggestions,
    loading,
    error,
    hasSearched,
    debouncedQuery,

    // Actions
    setQuery,
    setQueryOnly,
    search,
    clearSearch,
    getSuggestions,
    validateQuery,
    getRecentSearches,
    lookupCompany,

    // Computed values
    hasResults: results.length > 0,
    isEmpty: hasSearched && results.length === 0,
    isValidQuery: query.length >= minQueryLength,
    hasSuggestions: suggestions.length > 0,
  };
}

/**
 * Simplified hook for basic search functionality
 */
export function useSimpleSearch() {
  return useCompanySearch({
    enableSuggestions: false,
    autoSearch: false,
  });
}

/**
 * Hook for search with suggestions only (no auto-search)
 */
export function useSearchWithSuggestions() {
  return useCompanySearch({
    autoSearch: false,
    enableSuggestions: true,
  });
}

/**
 * Hook specifically for company lookup with detailed info
 */
export function useCompanyLookup() {
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const lookupCompany = useCallback(async (query) => {
    setLoading(true);
    setError(null);
    setCompany(null);

    try {
      const response = await apiService.lookupCompany(query);
      console.log('Company lookup response:', response);
      
      if (response.status === 'success') {
        setCompany(response.data);
        return response.data;
      } else {
        throw new Error(response.message || 'Company lookup failed');
      }
    } catch (err) {
      console.error('Company lookup error:', err);
      setError(err.message || 'Company lookup failed. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearCompany = useCallback(() => {
    setCompany(null);
    setError(null);
  }, []);

  return {
    company,
    loading,
    error,
    lookupCompany,
    clearCompany,
    hasCompany: !!company,
  };
}

export default useCompanySearch;