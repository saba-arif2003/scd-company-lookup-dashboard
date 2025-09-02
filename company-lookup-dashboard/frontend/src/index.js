import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { APP_INFO, FEATURES } from './services/constants';

// Remove initial loading screen
const removeInitialLoader = () => {
  const loader = document.getElementById('initial-loader');
  if (loader) {
    loader.style.opacity = '0';
    loader.style.transition = 'opacity 0.3s ease-out';
    setTimeout(() => loader.remove(), 300);
  }
};

// Console welcome message
const logWelcomeMessage = () => {
  if (FEATURES.DEBUG_MODE) {
    console.log(
      `%c🏢 ${APP_INFO.NAME} %cv${APP_INFO.VERSION}`,
      'background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;',
      'color: #64748b; font-weight: normal;'
    );
    console.log(
      `%c📊 Built with React + Tailwind CSS`,
      'color: #22c55e; font-weight: bold;'
    );
    console.log(
      `%c🔗 API Base URL: ${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1'}`,
      'color: #f59e0b;'
    );
    console.log(
      `%c🚀 Ready to search companies!`,
      'color: #8b5cf6; font-weight: bold;'
    );
  }
};

// Performance monitoring (development only)
const setupPerformanceMonitoring = () => {
  if (FEATURES.DEBUG_MODE && 'performance' in window) {
    // Log initial page load performance
    window.addEventListener('load', () => {
      const perfData = performance.getEntriesByType('navigation')[0];
      console.group('📈 Performance Metrics');
      console.log(`DOM Content Loaded: ${perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart}ms`);
      console.log(`Page Load Complete: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
      console.log(`Total Load Time: ${perfData.loadEventEnd - perfData.fetchStart}ms`);
      console.groupEnd();
    });

    // Monitor long tasks
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const longTasks = list.getEntries();
          longTasks.forEach((task) => {
            if (task.duration > 50) {
              console.warn(`🐌 Long Task detected: ${task.duration.toFixed(2)}ms`);
            }
          });
        });
        observer.observe({ entryTypes: ['longtask'] });
      } catch (error) {
        // PerformanceObserver might not be supported in all browsers
        console.warn('PerformanceObserver not supported');
      }
    }
  }
};

// Error handling for uncaught errors
const setupGlobalErrorHandling = () => {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    if (FEATURES.DEBUG_MODE) {
      console.error('Promise rejection details:', event);
    }
    
    // Prevent the default handling (which would log the error to console)
    event.preventDefault();
  });

  // Handle uncaught JavaScript errors
  window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error);
    
    if (FEATURES.DEBUG_MODE) {
      console.error('Error details:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      });
    }
  });
};

// Initialize React application
const initializeApp = () => {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  
  // Log successful initialization
  if (FEATURES.DEBUG_MODE) {
    console.log('✅ React application initialized successfully');
  }
};

// Check for required environment variables
const validateEnvironment = () => {
  const requiredEnvVars = [];
  const warnings = [];
  
  // Check for production-specific requirements
  if (process.env.NODE_ENV === 'production') {
    if (!process.env.REACT_APP_API_BASE_URL) {
      warnings.push('REACT_APP_API_BASE_URL not set - using default localhost');
    }
  }
  
  // Log warnings
  if (warnings.length > 0 && FEATURES.DEBUG_MODE) {
    console.group('⚠️ Environment Warnings');
    warnings.forEach(warning => console.warn(warning));
    console.groupEnd();
  }
  
  return requiredEnvVars.length === 0;
};

// Check browser compatibility
const checkBrowserCompatibility = () => {
  const requiredFeatures = [
    'fetch',
    'Promise',
    'URLSearchParams',
    'IntersectionObserver'
  ];
  
  const unsupportedFeatures = requiredFeatures.filter(feature => !(feature in window));
  
  if (unsupportedFeatures.length > 0) {
    console.error('❌ Unsupported browser features:', unsupportedFeatures);
    
    // Show compatibility warning
    const warningDiv = document.createElement('div');
    warningDiv.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #fef2f2;
        border-bottom: 1px solid #fecaca;
        padding: 12px;
        text-align: center;
        font-family: system-ui, sans-serif;
        color: #991b1b;
        z-index: 9999;
      ">
        <strong>Browser Compatibility Warning:</strong>
        Your browser may not support all features of this application.
        Please consider updating to a modern browser.
      </div>
    `;
    document.body.insertBefore(warningDiv, document.body.firstChild);
    
    return false;
  }
  
  return true;
};

// Application startup sequence
const startApp = async () => {
  try {
    // 1. Validate environment
    if (!validateEnvironment()) {
      throw new Error('Environment validation failed');
    }
    
    // 2. Check browser compatibility
    const isCompatible = checkBrowserCompatibility();
    if (!isCompatible && process.env.NODE_ENV === 'production') {
      // Still continue in development mode for testing
      console.warn('Browser compatibility issues detected');
    }
    
    // 3. Setup error handling
    setupGlobalErrorHandling();
    
    // 4. Setup performance monitoring
    setupPerformanceMonitoring();
    
    // 5. Remove initial loading screen
    removeInitialLoader();
    
    // 6. Initialize React app
    initializeApp();
    
    // 7. Log welcome message
    logWelcomeMessage();
    
  } catch (error) {
    console.error('❌ Application startup failed:', error);
    
    // Show fallback error screen
    document.getElementById('root').innerHTML = `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem;
        font-family: system-ui, sans-serif;
        background: #f9fafb;
      ">
        <div style="
          max-width: 32rem;
          background: white;
          border-radius: 0.75rem;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
          padding: 2rem;
          text-align: center;
        ">
          <div style="
            width: 4rem;
            height: 4rem;
            background: #fef2f2;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
          ">
            <svg style="width: 2rem; height: 2rem; color: #dc2626;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <h1 style="font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;">
            Application Failed to Load
          </h1>
          <p style="color: #6b7280; margin-bottom: 1.5rem;">
            We're sorry, but the application couldn't start properly. Please try refreshing the page.
          </p>
          <button 
            onclick="window.location.reload()" 
            style="
              background: #3b82f6;
              color: white;
              border: none;
              border-radius: 0.5rem;
              padding: 0.75rem 1.5rem;
              font-weight: 600;
              cursor: pointer;
              transition: background-color 0.2s;
            "
            onmouseover="this.style.backgroundColor='#2563eb'"
            onmouseout="this.style.backgroundColor='#3b82f6'"
          >
            Refresh Page
          </button>
        </div>
      </div>
    `;
  }
};

// Start the application
startApp();