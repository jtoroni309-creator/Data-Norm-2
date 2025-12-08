/**
 * Register Page
 * Registration interface for invited R&D client users
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FlaskConical, Mail, Lock, User, Phone, ArrowRight, AlertCircle, CheckCircle, Building2 } from 'lucide-react';
import { useAuthStore } from '../store/auth';
import authService from '../services/auth.service';
import toast from 'react-hot-toast';

interface InvitationInfo {
  valid: boolean;
  study_id: string;
  study_name: string;
  company_name: string;
  tax_year: number;
  firm_name: string;
  email: string;
  name: string;
  expires_at: string;
  already_registered: boolean;
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { token: pathToken } = useParams();
  const [searchParams] = useSearchParams();
  const { login } = useAuthStore();

  const token = pathToken || searchParams.get('token') || '';

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invitation, setInvitation] = useState<InvitationInfo | null>(null);

  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Validate invitation on mount
  useEffect(() => {
    const validateInvitation = async () => {
      if (!token) {
        setError('No invitation token provided. Please use the link from your email.');
        setLoading(false);
        return;
      }

      try {
        const data = await authService.validateInvitation(token);
        setInvitation(data);
        setEmail(data.email);
        setFullName(data.name);

        if (data.already_registered) {
          setError('This email is already registered. Please sign in instead.');
        }
      } catch {
        setError('Invalid or expired invitation. Please contact your CPA firm for a new invitation.');
      } finally {
        setLoading(false);
      }
    };

    validateInvitation();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await authService.register({
        token,
        email,
        password,
        full_name: fullName,
        phone: phone || undefined,
      });

      login(response.user, response.access_token);
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (err: unknown) {
      if (err instanceof Error && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || 'Registration failed. Please try again.');
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Validating invitation...</p>
        </div>
      </div>
    );
  }

  if (!token || (error && !invitation)) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="fluent-card-elevated p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Invalid Invitation</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <Link to="/login" className="fluent-btn-primary">
              Go to Login
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background decorations */}
      <motion.div
        className="absolute top-20 left-20 w-64 h-64 bg-primary-200 rounded-full blur-3xl opacity-20"
        animate={{ y: [0, 30, 0] }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-80 h-80 bg-accent-200 rounded-full blur-3xl opacity-20"
        animate={{ y: [0, -40, 0] }}
        transition={{ duration: 10, repeat: Infinity }}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg relative z-10"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl mb-6 shadow-lg">
            <FlaskConical className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
          <p className="text-gray-600">Complete your registration to access the R&D Tax Credit Portal</p>
        </div>

        {/* Invitation Info Card */}
        {invitation && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6 p-4 bg-primary-50 border border-primary-200 rounded-xl"
          >
            <div className="flex items-start gap-3">
              <Building2 className="w-5 h-5 text-primary-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-primary-900">
                  Invited by {invitation.firm_name}
                </p>
                <p className="text-sm text-primary-700">
                  For: {invitation.company_name} - {invitation.tax_year} R&D Study
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Registration Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="fluent-card-elevated p-8"
        >
          {error && invitation && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="fullName" className="fluent-label">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  required
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="fluent-label">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  required
                  disabled={!!invitation?.email}
                  className="fluent-input pl-10 disabled:bg-gray-50 disabled:text-gray-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="phone" className="fluent-label">
                Phone Number <span className="text-gray-400">(optional)</span>
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="(555) 123-4567"
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="fluent-label">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a strong password"
                  required
                  minLength={8}
                  className="fluent-input pl-10"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">At least 8 characters</p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="fluent-label">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
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
              {confirmPassword && password === confirmPassword && (
                <p className="mt-1 text-xs text-green-600 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Passwords match
                </p>
              )}
            </div>

            <motion.button
              type="submit"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              disabled={submitting}
              className="fluent-btn-primary w-full py-3 mt-6"
            >
              {submitting ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-semibold">
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
