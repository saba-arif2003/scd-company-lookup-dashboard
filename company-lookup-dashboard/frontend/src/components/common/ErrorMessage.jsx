import React from 'react';
import { 
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

const ErrorMessage = ({ 
  title,
  message, 
  type = 'error',
  onRetry,
  onDismiss,
  retryText = 'Try Again',
  dismissText = 'Dismiss',
  showIcon = true,
  className,
  fullWidth = true,
  compact = false
}) => {
  // Type configurations
  const typeConfig = {
    error: {
      icon: XCircleIcon,
      bgColor: 'bg-danger-50',
      borderColor: 'border-danger-200',
      iconColor: 'text-danger-400',
      titleColor: 'text-danger-900',
      messageColor: 'text-danger-700',
      buttonColor: 'btn-danger',
    },
    warning: {
      icon: ExclamationTriangleIcon,
      bgColor: 'bg-warning-50',
      borderColor: 'border-warning-200',
      iconColor: 'text-warning-400',
      titleColor: 'text-warning-900',
      messageColor: 'text-warning-700',
      buttonColor: 'btn-warning',
    },
    info: {
      icon: InformationCircleIcon,
      bgColor: 'bg-primary-50',
      borderColor: 'border-primary-200',
      iconColor: 'text-primary-400',
      titleColor: 'text-primary-900',
      messageColor: 'text-primary-700',
      buttonColor: 'btn-primary',
    },
    success: {
      icon: ExclamationCircleIcon,
      bgColor: 'bg-success-50',
      borderColor: 'border-success-200',
      iconColor: 'text-success-400',
      titleColor: 'text-success-900',
      messageColor: 'text-success-700',
      buttonColor: 'btn-success',
    },
  };

  const config = typeConfig[type] || typeConfig.error;
  const Icon = config.icon;

  const containerClasses = clsx(
    'rounded-xl border shadow-sm',
    config.bgColor,
    config.borderColor,
    {
      'p-6': !compact,
      'p-4': compact,
      'w-full': fullWidth,
      'max-w-lg': !fullWidth,
    },
    className
  );

  return (
    <div className={containerClasses}>
      <div className="flex">
        {/* Icon */}
        {showIcon && (
          <div className="flex-shrink-0">
            <Icon className={clsx('w-5 h-5', config.iconColor)} />
          </div>
        )}

        {/* Content */}
        <div className={clsx('flex-1', showIcon && 'ml-3')}>
          {/* Title */}
          {title && (
            <h3 className={clsx(
              'font-semibold',
              compact ? 'text-sm' : 'text-base',
              config.titleColor
            )}>
              {title}
            </h3>
          )}

          {/* Message */}
          {message && (
            <div className={clsx(
              config.messageColor,
              compact ? 'text-sm' : 'text-sm',
              title && (compact ? 'mt-1' : 'mt-2')
            )}>
              {typeof message === 'string' ? (
                <p>{message}</p>
              ) : (
                message
              )}
            </div>
          )}

          {/* Actions */}
          {(onRetry || onDismiss) && (
            <div className={clsx(
              'flex flex-wrap gap-2',
              (title || message) && (compact ? 'mt-3' : 'mt-4')
            )}>
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className={clsx(
                    'btn',
                    compact ? 'btn-sm' : '',
                    config.buttonColor,
                    'inline-flex items-center'
                  )}
                >
                  <ArrowPathIcon className={clsx(
                    compact ? 'w-3 h-3' : 'w-4 h-4',
                    'mr-1'
                  )} />
                  {retryText}
                </button>
              )}

              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className={clsx(
                    'btn btn-secondary',
                    compact ? 'btn-sm' : '',
                    'inline-flex items-center'
                  )}
                >
                  <XMarkIcon className={clsx(
                    compact ? 'w-3 h-3' : 'w-4 h-4',
                    'mr-1'
                  )} />
                  {dismissText}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Dismiss button (top-right) */}
        {onDismiss && !compact && (
          <div className="flex-shrink-0 ml-4">
            <button
              type="button"
              onClick={onDismiss}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <span className="sr-only">Dismiss</span>
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Specialized error components
export const NetworkError = ({ onRetry, onDismiss }) => (
  <ErrorMessage
    type="error"
    title="Network Error"
    message="Unable to connect to the server. Please check your internet connection and try again."
    onRetry={onRetry}
    onDismiss={onDismiss}
  />
);

export const NotFoundError = ({ resource = 'resource', onRetry, onDismiss }) => (
  <ErrorMessage
    type="warning"
    title={`${resource} Not Found`}
    message={`The ${resource.toLowerCase()} you're looking for could not be found. It may have been moved or deleted.`}
    onRetry={onRetry}
    onDismiss={onDismiss}
    retryText="Search Again"
  />
);

export const RateLimitError = ({ retryAfter, onDismiss }) => {
  const message = retryAfter 
    ? `Too many requests. Please wait ${retryAfter} seconds before trying again.`
    : 'Too many requests. Please wait a moment before trying again.';

  return (
    <ErrorMessage
      type="warning"
      title="Rate Limit Exceeded"
      message={message}
      onDismiss={onDismiss}
    />
  );
};

export const ServerError = ({ onRetry, onDismiss }) => (
  <ErrorMessage
    type="error"
    title="Server Error"
    message="Something went wrong on our end. Our team has been notified and is working to fix this issue."
    onRetry={onRetry}
    onDismiss={onDismiss}
  />
);

export const ValidationError = ({ errors, onDismiss }) => {
  const errorList = Array.isArray(errors) ? errors : [errors];
  
  return (
    <ErrorMessage
      type="warning"
      title="Validation Error"
      message={
        <div>
          <p className="mb-2">Please correct the following issues:</p>
          <ul className="list-disc list-inside space-y-1">
            {errorList.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      }
      onDismiss={onDismiss}
    />
  );
};

// Empty state component
export const EmptyState = ({ 
  title,
  message,
  icon: Icon = ExclamationTriangleIcon,
  action,
  actionText = 'Get Started',
  className 
}) => (
  <div className={clsx(
    'text-center py-12 px-6',
    className
  )}>
    <Icon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
    <h3 className="text-lg font-semibold text-gray-900 mb-2">
      {title}
    </h3>
    <p className="text-gray-600 mb-6 max-w-sm mx-auto">
      {message}
    </p>
    {action && (
      <button
        type="button"
        onClick={action}
        className="btn btn-primary"
      >
        {actionText}
      </button>
    )}
  </div>
);

// Inline error for form fields
export const FieldError = ({ error, className }) => {
  if (!error) return null;

  return (
    <p className={clsx(
      'text-sm text-danger-600 mt-1',
      className
    )}>
      {error}
    </p>
  );
};

// Toast-style error notification
export const ErrorToast = ({ 
  message, 
  onClose, 
  autoClose = true,
  duration = 5000 
}) => {
  React.useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose, duration]);

  return (
    <div className="fixed top-4 right-4 max-w-sm w-full bg-white border border-danger-200 rounded-xl shadow-strong z-50 animate-slide-down">
      <div className="p-4">
        <div className="flex items-start">
          <XCircleIcon className="w-5 h-5 text-danger-400 flex-shrink-0 mt-0.5" />
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-danger-900">
              Error
            </p>
            <p className="text-sm text-danger-700 mt-1">
              {message}
            </p>
          </div>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="ml-4 text-danger-400 hover:text-danger-600 transition-colors duration-200"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;