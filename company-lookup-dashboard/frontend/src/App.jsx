import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import Dashboard from './components/dashboard/Dashboard';
import LoadingSpinner from './components/common/LoadingSpinner';
import { ErrorToast } from './components/common/ErrorMessage';
import apiService from './services/api';
import { APP_INFO, FEATURES } from './services/constants';
import './styles/index.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [appHealth, setAppHealth] = useState({
    status: 'unknown',
    lastChecked: null,
    error: null,
  });

  // Initialize app and check health
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Simulate initialization delay for smooth loading experience
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check API health
        try {
          const healthResponse = await apiService.checkHealthSimple();
          setAppHealth({
            status: 'healthy',
            lastChecked: new Date(),
            error: null,
          });
          
          if (FEATURES.DEBUG_MODE) {
            console.log('✅ API Health Check:', healthResponse);
          }
        } catch (error) {
          console.warn('⚠️ API health check failed:', error);
          setAppHealth({
            status: 'degraded',
            lastChecked: new Date(),
            error: error.message,
          });
        }
        
      } catch (error) {
        console.error('❌ App initialization failed:', error);
        setAppHealth({
          status: 'error',
          lastChecked: new Date(),
          error: error.message,
        });
      } finally {
        setIsLoading(false);
      }
    };

    initializeApp();
  }, []);

  // Periodic health checks
  useEffect(() => {
    if (!FEATURES.DEBUG_MODE) return;

    const interval = setInterval(async () => {
      try {
        await apiService.checkHealthSimple();
        setAppHealth(prev => ({
          ...prev,
          status: 'healthy',
          lastChecked: new Date(),
          error: null,
        }));
      } catch (error) {
        setAppHealth(prev => ({
          ...prev,
          status: 'degraded',
          lastChecked: new Date(),
          error: error.message,
        }));
      }
    }, 5 * 60 * 1000); // Check every 5 minutes

    return () => clearInterval(interval);
  }, []);

  // Show loading screen during initialization
  if (isLoading) {
    return (
      <LoadingSpinner 
        fullScreen={true}
        text="Loading Company Lookup Dashboard..."
        color="primary"
        size="lg"
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1" id="main-content">
        <Dashboard />
      </main>

      {/* Footer */}
      <Footer />

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          success: {
            className: 'toast-success',
            iconTheme: {
              primary: '#22c55e',
              secondary: '#ffffff',
            },
          },
          error: {
            className: 'toast-error',
            iconTheme: {
              primary: '#ef4444',
              secondary: '#ffffff',
            },
          },
          loading: {
            className: 'toast-info',
          },
        }}
      />

      {/* Global Error Handler */}
      {appHealth.status === 'error' && appHealth.error && (
        <ErrorToast
          message={`Application Error: ${appHealth.error}`}
          onClose={() => setAppHealth(prev => ({ ...prev, error: null }))}
          autoClose={false}
        />
      )}

      {/* Accessibility Skip Link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-primary-600 text-white px-4 py-2 rounded-md"
      >
        Skip to main content
      </a>
    </div>
  );
}

// Error Boundary Component
class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error Boundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-strong p-8 text-center">
            <div className="w-16 h-16 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            
            <h1 className="text-xl font-bold text-gray-900 mb-2">
              Something went wrong
            </h1>
            
            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>

            <button
              onClick={() => window.location.reload()}
              className="w-full btn btn-primary"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Wrap App with Error Boundary
function AppWithErrorBoundary() {
  return (
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>
  );
}

export default AppWithErrorBoundary;