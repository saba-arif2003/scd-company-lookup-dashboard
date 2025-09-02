import React from 'react';
import clsx from 'clsx';

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'primary', 
  text, 
  centered = true,
  fullScreen = false,
  overlay = false 
}) => {
  // Size mappings
  const sizeClasses = {
    xs: 'w-4 h-4 border-2',
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-4',
    lg: 'w-12 h-12 border-4',
    xl: 'w-16 h-16 border-4',
  };

  // Color mappings
  const colorClasses = {
    primary: 'border-primary-200 border-t-primary-600',
    secondary: 'border-gray-200 border-t-gray-600',
    white: 'border-gray-300 border-t-white',
    success: 'border-success-200 border-t-success-600',
    danger: 'border-danger-200 border-t-danger-600',
    warning: 'border-warning-200 border-t-warning-600',
  };

  const spinnerClasses = clsx(
    'animate-spin rounded-full',
    sizeClasses[size],
    colorClasses[color]
  );

  const textColorClasses = {
    primary: 'text-primary-600',
    secondary: 'text-gray-600',
    white: 'text-white',
    success: 'text-success-600',
    danger: 'text-danger-600',
    warning: 'text-warning-600',
  };

  const content = (
    <div className={clsx(
      'flex flex-col items-center space-y-3',
      centered && !fullScreen && 'justify-center',
      fullScreen && 'min-h-screen justify-center',
    )}>
      <div className={spinnerClasses} />
      {text && (
        <div className={clsx(
          'text-sm font-medium',
          textColorClasses[color]
        )}>
          {text}
        </div>
      )}
    </div>
  );

  // Full screen loading
  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 bg-white">
        {content}
      </div>
    );
  }

  // Overlay loading
  if (overlay) {
    return (
      <div className="absolute inset-0 z-10 bg-white bg-opacity-75 backdrop-blur-sm">
        {content}
      </div>
    );
  }

  // Regular loading
  return content;
};

// Skeleton loading components
export const SkeletonLine = ({ width = 'full', height = '4' }) => (
  <div className={`h-${height} bg-gray-200 rounded animate-pulse w-${width}`} />
);

export const SkeletonCard = ({ lines = 3, showAvatar = false }) => (
  <div className="skeleton-card">
    {showAvatar && (
      <div className="flex items-center space-x-3 mb-4">
        <div className="skeleton-avatar" />
        <div className="flex-1">
          <SkeletonLine width="1/2" />
        </div>
      </div>
    )}
    {Array.from({ length: lines }).map((_, index) => (
      <SkeletonLine 
        key={index} 
        width={index === lines - 1 ? '2/3' : 'full'} 
      />
    ))}
  </div>
);

export const SkeletonTable = ({ rows = 5, columns = 4 }) => (
  <div className="space-y-3">
    {/* Header */}
    <div className="grid grid-cols-4 gap-4">
      {Array.from({ length: columns }).map((_, index) => (
        <SkeletonLine key={index} width="3/4" />
      ))}
    </div>
    
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="grid grid-cols-4 gap-4">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <SkeletonLine 
            key={colIndex} 
            width={colIndex === 0 ? 'full' : '2/3'} 
          />
        ))}
      </div>
    ))}
  </div>
);

// Loading states for specific components
export const SearchLoading = () => (
  <LoadingSpinner 
    size="sm" 
    color="primary" 
    text="Searching companies..." 
    centered={true}
  />
);

export const CompanyLoading = () => (
  <div className="space-y-6">
    <SkeletonCard lines={2} showAvatar={true} />
    <SkeletonCard lines={4} />
    <SkeletonTable rows={3} columns={3} />
  </div>
);

export const ChartLoading = () => (
  <div className="chart-container">
    <div className="chart-header">
      <SkeletonLine width="1/3" />
    </div>
    <div className="h-64 bg-gray-100 rounded animate-pulse flex items-center justify-center">
      <LoadingSpinner size="lg" color="secondary" />
    </div>
  </div>
);

// Button loading state
export const ButtonLoading = ({ size = 'md' }) => {
  const sizeMap = {
    sm: 'xs',
    md: 'sm',
    lg: 'md',
  };
  
  return (
    <LoadingSpinner 
      size={sizeMap[size]} 
      color="white" 
      centered={false} 
    />
  );
};

export default LoadingSpinner;