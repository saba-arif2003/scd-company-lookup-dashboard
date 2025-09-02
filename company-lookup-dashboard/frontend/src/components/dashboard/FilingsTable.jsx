import React, { useState, useMemo } from 'react';
import {
  DocumentTextIcon,
  ArrowTopRightOnSquareIcon,
  FunnelIcon,
  ChevronUpDownIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { formatters } from '../../utils/formatters';
import { FILING_FORMS } from '../../services/constants';

// Helper function to get filing badge color
const getFilingBadgeColor = (form) => {
  const config = formatters.filingForm(form);
  const colorMap = {
    'blue': 'filing-form-10k',
    'green': 'filing-form-10q', 
    'yellow': 'filing-form-8k',
    'gray': 'filing-form-other',
  };
  return colorMap[config.color] || 'filing-form-other';
};

const FilingsTable = ({ 
  filings = [], 
  loading = false, 
  className,
  showFilters = true,
  maxHeight = '400px' 
}) => {
  const [sortConfig, setSortConfig] = useState({ key: 'filing_date', direction: 'desc' });
  const [filterForm, setFilterForm] = useState('all');

  // Filter filings by form type
  const filteredFilings = useMemo(() => {
    if (filterForm === 'all') return filings;
    return filings.filter(filing => filing.form === filterForm);
  }, [filings, filterForm]);

  // Sort filings
  const sortedFilings = useMemo(() => {
    if (!sortConfig.key) return filteredFilings;

    return [...filteredFilings].sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      // Handle dates
      if (sortConfig.key === 'filing_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }

      // Handle strings
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue?.toLowerCase() || '';
      }

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [filteredFilings, sortConfig]);

  // Get unique form types for filter
  const availableFormTypes = useMemo(() => {
    const forms = [...new Set(filings.map(filing => filing.form))];
    return forms.sort();
  }, [filings]);

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const handleFilingClick = (filing) => {
    if (filing.filing_url) {
      window.open(filing.filing_url, '_blank', 'noopener,noreferrer');
    }
  };

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return <ChevronUpDownIcon className="w-4 h-4" />;
    }
    return sortConfig.direction === 'asc' 
      ? <ChevronUpIcon className="w-4 h-4" />
      : <ChevronDownIcon className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className={clsx('bg-white rounded-xl border border-gray-200 shadow-soft', className)}>
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="h-6 bg-gray-200 rounded animate-pulse w-32" />
            {showFilters && (
              <div className="h-8 bg-gray-200 rounded animate-pulse w-40" />
            )}
          </div>
        </div>
        <div className="p-6 space-y-4">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="grid grid-cols-4 gap-4">
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!filings || filings.length === 0) {
    return (
      <div className={clsx('bg-white rounded-xl border border-gray-200 shadow-soft', className)}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <DocumentTextIcon className="w-5 h-5 mr-2" />
            SEC Filings
          </h3>
        </div>
        <div className="p-12 text-center">
          <DocumentTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            No SEC Filings Found
          </h4>
          <p className="text-gray-600">
            No recent SEC filings are available for this company.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('bg-white rounded-xl border border-gray-200 shadow-soft', className)}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <DocumentTextIcon className="w-5 h-5 mr-2" />
            SEC Filings ({filteredFilings.length})
          </h3>

          {/* Filter Dropdown */}
          {showFilters && availableFormTypes.length > 0 && (
            <div className="flex items-center space-x-2">
              <FunnelIcon className="w-4 h-4 text-gray-400" />
              <select
                value={filterForm}
                onChange={(e) => setFilterForm(e.target.value)}
                className="text-sm border border-gray-300 rounded-md px-3 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Forms</option>
                {availableFormTypes.map(form => (
                  <option key={form} value={form}>
                    {form} {FILING_FORMS[form] ? `- ${FILING_FORMS[form].name}` : ''}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="filings-table-container" style={{ maxHeight }}>
        <table className="filings-table">
          <thead>
            <tr>
              <th>
                <button
                  type="button"
                  onClick={() => handleSort('form')}
                  className="flex items-center space-x-1 hover:text-gray-700 transition-colors duration-200"
                >
                  <span>Form</span>
                  {getSortIcon('form')}
                </button>
              </th>
              <th>
                <button
                  type="button"
                  onClick={() => handleSort('filing_date')}
                  className="flex items-center space-x-1 hover:text-gray-700 transition-colors duration-200"
                >
                  <span>Filed Date</span>
                  {getSortIcon('filing_date')}
                </button>
              </th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedFilings.map((filing, index) => (
              <tr key={filing.accession_number || index}>
                <td>
                  <span className={clsx(
                    'filing-form-badge',
                    getFilingBadgeColor(filing.form)
                  )}>
                    {filing.form}
                  </span>
                </td>
                
                <td>
                  <div className="text-gray-900">
                    {formatters.date(filing.filing_date)}
                  </div>
                  {filing.period_end_date && (
                    <div className="text-xs text-gray-500">
                      Period: {formatters.date(filing.period_end_date)}
                    </div>
                  )}
                </td>
                
                <td>
                  <div className="text-gray-900">
                    {filing.description || FILING_FORMS[filing.form]?.description || 'SEC Filing'}
                  </div>
                  {filing.file_size && (
                    <div className="text-xs text-gray-500">
                      Size: {formatters.fileSize(filing.file_size)}
                    </div>
                  )}
                </td>
                
                <td>
                  <button
                    type="button"
                    onClick={() => handleFilingClick(filing)}
                    className="filing-link inline-flex items-center text-sm font-medium"
                    title="View filing on SEC website"
                  >
                    View Filing
                    <ArrowTopRightOnSquareIcon className="w-3 h-3 ml-1" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer with summary info */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 rounded-b-xl">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            Showing {sortedFilings.length} of {filings.length} filings
          </div>
          
          {filings.length > 0 && (
            <div className="text-xs">
              Latest: {formatters.date(filings[0]?.filing_date)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Compact version for smaller spaces
export const FilingsTableCompact = ({ filings = [], className, maxItems = 3 }) => {
  const displayFilings = filings.slice(0, maxItems);

  if (!filings || filings.length === 0) {
    return (
      <div className={clsx('bg-white border border-gray-200 rounded-lg p-4', className)}>
        <div className="text-center">
          <DocumentTextIcon className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No recent filings</p>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('bg-white border border-gray-200 rounded-lg', className)}>
      <div className="px-4 py-3 border-b border-gray-200">
        <h4 className="text-sm font-semibold text-gray-900 flex items-center">
          <DocumentTextIcon className="w-4 h-4 mr-2" />
          Recent Filings
        </h4>
      </div>

      <div className="divide-y divide-gray-100">
        {displayFilings.map((filing, index) => (
          <div key={filing.accession_number || index} className="px-4 py-3 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className={clsx(
                  'filing-form-badge text-xs',
                  getFilingBadgeColor(filing.form)
                )}>
                  {filing.form}
                </span>
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {formatters.date(filing.filing_date)}
                  </div>
                  {filing.description && (
                    <div className="text-xs text-gray-500 truncate max-w-40">
                      {filing.description}
                    </div>
                  )}
                </div>
              </div>

              <button
                type="button"
                onClick={() => window.open(filing.filing_url, '_blank', 'noopener,noreferrer')}
                className="text-primary-600 hover:text-primary-800 transition-colors duration-200"
              >
                <ArrowTopRightOnSquareIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {filings.length > maxItems && (
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 rounded-b-lg">
          <p className="text-xs text-gray-500 text-center">
            +{filings.length - maxItems} more filings available
          </p>
        </div>
      )}
    </div>
  );
};

export default FilingsTable;