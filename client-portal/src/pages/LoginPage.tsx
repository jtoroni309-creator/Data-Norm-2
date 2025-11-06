/**
 * Login Page
 * Beautiful login page with OAuth SSO for Microsoft 365 and Google Business
 */

import { useState } from 'react';
import { authService } from '@/services/auth.service';
import { motion } from 'framer-motion';

export function LoginPage() {
  const [loading, setLoading] = useState<string | null>(null);

  const handleOAuthLogin = async (provider: 'microsoft' | 'google') => {
    setLoading(provider);
    try {
      await authService.initiateOAuth(provider);
    } catch (error) {
      console.error('OAuth login failed:', error);
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
            className="inline-flex items-center justify-center w-20 h-20 bg-gradient-primary rounded-2xl mb-4 shadow-lg"
          >
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </motion.div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to <span className="text-gradient">Aura Audit</span>
          </h1>
          <p className="text-gray-600">
            Access your client portal to manage your audit engagement
          </p>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card p-8"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
            Sign in with your business account
          </h2>

          <div className="space-y-4">
            {/* Microsoft 365 Login */}
            <button
              onClick={() => handleOAuthLogin('microsoft')}
              disabled={loading !== null}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:bg-gray-50 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
            >
              {loading === 'microsoft' ? (
                <div className="w-6 h-6 border-3 border-primary-600 border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <svg className="w-6 h-6" viewBox="0 0 23 23">
                    <path fill="#f35325" d="M0 0h11v11H0z" />
                    <path fill="#81bc06" d="M12 0h11v11H12z" />
                    <path fill="#05a6f0" d="M0 12h11v11H0z" />
                    <path fill="#ffba08" d="M12 12h11v11H12z" />
                  </svg>
                  <span className="font-semibold text-gray-700">
                    Continue with Microsoft 365
                  </span>
                </>
              )}
            </button>

            {/* Google Business Login */}
            <button
              onClick={() => handleOAuthLogin('google')}
              disabled={loading !== null}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:bg-gray-50 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
            >
              {loading === 'google' ? (
                <div className="w-6 h-6 border-3 border-primary-600 border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <svg className="w-6 h-6" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span className="font-semibold text-gray-700">
                    Continue with Google Business
                  </span>
                </>
              )}
            </button>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              By signing in, you agree to our{' '}
              <a href="/terms" className="text-primary-600 hover:text-primary-700 font-medium">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-primary-600 hover:text-primary-700 font-medium">
                Privacy Policy
              </a>
            </p>
          </div>
        </motion.div>

        {/* Help Text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-gray-600">
            Need help?{' '}
            <a
              href="mailto:support@aura-audit.com"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Contact Support
            </a>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
