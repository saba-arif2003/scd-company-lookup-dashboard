import React, { useState, useRef, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  XMarkIcon,
  ClockIcon,
  BuildingOfficeIcon 
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { useCompanySearch } from '../../hooks/useCompanySearch';
import SearchSuggestions from './SearchSuggestions';
import LoadingSpinner from '../common/LoadingSpinner';

const SearchBar = ({ 
  onSearchResult,
  placeholder = "Search companies (e.g., Tesla, TSLA, Apple)",
  showSuggestions = true,
  showRecentSearches = true,
  autoFocus = false,
  size = 'lg',
  className 
}) => {
  const [focused, setFocused] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  const {
    query,
    setQuery,
    search,
    results,
    suggestions,
    loading,
    error,
    hasSearched,
    clearSearch,
    getRecentSearches,
    isValidQuery,
    hasSuggestions,
  } = useCompanySearch({
    autoSearch: false, // Manual search only
    enableSuggestions: showSuggestions,
  });

  const [recentSearches, setRecentSearches] = useState([]);

  // Load recent searches on mount
  useEffect(() => {
    if (showRecentSearches) {
      setRecentSearches(getRecentSearches());
    }
  }, [showRecentSearches, getRecentSearches]);

  // Auto focus
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  // Handle clicks outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !inputRef.current?.contains(event.target)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Size configurations
  const sizeConfig = {
    sm: {
      input: 'text-sm py-2 pl-10 pr-10',
      icon: 'w-4 h-4 left-3',
      clearIcon: 'w-4 h-4',
    },
    md: {
      input: 'text-base py-3 pl-12 pr-12',
      icon: 'w-5 h-5 left-4',
      clearIcon: 'w-5 h-5',
    },
    lg: {
      input: 'text-lg py-4 pl-14 pr-14',
      icon: 'w-6 h-6 left-4',
      clearIcon: 'w-5 h-5',
    },
  };

  const config = sizeConfig[size] || sizeConfig.lg;

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    // Show dropdown when typing
    if (value.trim() && (showSuggestions || showRecentSearches)) {
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
  };

  const handleInputFocus = () => {
    setFocused(true);
    
    // Show recent searches or suggestions on focus
    if (showRecentSearches && recentSearches.length > 0) {
      setShowDropdown(true);
    } else if (showSuggestions && (query.trim() || hasSuggestions)) {
      setShowDropdown(true);
    }
  };

  const handleInputBlur = () => {
    setFocused(false);
    // Delay hiding dropdown to allow for clicks on suggestions
    setTimeout(() => {
      setShowDropdown(false);
    }, 200);
  };

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim() || !isValidQuery) return;

    try {
      const searchResults = await search(searchQuery);
      
      // Update recent searches
      if (showRecentSearches) {
        const updatedRecent = getRecentSearches();
        setRecentSearches(updatedRecent);
      }
      
      // Notify parent component
      if (onSearchResult) {
        onSearchResult({
          query: searchQuery,
          results: results,
          hasResults: results.length > 0,
          error: null,
        });
      }
      
      setShowDropdown(false);
    } catch (err) {
      // Handle error
      if (onSearchResult) {
        onSearchResult({
          query: searchQuery,
          results: [],
          hasResults: false,
          error: err.message || 'Search failed',
        });
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
      inputRef.current?.blur();
    }
  };

  const handleClear = () => {
    clearSearch();
    setShowDropdown(false);
    inputRef.current?.focus();
    
    // Notify parent about clearing
    if (onSearchResult) {
      onSearchResult({
        query: '',
        results: [],
        hasResults: false,
        error: null,
      });
    }
  };

  const handleSuggestionSelect = (suggestion) => {
    const searchText = typeof suggestion === 'string' ? suggestion : suggestion.text;
    setQuery(searchText);
    handleSearch(searchText);
  };

  const handleRecentSearchSelect = (recentQuery) => {
    setQuery(recentQuery);
    handleSearch(recentQuery);
  };

  return (
    <div className={clsx('search-container relative', className)}>
      {/* Search Input */}
      <div className="relative">
        {/* Search Icon */}
        <MagnifyingGlassIcon 
          className={clsx(
            'search-icon absolute top-1/2 transform -translate-y-1/2 text-gray-400',
            config.icon
          )}
        />

        {/* Input Field */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={clsx(
            'search-input block w-full border border-gray-300 rounded-xl shadow-sm transition-all duration-200',
            'focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder-gray-400',
            config.input,
            {
              'ring-2 ring-blue-500 border-blue-500': focused,
              'border-danger-300 focus:border-danger-500 focus:ring-danger-500': error,
            }
          )}
          disabled={loading}
        />

        {/* Loading Spinner or Clear Button */}
        <div className={clsx(
          'absolute right-4 top-1/2 transform -translate-y-1/2',
          'flex items-center space-x-2'
        )}>
          {loading && (
            <LoadingSpinner size="sm" color="primary" />
          )}
          
          {query && !loading && (
            <button
              type="button"
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <XMarkIcon className={config.clearIcon} />
            </button>
          )}
        </div>
      </div>

      {/* Search Button (for mobile) */}
      <button
        type="button"
        onClick={() => handleSearch()}
        disabled={!isValidQuery || loading}
        className="md:hidden mt-3 w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? <LoadingSpinner size="sm" color="white" /> : 'Search'}
      </button>

      {/* Dropdown with Suggestions and Recent Searches */}
      {showDropdown && (focused || showDropdown) && (
        <div 
          ref={dropdownRef}
          className="search-suggestions absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-xl shadow-strong mt-2 max-h-80 overflow-y-auto z-50"
        >
          {/* Error Message */}
          {error && (
            <div className="px-4 py-3 text-sm text-danger-600 bg-danger-50 border-b border-danger-200">
              {error}
            </div>
          )}

          {/* Suggestions */}
          {showSuggestions && hasSuggestions && (
            <SearchSuggestions
              suggestions={suggestions}
              onSelect={handleSuggestionSelect}
              query={query}
            />
          )}

          {/* Recent Searches */}
          {showRecentSearches && recentSearches.length > 0 && !query.trim() && (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
                Recent Searches
              </div>
              {recentSearches.slice(0, 5).map((recentQuery, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleRecentSearchSelect(recentQuery)}
                  className="search-suggestion-item w-full text-left flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors duration-150"
                >
                  <ClockIcon className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-900">{recentQuery}</span>
                </button>
              ))}
            </div>
          )}

          {/* No Results */}
          {!loading && !hasSuggestions && !recentSearches.length && query.trim() && (
            <div className="px-4 py-8 text-center">
              <BuildingOfficeIcon className="w-8 h-8 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                No suggestions found for "{query}"
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Try searching for a company name or ticker symbol
              </p>
            </div>
          )}

          {/* Loading State */}
          {loading && query.trim() && (
            <div className="px-4 py-8 text-center">
              <LoadingSpinner size="sm" color="primary" text="Searching..." />
            </div>
          )}
        </div>
      )}

      {/* Search Tips (hidden by default, can be shown based on props) */}
      {focused && !query && !showDropdown && (
        <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-xl shadow-soft mt-2 p-4 z-40">
          <div className="text-sm text-gray-600">
            <p className="font-medium mb-2">Search Tips:</p>
            <ul className="space-y-1 text-xs">
              <li>• Try company names: "Tesla", "Apple", "Microsoft"</li>
              <li>• Or ticker symbols: "TSLA", "AAPL", "MSFT"</li>
              <li>• Use partial names: "micro" will find "Microsoft"</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;