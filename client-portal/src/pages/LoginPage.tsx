/**
 * Login Page
 * Microsoft Fluent Design inspired login with email/password and OAuth SSO
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Shield, ArrowRight, Mail, Lock, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export function LoginPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showEmailLogin, setShowEmailLogin] = useState(false);

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading('email');
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password,
      });

      // Store tokens
      localStorage.setItem('access_token', response.data.access_token);
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token);
      }

      // Store user data
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      // Navigate to firm dashboard
      navigate('/firm/dashboard');
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Login failed. Please check your credentials and try again.');
      }
      setLoading(null);
    }
  };

  const handleOAuthLogin = async (provider: 'microsoft' | 'google') => {
    setLoading(provider);
    setError('OAuth login is not yet configured. Please use email/password login.');
    setLoading(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-neutral-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(to right, rgba(0,120,212,0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0,120,212,0.05) 1px, transparent 1px)
          `,
          backgroundSize: '4rem 4rem'
        }} />
      </div>

      {/* Floating Orbs */}
      <motion.div
        className="absolute top-20 left-20 w-64 h-64 bg-primary-200 rounded-full blur-3xl opacity-20"
        animate={{
          y: [0, 30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-80 h-80 bg-accent-200 rounded-full blur-3xl opacity-20"
        animate={{
          y: [0, -40, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.1, 0.9, 0.2, 1] }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: 'spring',
              stiffness: 200,
              damping: 20,
              delay: 0.1
            }}
            className="inline-flex items-center justify-center w-16 h-16 bg-primary-500 rounded-fluent-lg mb-6 shadow-fluent-8"
          >
            <Building2 className="w-9 h-9 text-white" />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="text-display-large text-neutral-900 mb-3 font-semibold"
          >
            Welcome to Aura CPA
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
            className="text-subtitle text-neutral-600"
          >
            Access your professional accounting portal
          </motion.p>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.4, ease: [0.1, 0.9, 0.2, 1] }}
          className="fluent-card-elevated p-8 backdrop-blur-sm"
        >
          <div className="flex items-center gap-2 mb-6">
            <Shield className="w-5 h-5 text-primary-500" />
            <h2 className="text-title text-neutral-900">
              Sign in securely
            </h2>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-error-50 border border-error-200 rounded-fluent flex items-center gap-2 text-error-600"
            >
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-body">{error}</span>
            </motion.div>
          )}

          {showEmailLogin ? (
            /* Email/Password Login Form */
            <form onSubmit={handleEmailLogin} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-body-strong text-neutral-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="fluent-input pl-10"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-body-strong text-neutral-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                    className="fluent-input pl-10"
                  />
                </div>
              </div>

              <motion.button
                type="submit"
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                disabled={loading === 'email'}
                className="fluent-btn-primary w-full py-3"
              >
                {loading === 'email' ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </motion.button>

              <button
                type="button"
                onClick={() => setShowEmailLogin(false)}
                className="w-full text-center text-body text-primary-500 hover:text-primary-600 font-medium mt-4"
              >
                Back to other sign-in options
              </button>
            </form>
          ) : (
            /* OAuth and Email Options */
            <div className="space-y-3">
              {/* Microsoft 365 Login */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleOAuthLogin('microsoft')}
                disabled={loading !== null}
                className="fluent-reveal w-full flex items-center gap-4 px-5 py-4 bg-white border-2 border-neutral-200 rounded-fluent hover:border-primary-300 hover:shadow-fluent-4 active:scale-[0.98] transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                {loading === 'microsoft' ? (
                  <div className="w-6 h-6 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <svg className="w-6 h-6 flex-shrink-0" viewBox="0 0 23 23">
                      <path fill="#f35325" d="M0 0h11v11H0z" />
                      <path fill="#81bc06" d="M12 0h11v11H12z" />
                      <path fill="#05a6f0" d="M0 12h11v11H0z" />
                      <path fill="#ffba08" d="M12 12h11v11H12z" />
                    </svg>
                    <span className="text-body-strong text-neutral-900 flex-1 text-left">
                      Continue with Microsoft 365
                    </span>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                  </>
                )}
              </motion.button>

              {/* Google Business Login */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleOAuthLogin('google')}
                disabled={loading !== null}
                className="fluent-reveal w-full flex items-center gap-4 px-5 py-4 bg-white border-2 border-neutral-200 rounded-fluent hover:border-primary-300 hover:shadow-fluent-4 active:scale-[0.98] transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                {loading === 'google' ? (
                  <div className="w-6 h-6 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <svg className="w-6 h-6 flex-shrink-0" viewBox="0 0 24 24">
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
                    <span className="text-body-strong text-neutral-900 flex-1 text-left">
                      Continue with Google Workspace
                    </span>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                  </>
                )}
              </motion.button>

              {/* Divider */}
              <div className="flex items-center gap-4 my-4">
                <div className="flex-1 h-px bg-neutral-200" />
                <span className="text-caption text-neutral-500">or</span>
                <div className="flex-1 h-px bg-neutral-200" />
              </div>

              {/* Email Login Button */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setShowEmailLogin(true)}
                className="fluent-reveal w-full flex items-center gap-4 px-5 py-4 bg-white border-2 border-neutral-200 rounded-fluent hover:border-primary-300 hover:shadow-fluent-4 active:scale-[0.98] transition-all duration-150 group"
              >
                <Mail className="w-6 h-6 flex-shrink-0 text-neutral-600" />
                <span className="text-body-strong text-neutral-900 flex-1 text-left">
                  Sign in with Email
                </span>
                <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
              </motion.button>
            </div>
          )}

          <div className="mt-6 pt-6 border-t border-neutral-200">
            <p className="text-caption text-neutral-600 text-center mb-4">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-primary-500 hover:text-primary-600 font-semibold hover:underline transition-colors"
              >
                Create Account
              </button>
            </p>
            <p className="text-caption text-neutral-600 text-center leading-relaxed">
              By signing in, you agree to our{' '}
              <a href="/terms" className="text-primary-500 hover:text-primary-600 font-semibold hover:underline transition-colors">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-primary-500 hover:text-primary-600 font-semibold hover:underline transition-colors">
                Privacy Policy
              </a>
            </p>
          </div>
        </motion.div>

        {/* Help Text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.4 }}
          className="mt-6 text-center"
        >
          <p className="text-body text-neutral-600">
            Need assistance?{' '}
            <a
              href="mailto:support@aura-cpa.com"
              className="text-primary-500 hover:text-primary-600 font-semibold hover:underline transition-colors"
            >
              Contact Support
            </a>
          </p>
        </motion.div>

        {/* Security Badge */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.4 }}
          className="mt-8 flex items-center justify-center gap-2 text-caption text-neutral-500"
        >
          <Shield className="w-4 h-4" />
          <span>Enterprise-grade security & compliance</span>
        </motion.div>
      </motion.div>
    </div>
  );
}
