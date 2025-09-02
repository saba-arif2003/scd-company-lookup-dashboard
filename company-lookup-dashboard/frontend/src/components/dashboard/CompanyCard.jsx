import React from 'react';
import { 
  BuildingOfficeIcon,
  GlobeAltIcon,
  MapPinIcon,
  UserGroupIcon,
  InformationCircleIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { formatters } from '../../utils/formatters';

const CompanyCard = ({ company, className, showDetails = true }) => {
  if (!company) {
    return null;
  }

  const {
    name,
    ticker,
    cik,
    exchange,
    industry,
    sector,
    description,
    website,
    headquarters,
    market_cap,
    employees,
  } = company;

  // Generate company logo placeholder
  const getCompanyInitials = (companyName) => {
    return companyName
      ?.split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2) || '??';
  };

  const handleWebsiteClick = () => {
    if (website) {
      window.open(website, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className={clsx('company-card', className)}>
      {/* Header */}
      <div className="company-card-header">
        <div className="flex items-start space-x-4">
          {/* Company Logo Placeholder */}
          <div className="company-logo flex-shrink-0">
            {getCompanyInitials(name)}
          </div>

          {/* Company Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="min-w-0 flex-1">
                <h2 className="text-xl font-bold text-gray-900 truncate">
                  {formatters.companyName(name)}
                </h2>
                
                <div className="flex items-center space-x-3 mt-1">
                  {ticker && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                      {formatters.ticker(ticker)}
                    </span>
                  )}
                  
                  {exchange && (
                    <span className="text-sm text-gray-600">
                      {exchange}
                    </span>
                  )}
                </div>
              </div>

              {/* CIK */}
              {cik && (
                <div className="text-right flex-shrink-0">
                  <div className="text-xs text-gray-500">CIK</div>
                  <div className="text-sm font-mono text-gray-900">{cik}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="company-card-body space-y-4">
        {/* Basic Info Grid */}
        <div className="grid grid-cols-2 gap-4">
          {industry && (
            <div>
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Industry
              </div>
              <div className="text-sm text-gray-900 mt-1">
                {industry}
              </div>
            </div>
          )}

          {sector && (
            <div>
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sector
              </div>
              <div className="text-sm text-gray-900 mt-1">
                {sector}
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

          {employees && (
            <div>
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Employees
              </div>
              <div className="text-sm text-gray-900 mt-1">
                {formatters.largeNumber(employees)}
              </div>
            </div>
          )}
        </div>

        {/* Location and Website */}
        {(headquarters || website) && (
          <div className="space-y-3 pt-2 border-t border-gray-100">
            {headquarters && (
              <div className="flex items-center space-x-2">
                <MapPinIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <span className="text-sm text-gray-600">{headquarters}</span>
              </div>
            )}

            {website && (
              <button
                type="button"
                onClick={handleWebsiteClick}
                className="flex items-center space-x-2 text-primary-600 hover:text-primary-800 transition-colors duration-200"
              >
                <GlobeAltIcon className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm font-medium truncate">{website}</span>
                <ArrowTopRightOnSquareIcon className="w-3 h-3 flex-shrink-0" />
              </button>
            )}
          </div>
        )}

        {/* Description */}
        {description && showDetails && (
          <div className="pt-3 border-t border-gray-100">
            <div className="flex items-start space-x-2">
              <InformationCircleIcon className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                  About
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {formatters.truncateText(description, 200)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Key Metrics (if available) */}
        {showDetails && (market_cap || employees) && (
          <div className="pt-3 border-t border-gray-100">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {market_cap && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <BuildingOfficeIcon className="w-4 h-4 text-primary-500" />
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Value
                    </div>
                  </div>
                  <div className="text-lg font-bold text-gray-900 mt-1">
                    {formatters.marketCap(market_cap)}
                  </div>
                </div>
              )}

              {employees && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <UserGroupIcon className="w-4 h-4 text-success-500" />
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Workforce
                    </div>
                  </div>
                  <div className="text-lg font-bold text-gray-900 mt-1">
                    {formatters.largeNumber(employees)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Skeleton loading state for CompanyCard
export const CompanyCardSkeleton = ({ className }) => (
  <div className={clsx('company-card', className)}>
    <div className="company-card-header">
      <div className="flex items-start space-x-4">
        <div className="w-12 h-12 bg-gray-200 rounded-lg animate-pulse" />
        <div className="flex-1 space-y-2">
          <div className="h-6 bg-gray-200 rounded animate-pulse w-3/4" />
          <div className="flex space-x-2">
            <div className="h-5 bg-gray-200 rounded-full animate-pulse w-16" />
            <div className="h-5 bg-gray-200 rounded animate-pulse w-20" />
          </div>
        </div>
        <div className="space-y-1">
          <div className="h-3 bg-gray-200 rounded animate-pulse w-8" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-12" />
        </div>
      </div>
    </div>

    <div className="company-card-body space-y-4">
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="space-y-2">
            <div className="h-3 bg-gray-200 rounded animate-pulse w-16" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-20" />
          </div>
        ))}
      </div>
      
      <div className="pt-2 border-t border-gray-100 space-y-3">
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
      </div>
    </div>
  </div>
);

// Compact version for search results
export const CompanyCardCompact = ({ company, onClick, className }) => {
  if (!company) return null;

  const { name, ticker, exchange, industry } = company;

  return (
    <button
      type="button"
      onClick={() => onClick?.(company)}
      className={clsx(
        'w-full text-left p-4 bg-white border border-gray-200 rounded-lg',
        'hover:border-primary-300 hover:shadow-md transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-20',
        className
      )}
    >
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600 font-bold text-sm flex-shrink-0">
          {formatters.companyName(name)
            ?.split(' ')
            .map(word => word.charAt(0))
            .join('')
            .toUpperCase()
            .slice(0, 2) || '??'}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">
            {formatters.companyName(name, 40)}
          </h3>
          
          <div className="flex items-center space-x-2 mt-1">
            {ticker && (
              <span className="text-sm font-medium text-primary-600">
                {formatters.ticker(ticker)}
              </span>
            )}
            
            {exchange && (
              <>
                <span className="text-gray-300">•</span>
                <span className="text-sm text-gray-600">{exchange}</span>
              </>
            )}
            
            {industry && (
              <>
                <span className="text-gray-300">•</span>
                <span className="text-sm text-gray-500 truncate">{industry}</span>
              </>
            )}
          </div>
        </div>

        <ArrowTopRightOnSquareIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
      </div>
    </button>
  );
};

export default CompanyCard;