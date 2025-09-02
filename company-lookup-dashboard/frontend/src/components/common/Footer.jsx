import React from 'react';
import { 
  ShieldCheckIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Brand Section */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="text-xl font-bold">FinanceHub</div>
          </div>
          <p className="text-gray-400 text-sm max-w-md mx-auto">
            Professional financial data and market intelligence platform for informed investment decisions.
          </p>
        </div>

        {/* Features Section */}
        <div className="border-t border-gray-800 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-3">
                <ShieldCheckIcon className="w-6 h-6 text-blue-400 mr-2" />
                <h4 className="font-semibold text-gray-300">Secure & Reliable</h4>
              </div>
              <p className="text-gray-400 text-sm">Bank-grade security with 99.9% uptime guarantee</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-3">
                <DocumentTextIcon className="w-6 h-6 text-green-400 mr-2" />
                <h4 className="font-semibold text-gray-300">Real-time Data</h4>
              </div>
              <p className="text-gray-400 text-sm">Live market data and SEC filings updated instantly</p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-3">
                <ChatBubbleLeftRightIcon className="w-6 h-6 text-purple-400 mr-2" />
                <h4 className="font-semibold text-gray-300">Expert Support</h4>
              </div>
              <p className="text-gray-400 text-sm">24/7 support from financial data specialists</p>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-gray-400 text-sm">
              © {currentYear} FinanceHub. All rights reserved.
            </div>
            
            <div className="text-gray-400 text-sm text-center md:text-right">
              <p>Data provided by SEC EDGAR and Yahoo Finance.</p>
              <p className="mt-1">For informational purposes only. Not investment advice.</p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;