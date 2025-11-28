/**
 * Registration Page
 * New user signup for CPA portal
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Shield, ArrowRight, Mail, Lock, AlertCircle, User, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export function RegisterPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'register' | 'success'>('register');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validation
    if (!fullName || !email || !password || !organizationName) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    try {
      // Step 1: Create organization
      const orgResponse = await axios.post(`${API_BASE_URL}/identity/admin/organizations`, {
        firm_name: organizationName,
        legal_name: organizationName,
        primary_contact_name: fullName,
        primary_contact_email: email,
        subscription_tier: 'professional',
        subscription_status: 'trial',
        max_users: 25
      });

      const organizationId = orgResponse.data.id;

      // Step 2: Register user with organization
      await axios.post(`${API_BASE_URL}/identity/auth/register`, {
        email,
        password,
        full_name: fullName,
        organization_id: organizationId,
        role: 'partner'
      });

      setStep('success');
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Registration failed. Please try again.');
      }
      setLoading(false);
    }
  };

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-neutral-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="fluent-card-elevated p-8 text-center backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
              className="inline-flex items-center justify-center w-16 h-16 bg-success-500 rounded-full mb-6"
            >
              <CheckCircle className="w-9 h-9 text-white" />
            </motion.div>
            <h1 className="text-title-large text-neutral-900 mb-3">Registration Successful!</h1>
            <p className="text-body text-neutral-600 mb-6">
              Your account has been created. You can now sign in to access your CPA portal.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="fluent-btn-primary w-full"
            >
              <ArrowRight className="w-5 h-5" />
              Sign In Now
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

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
            Register Your Firm
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
            className="text-subtitle text-neutral-600"
          >
            Create a new CPA firm account on Aura Audit AI
          </motion.p>
        </div>

        {/* Registration Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.4, ease: [0.1, 0.9, 0.2, 1] }}
          className="fluent-card-elevated p-8 backdrop-blur-sm"
        >
          <div className="flex items-center gap-2 mb-6">
            <Shield className="w-5 h-5 text-primary-500" />
            <h2 className="text-title text-neutral-900">
              Register your CPA firm
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

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label htmlFor="organizationName" className="block text-body-strong text-neutral-700 mb-2">
                Firm Name *
              </label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  id="organizationName"
                  type="text"
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  placeholder="Your CPA Firm Name"
                  required
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="fullName" className="block text-body-strong text-neutral-700 mb-2">
                Full Name *
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Smith"
                  required
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-body-strong text-neutral-700 mb-2">
                Email Address *
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@yourfirm.com"
                  required
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-body-strong text-neutral-700 mb-2">
                Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  required
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-body-strong text-neutral-700 mb-2">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  required
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <motion.button
              type="submit"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              disabled={loading}
              className="fluent-btn-primary w-full py-3"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>

          <div className="mt-6 pt-6 border-t border-neutral-200 space-y-4">
            <p className="text-caption text-neutral-600 text-center">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-primary-500 hover:text-primary-600 font-semibold hover:underline transition-colors"
              >
                Sign In
              </button>
            </p>
            <div className="p-3 bg-neutral-50 rounded-fluent border border-neutral-200">
              <p className="text-caption text-neutral-600 text-center">
                <strong>Been invited to join an existing firm?</strong>
                <br />
                Check your email for an invitation link from your firm administrator.
              </p>
            </div>
          </div>
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
