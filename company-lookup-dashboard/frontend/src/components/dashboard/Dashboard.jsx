import React, { useState, useCallback } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import SearchBar from '../search/SearchBar';
import CompanyCard, { CompanyCardSkeleton } from './CompanyCard';
import StockCard, { StockCardSkeleton } from './StockCard';
import FilingsTable from './FilingsTable';
import { NetworkError, NotFoundError, EmptyState } from '../common/ErrorMessage';
import LoadingSpinner from '../common/LoadingSpinner';
import apiService from '../../services/api';

const Dashboard = () => {
  const [searchState, setSearchState] = useState({
    query: '',
    loading: false,
    error: null,
    hasSearched: false,
  });

  const [companyData, setCompanyData] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const handleSearchResult = useCallback(async (searchResult) => {
    const { query, results, hasResults, error } = searchResult;
    
    setSearchState({
      query,
      loading: false,
      error,
      hasSearched: true,
    });

    // If we have results, get detailed information for the first result
    if (hasResults && results.length > 0) {
      setLoadingDetails(true);
      
      try {
        const response = await apiService.lookupCompany(query);
        
        if (response.status === 'success') {
          setCompanyData(response.data);
        } else {
          setSearchState(prev => ({
            ...prev,
            error: response.message || 'Failed to load company details'
          }));
        }
      } catch (err) {
        setSearchState(prev => ({
          ...prev,
          error: err.message || 'Failed to load company details'
        }));
      } finally {
        setLoadingDetails(false);
      }
    } else {
      setCompanyData(null);
    }
  }, []);

  const handleRetrySearch = useCallback(() => {
    if (searchState.query) {
      setSearchState(prev => ({ ...prev, loading: true, error: null }));
      // The SearchBar will handle the retry automatically
    }
  }, [searchState.query]);

  const clearResults = useCallback(() => {
    setSearchState({
      query: '',
      loading: false,
      error: null,
      hasSearched: false,
    });
    setCompanyData(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Company Financial Intelligence
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Access real-time stock data, company fundamentals, and SEC filings for informed investment decisions.
          </p>
        </div>

        {/* Search Section */}
        <div className="max-w-2xl mx-auto mb-12">
          <SearchBar
            onSearchResult={handleSearchResult}
            placeholder="Search companies by name or ticker (e.g., TSLA, AAPL)"
            showSuggestions={true}
            showRecentSearches={true}
            autoFocus={true}
          />
        </div>

        {/* Results Section */}
        <div className="space-y-8">
          {/* Loading State */}
          {loadingDetails && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-6">
                <CompanyCardSkeleton />
              </div>
              <div className="lg:col-span-1 space-y-6">
                <StockCardSkeleton />
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <div className="space-y-4">
                    {Array.from({ length: 3 }).map((_, index) => (
                      <div key={index} className="h-4 bg-gray-200 rounded animate-pulse" />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error States */}
          {searchState.error && !loadingDetails && (
            <div className="max-w-2xl mx-auto">
              {searchState.error.includes('Network') ? (
                <NetworkError onRetry={handleRetrySearch} onDismiss={clearResults} />
              ) : searchState.error.includes('not found') ? (
                <NotFoundError 
                  resource="Company" 
                  onRetry={handleRetrySearch} 
                  onDismiss={clearResults}
                />
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-red-900 mb-2">
                      Search Error
                    </div>
                    <p className="text-red-700 mb-4">
                      {searchState.error}
                    </p>
                    <div className="flex justify-center space-x-3">
                      <button
                        type="button"
                        onClick={handleRetrySearch}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
                      >
                        Try Again
                      </button>
                      <button
                        type="button"
                        onClick={clearResults}
                        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors duration-200"
                      >
                        Clear Search
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* No Results State */}
          {searchState.hasSearched && !companyData && !searchState.error && !loadingDetails && (
            <div className="max-w-2xl mx-auto">
              <EmptyState
                title="No Company Found"
                message={`We couldn't find any companies matching "${searchState.query}". Try searching with a different company name or ticker symbol.`}
                icon={MagnifyingGlassIcon}
                action={() => document.querySelector('input[type="text"]')?.focus()}
                actionText="Search Again"
              />
            </div>
          )}

          {/* Company Results */}
          {companyData && !loadingDetails && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-6">
                {/* Company Information */}
                <CompanyCard 
                  company={companyData.company} 
                  showDetails={true}
                />

                {/* SEC Filings */}
                {companyData.recent_filings && (
                  <FilingsTable 
                    filings={companyData.recent_filings}
                    showFilters={true}
                    maxHeight="500px"
                  />
                )}
              </div>

              {/* Sidebar */}
              <div className="lg:col-span-1 space-y-6">
                {/* Stock Quote */}
                {companyData.stock_quote && (
                  <StockCard 
                    stockData={companyData.stock_quote}
                    showExtendedData={false}
                  />
                )}

                {/* AI Investment Analysis */}
                {companyData.investment_analysis && (
                  <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      AI Investment Analysis
                    </h3>
                    
                    {/* Overall Sentiment */}
                    <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">Overall Sentiment:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${
                          companyData.investment_analysis.summary?.overall_sentiment === 'optimistic' || 
                          companyData.investment_analysis.summary?.overall_sentiment === 'cautiously optimistic' ? 'bg-green-100 text-green-800' :
                          companyData.investment_analysis.summary?.overall_sentiment === 'cautious' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {companyData.investment_analysis.summary?.overall_sentiment || 'Neutral'}
                        </span>
                      </div>
                    </div>

                    {/* Key Metrics */}
                    {companyData.investment_analysis.key_metrics && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Key Metrics</h4>
                        <div className="space-y-2 text-sm">
                          {Object.entries(companyData.investment_analysis.key_metrics).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                              <span className="font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Financial Metrics */}
                    {companyData.investment_analysis.financial_metrics && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Financial Overview</h4>
                        <div className="space-y-2 text-sm">
                          {Object.entries(companyData.investment_analysis.financial_metrics).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                              <span className="font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Technical Analysis */}
                    {companyData.investment_analysis.technical_analysis && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Technical Analysis</h4>
                        <div className="space-y-2 text-sm">
                          {Object.entries(companyData.investment_analysis.technical_analysis).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                              <span className="font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Performance Insights */}
                    {companyData.investment_analysis.performance_insights && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Performance</h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          {companyData.investment_analysis.performance_insights.short_term && (
                            <div>
                              <div className="text-gray-600 mb-1">Short Term</div>
                              {Object.entries(companyData.investment_analysis.performance_insights.short_term).map(([key, value]) => (
                                <div key={key} className="flex justify-between text-xs">
                                  <span>{key}:</span>
                                  <span className={value.startsWith('+') ? 'text-green-600' : value.startsWith('-') ? 'text-red-600' : ''}>{value}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          {companyData.investment_analysis.performance_insights.long_term && (
                            <div>
                              <div className="text-gray-600 mb-1">Long Term</div>
                              {Object.entries(companyData.investment_analysis.performance_insights.long_term).map(([key, value]) => (
                                <div key={key} className="flex justify-between text-xs">
                                  <span>{key}:</span>
                                  <span className={value.startsWith('+') ? 'text-green-600' : value.startsWith('-') ? 'text-red-600' : ''}>{value}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Risk Assessment */}
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Risk Assessment</h4>
                      <div className="text-sm">
                        <div className="flex justify-between mb-2">
                          <span className="text-gray-600">Risk Level:</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${
                            companyData.investment_analysis.risk_assessment?.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                            companyData.investment_analysis.risk_assessment?.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {companyData.investment_analysis.risk_assessment?.risk_level}
                          </span>
                        </div>
                        
                        {/* Risk Factors */}
                        {companyData.investment_analysis.risk_assessment?.risk_factors?.length > 0 && (
                          <div className="mt-2">
                            <div className="text-gray-600 mb-1">Risk Factors:</div>
                            <ul className="text-xs text-red-600 space-y-1">
                              {companyData.investment_analysis.risk_assessment.risk_factors.slice(0, 3).map((factor, index) => (
                                <li key={index}>• {factor}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Positive Indicators */}
                        {companyData.investment_analysis.risk_assessment?.positive_indicators?.length > 0 && (
                          <div className="mt-2">
                            <div className="text-gray-600 mb-1">Positive Indicators:</div>
                            <ul className="text-xs text-green-600 space-y-1">
                              {companyData.investment_analysis.risk_assessment.positive_indicators.slice(0, 3).map((indicator, index) => (
                                <li key={index}>• {indicator}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Recent Developments */}
                    {companyData.investment_analysis.recent_developments?.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Recent Developments</h4>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {companyData.investment_analysis.recent_developments.slice(0, 3).map((development, index) => (
                            <li key={index}>• {development}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Educational Considerations */}
                    {companyData.investment_analysis.educational_considerations?.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Key Considerations</h4>
                        <ul className="text-xs text-blue-600 space-y-1">
                          {companyData.investment_analysis.educational_considerations.slice(0, 4).map((consideration, index) => (
                            <li key={index}>• {consideration}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Disclaimer */}
                    <div className="text-xs text-gray-500 mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <strong>Disclaimer:</strong> {companyData.investment_analysis.disclaimer}
                    </div>
                  </div>
                )}

                {/* Data Sources */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Data Sources
                  </h3>
                  <div className="space-y-3">
                    {companyData.data_sources && Object.entries(companyData.data_sources).map(([key, source]) => (
                      <div key={key} className="flex justify-between items-center text-sm">
                        <span className="text-gray-600 capitalize">
                          {key.replace('_', ' ')}:
                        </span>
                        <span className="font-medium text-gray-900">
                          {source}
                        </span>
                      </div>
                    ))}
                  </div>
                  
                  {companyData.last_updated && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <div className="text-xs text-gray-500">
                        Last updated: {new Date(companyData.last_updated).toLocaleString()}
                      </div>
                    </div>
                  )}
                </div>

                {/* Quick Actions */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Quick Actions
                  </h3>
                  <div className="space-y-3">
                    {companyData.company?.website && (
                      <button
                        type="button"
                        onClick={() => window.open(companyData.company.website, '_blank')}
                        className="w-full px-4 py-2 text-left bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                      >
                        Visit Company Website
                      </button>
                    )}
                    
                    <button
                      type="button"
                      onClick={() => window.open(`https://www.sec.gov/cgi-bin/browse-edgar?CIK=${companyData.company?.cik}`, '_blank')}
                      className="w-full px-4 py-2 text-left bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                    >
                      View All SEC Filings
                    </button>
                    
                    {companyData.company?.ticker && (
                      <button
                        type="button"
                        onClick={() => window.open(`https://finance.yahoo.com/quote/${companyData.company.ticker}`, '_blank')}
                        className="w-full px-4 py-2 text-left bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                      >
                        View on Yahoo Finance
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Welcome State - Show when no search has been performed */}
          {!searchState.hasSearched && !loadingDetails && (
            <div className="max-w-4xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                {/* Feature Cards */}
                <div className="text-center p-6 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <MagnifyingGlassIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Company Intelligence
                  </h3>
                  <p className="text-gray-600">
                    Search public companies by name or ticker to access comprehensive business profiles and metrics.
                  </p>
                </div>

                <div className="text-center p-6 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Market Data
                  </h3>
                  <p className="text-gray-600">
                    Real-time stock prices, market capitalization, trading volume, and key financial indicators.
                  </p>
                </div>

                <div className="text-center p-6 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Regulatory Filings
                  </h3>
                  <p className="text-gray-600">
                    Direct access to SEC filings including quarterly reports, annual reports, and material events.
                  </p>
                </div>
              </div>

              {/* AI Analysis Feature Card */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200 shadow-sm p-8 mb-12">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    AI Investment Analysis
                  </h3>
                  <p className="text-gray-600 max-w-2xl mx-auto">
                    Get educational investment insights powered by artificial intelligence. Our AI analyzes technical indicators, risk factors, and market trends to provide educational perspectives on companies.
                  </p>
                  <div className="text-sm text-purple-600 mt-4 font-medium">
                    Educational insights • Not financial advice • Always consult professionals
                  </div>
                </div>
              </div>

              {/* Popular Searches */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-6 text-center">
                  Popular Searches
                </h3>
                <div className="flex flex-wrap justify-center gap-3">
                  {['TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'NVDA', 'META', 'BRK.A'].map((ticker) => (
                    <button
                      key={ticker}
                      type="button"
                      onClick={() => {
                        const searchInput = document.querySelector('input[type="text"]');
                        if (searchInput) {
                          searchInput.value = ticker;
                          searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                          setTimeout(() => {
                            searchInput.focus();
                            searchInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
                          }, 100);
                        }
                      }}
                      className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200 border border-blue-200"
                    >
                      {ticker}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;