import React from 'react';
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { formatters } from '../../utils/formatters';

const StockCard = ({ 
  stockData, 
  className, 
  showExtendedData = false,
  onViewDetails 
}) => {
  if (!stockData) {
    return null;
  }

  // Handle both StockQuote and StockData formats
  const quote = stockData.quote || stockData;
  const {
    symbol,
    price,
    currency = 'USD',
    change,
    change_percent,
    volume,
    market_cap,
    last_updated,
    market_state
  } = quote;

  // Extended data (only available in StockData format)
  const {
    open_price,
    high_price,
    low_price,
    previous_close,
    fifty_two_week_high,
    fifty_two_week_low,
    pe_ratio,
    eps,
    dividend_yield,
    beta
  } = stockData;

  // Format stock change
  const stockChange = formatters.stockChange(change, change_percent);

  // Determine market state display
  const getMarketStateInfo = (state) => {
    const stateMap = {
      'REGULAR': { text: 'Market Open', color: 'text-success-600', bgColor: 'bg-success-100' },
      'CLOSED': { text: 'Market Closed', color: 'text-gray-600', bgColor: 'bg-gray-100' },
      'PRE': { text: 'Pre-Market', color: 'text-warning-600', bgColor: 'bg-warning-100' },
      'POST': { text: 'After Hours', color: 'text-warning-600', bgColor: 'bg-warning-100' },
    };
    
    return stateMap[state] || stateMap.CLOSED;
  };

  const marketInfo = getMarketStateInfo(market_state);

  return (
    <div className={clsx('stock-card', className)}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <CurrencyDollarIcon className="w-6 h-6 text-white" />
            </div>
            
            <div>
              <h3 className="text-lg font-bold text-gray-900">
                {formatters.ticker(symbol)}
              </h3>
              <div className="text-sm text-gray-600">Stock Quote</div>
            </div>
          </div>

          {/* Market State */}
          <div className={clsx(
            'px-2.5 py-1 rounded-full text-xs font-medium',
            marketInfo.bgColor,
            marketInfo.color
          )}>
            {marketInfo.text}
          </div>
        </div>
      </div>

      {/* Main Price Section */}
      <div className="px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          {/* Current Price */}
          <div>
            <div className="text-3xl font-bold text-gray-900">
              {formatters.currency(price, { currency })}
            </div>
            
            {/* Price Change */}
            <div className="flex items-center space-x-2 mt-2">
              <div className={clsx(
                'stock-change-badge flex items-center space-x-1',
                {
                  'stock-change-positive': stockChange.isPositive,
                  'stock-change-negative': stockChange.isNegative,
                  'stock-change-neutral': stockChange.isNeutral,
                }
              )}>
                {stockChange.isPositive && (
                  <ArrowTrendingUpIcon className="w-3 h-3" />
                )}
                {stockChange.isNegative && (
                  <ArrowTrendingDownIcon className="w-3 h-3" />
                )}
                <span className="text-sm font-medium">
                  {stockChange.value}
                </span>
              </div>
              
              <div className={clsx(
                'stock-change-badge',
                {
                  'stock-change-positive': stockChange.isPositive,
                  'stock-change-negative': stockChange.isNegative,
                  'stock-change-neutral': stockChange.isNeutral,
                }
              )}>
                <span className="text-sm font-medium">
                  {stockChange.percent}
                </span>
              </div>
            </div>
          </div>

          {/* View Details Button */}
          {onViewDetails && (
            <button
              type="button"
              onClick={onViewDetails}
              className="btn btn-secondary btn-sm inline-flex items-center"
            >
              <EyeIcon className="w-4 h-4 mr-1" />
              Details
            </button>
          )}
        </div>

        {/* Trading Info */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {volume && (
            <div>
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Volume
              </div>
              <div className="text-sm font-semibold text-gray-900 mt-1">
                {formatters.volume(volume)}
              </div>
            </div>
          )}

          {market_cap && (
            <div>
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Market Cap
              </div>
              <div className="text-sm font-semibold text-gray-900 mt-1">
                {formatters.marketCap(market_cap)}
              </div>
            </div>
          )}
        </div>

        {/* Extended Data */}
        {showExtendedData && (
          <div className="space-y-4 pt-4 border-t border-gray-100">
            {/* Price Range */}
            {(high_price || low_price || open_price || previous_close) && (
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  Today's Range
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  {open_price && (
                    <div>
                      <div className="text-xs text-gray-500">Open</div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatters.currency(open_price, { currency })}
                      </div>
                    </div>
                  )}
                  
                  {previous_close && (
                    <div>
                      <div className="text-xs text-gray-500">Prev. Close</div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatters.currency(previous_close, { currency })}
                      </div>
                    </div>
                  )}
                  
                  {high_price && (
                    <div>
                      <div className="text-xs text-gray-500">Day High</div>
                      <div className="text-sm font-medium text-success-600">
                        {formatters.currency(high_price, { currency })}
                      </div>
                    </div>
                  )}
                  
                  {low_price && (
                    <div>
                      <div className="text-xs text-gray-500">Day Low</div>
                      <div className="text-sm font-medium text-danger-600">
                        {formatters.currency(low_price, { currency })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 52-Week Range */}
            {(fifty_two_week_high || fifty_two_week_low) && (
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  52-Week Range
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  {fifty_two_week_low && (
                    <div>
                      <div className="text-xs text-gray-500">52W Low</div>
                      <div className="text-sm font-medium text-danger-600">
                        {formatters.currency(fifty_two_week_low, { currency })}
                      </div>
                    </div>
                  )}
                  
                  {fifty_two_week_high && (
                    <div>
                      <div className="text-xs text-gray-500">52W High</div>
                      <div className="text-sm font-medium text-success-600">
                        {formatters.currency(fifty_two_week_high, { currency })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Financial Metrics */}
            {(pe_ratio || eps || dividend_yield || beta) && (
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  Key Metrics
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  {pe_ratio && (
                    <div>
                      <div className="text-xs text-gray-500">P/E Ratio</div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatters.peRatio(pe_ratio)}
                      </div>
                    </div>
                  )}
                  
                  {eps && (
                    <div>
                      <div className="text-xs text-gray-500">EPS</div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatters.currency(eps, { currency })}
                      </div>
                    </div>
                  )}
                  
                  {dividend_yield && (
                    <div>
                      <div className="text-xs text-gray-500">Dividend Yield</div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatters.percentage(dividend_yield)}
                      </div>
                    </div>
                  )}
                  
                  {beta && (
                    <div>
                      <div className="text-xs text-gray-500">Beta</div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatters.number(beta)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Last Updated */}
        {last_updated && (
          <div className="flex items-center justify-center space-x-2 pt-4 mt-4 border-t border-gray-100">
            <ClockIcon className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-500">
              Updated {formatters.relativeTime(last_updated)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

// Skeleton loading state
export const StockCardSkeleton = ({ className }) => (
  <div className={clsx('stock-card', className)}>
    <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-200 rounded-lg animate-pulse" />
          <div className="space-y-1">
            <div className="h-5 bg-gray-200 rounded animate-pulse w-16" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-20" />
          </div>
        </div>
        <div className="h-6 bg-gray-200 rounded-full animate-pulse w-24" />
      </div>
    </div>

    <div className="px-6 py-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-32" />
          <div className="flex space-x-2">
            <div className="h-6 bg-gray-200 rounded-full animate-pulse w-20" />
            <div className="h-6 bg-gray-200 rounded-full animate-pulse w-16" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="space-y-1">
            <div className="h-3 bg-gray-200 rounded animate-pulse w-16" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-20" />
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Compact version for lists
export const StockCardCompact = ({ stockData, className, onClick }) => {
  if (!stockData) return null;

  const quote = stockData.quote || stockData;
  const { symbol, price, currency, change, change_percent } = quote;
  const stockChange = formatters.stockChange(change, change_percent);

  return (
    <div className={clsx(
      'flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200',
      onClick && 'cursor-pointer hover:border-primary-300',
      className
    )} onClick={onClick}>
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
          <ChartBarIcon className="w-4 h-4 text-blue-600" />
        </div>
        <div>
          <div className="font-semibold text-gray-900">
            {formatters.ticker(symbol)}
          </div>
          <div className="text-sm text-gray-500">Stock</div>
        </div>
      </div>

      <div className="text-right">
        <div className="font-semibold text-gray-900">
          {formatters.currency(price, { currency })}
        </div>
        <div className={clsx(
          'text-sm font-medium',
          {
            'text-success-600': stockChange.isPositive,
            'text-danger-600': stockChange.isNegative,
            'text-gray-600': stockChange.isNeutral,
          }
        )}>
          {stockChange.percent}
        </div>
      </div>
    </div>
  );
};

export default StockCard;