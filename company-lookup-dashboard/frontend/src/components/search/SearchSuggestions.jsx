import React from 'react';
import { 
  BuildingOfficeIcon, 
  HashtagIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

const SearchSuggestions = ({ suggestions = [], onSelect, query = '', maxItems = 5 }) => {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  // Limit suggestions to maxItems
  const displaySuggestions = suggestions.slice(0, maxItems);

  const getIconForType = (type) => {
    switch (type) {
      case 'ticker':
        return HashtagIcon;
      case 'company_name':
        return BuildingOfficeIcon;
      case 'suggestion':
        return SparklesIcon;
      default:
        return BuildingOfficeIcon;
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'ticker':
        return 'Ticker';
      case 'company_name':
        return 'Company';
      case 'suggestion':
        return 'Suggestion';
      default:
        return 'Company';
    }
  };

  const highlightMatch = (text, searchQuery) => {
    if (!searchQuery || !text) return text;

    const regex = new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) => {
      const isMatch = part.toLowerCase() === searchQuery.toLowerCase();
      return (
        <span
          key={index}
          className={isMatch ? 'font-semibold text-primary-600 bg-primary-50 px-1 rounded' : ''}
        >
          {part}
        </span>
      );
    });
  };

  return (
    <div className="py-2">
      {/* Header */}
      <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
        Suggestions
      </div>

      {/* Suggestion Items */}
      <div className="max-h-64 overflow-y-auto">
        {displaySuggestions.map((suggestion, index) => {
          const Icon = getIconForType(suggestion.type);
          const isString = typeof suggestion === 'string';
          const text = isString ? suggestion : suggestion.text;
          const type = isString ? 'company_name' : suggestion.type;
          const matchScore = isString ? null : suggestion.match_score;
          const ticker = isString ? null : suggestion.ticker;
          const companyName = isString ? null : suggestion.company_name;

          return (
            <button
              key={index}
              type="button"
              onClick={() => onSelect(suggestion)}
              className={clsx(
                'search-suggestion-item w-full text-left',
                'flex items-center space-x-3 px-4 py-3',
                'hover:bg-gray-50 focus:bg-gray-50 focus:outline-none',
                'transition-colors duration-150',
                'border-b border-gray-100 last:border-b-0'
              )}
            >
              {/* Icon */}
              <div className="flex-shrink-0">
                <Icon className="w-4 h-4 text-gray-400" />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  {/* Main text */}
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {highlightMatch(text, query)}
                  </div>

                  {/* Type badge */}
                  <span className={clsx(
                    'ml-2 px-2 py-1 text-xs font-medium rounded-full flex-shrink-0',
                    {
                      'bg-blue-100 text-blue-800': type === 'ticker',
                      'bg-gray-100 text-gray-800': type === 'company_name',
                      'bg-purple-100 text-purple-800': type === 'suggestion',
                    }
                  )}>
                    {getTypeLabel(type)}
                  </span>
                </div>

                {/* Additional info */}
                {(ticker || companyName) && (
                  <div className="text-xs text-gray-500 mt-1 truncate">
                    {type === 'ticker' && companyName ? (
                      <span>Company: {companyName}</span>
                    ) : type === 'company_name' && ticker ? (
                      <span>Ticker: {ticker}</span>
                    ) : null}
                  </div>
                )}

                {/* Match score (for debugging/development) */}
                {process.env.NODE_ENV === 'development' && matchScore && (
                  <div className="text-xs text-gray-400 mt-1">
                    Match: {(matchScore * 100).toFixed(0)}%
                  </div>
                )}
              </div>

              {/* Keyboard shortcut hint */}
              {index < 9 && (
                <div className="flex-shrink-0 text-xs text-gray-400 font-mono">
                  {index + 1}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Show more indicator */}
      {suggestions.length > maxItems && (
        <div className="px-4 py-2 text-center border-t border-gray-100">
          <span className="text-xs text-gray-500">
            +{suggestions.length - maxItems} more suggestions
          </span>
        </div>
      )}
    </div>
  );
};

export default SearchSuggestions;