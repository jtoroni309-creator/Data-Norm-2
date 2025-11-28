/**
 * Accept Invitation Page
 * Dedicated page for users who have been invited to join an organization
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UserPlus,
  Shield,
  ArrowRight,
  Lock,
  AlertCircle,
  User,
  CheckCircle,
  Mail,
  Building2,
  Eye,
  EyeOff,
  Check,
  X,
  Clock,
  Loader2
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

interface InvitationDetails {
  email: string;
  organization_name: string;
  role: string;
  invited_by: string;
  expires_at: string;
}

interface PasswordRequirement {
  label: string;
  test: (password: string) => boolean;
}

const passwordRequirements: PasswordRequirement[] = [
  { label: 'At least 8 characters', test: (p) => p.length >= 8 },
  { label: 'One uppercase letter', test: (p) => /[A-Z]/.test(p) },
  { label: 'One lowercase letter', test: (p) => /[a-z]/.test(p) },
  { label: 'One number', test: (p) => /\d/.test(p) },
];

const getRoleDisplayName = (role: string) => {
  const roleMap: Record<string, string> = {
    partner: 'Partner',
    manager: 'Manager',
    senior: 'Senior Associate',
    staff: 'Staff',
    qc_reviewer: 'QC Reviewer',
    client_contact: 'Client Contact'
  };
  return roleMap[role] || role;
};

export function AcceptInvitation() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'loading' | 'form' | 'success' | 'expired' | 'invalid'>('loading');
  const [invitation, setInvitation] = useState<InvitationDetails | null>(null);

  useEffect(() => {
    if (!token) {
      setStep('invalid');
      setValidating(false);
      return;
    }
    validateToken();
  }, [token]);

  const validateToken = async () => {
    try {
      setValidating(true);
      const response = await axios.get(`${API_BASE_URL}/identity/invitations/validate`, {
        params: { token }
      });
      setInvitation(response.data);
      setStep('form');
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 410) {
          setStep('expired');
        } else {
          setStep('invalid');
        }
      } else {
        setStep('invalid');
      }
    } finally {
      setValidating(false);
    }
  };

  const handleAcceptInvitation = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!fullName.trim()) {
      setError('Please enter your full name');
      setLoading(false);
      return;
    }

    if (!passwordRequirements.every(req => req.test(password))) {
      setError('Password does not meet all requirements');
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/identity/invitations/accept`, {
        token,
        full_name: fullName.trim(),
        password
      });

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
      }
      setStep('success');
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to create account. Please try again.');
      }
      setLoading(false);
    }
  };

  const getPasswordStrength = () => {
    const passed = passwordRequirements.filter(req => req.test(password)).length;
    if (passed === 0) return { level: 0, label: '', color: '' };
    if (passed === 1) return { level: 1, label: 'Weak', color: 'bg-red-500' };
    if (passed === 2) return { level: 2, label: 'Fair', color: 'bg-orange-500' };
    if (passed === 3) return { level: 3, label: 'Good', color: 'bg-yellow-500' };
    return { level: 4, label: 'Strong', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength();

  // Loading state
  if (validating || step === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Validating your invitation...</p>
        </div>
      </div>
    );
  }

  // Invalid token
  if (step === 'invalid') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-6">
            <X className="w-9 h-9 text-red-500" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">Invalid Invitation</h1>
          <p className="text-gray-600 mb-6">
            This invitation link is invalid or has already been used. Please contact the person who invited you to request a new invitation.
          </p>
          <button onClick={() => navigate('/login')} className="btn-secondary w-full">
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Expired token
  if (step === 'expired') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-6">
            <Clock className="w-9 h-9 text-yellow-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">Invitation Expired</h1>
          <p className="text-gray-600 mb-6">
            This invitation has expired. Invitations are valid for 7 days. Please contact the person who invited you to request a new invitation.
          </p>
          <button onClick={() => navigate('/login')} className="btn-secondary w-full">
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Success state
  if (step === 'success') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50 flex items-center justify-center p-4">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-md">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
              className="inline-flex items-center justify-center w-16 h-16 bg-green-500 rounded-full mb-6"
            >
              <CheckCircle className="w-9 h-9 text-white" />
            </motion.div>
            <h1 className="text-2xl font-bold text-gray-900 mb-3">Welcome to the Team!</h1>
            <p className="text-gray-600 mb-2">Your account has been created successfully.</p>
            {invitation && (
              <p className="text-gray-600 mb-6">
                You've joined <strong>{invitation.organization_name}</strong> as a <strong>{getRoleDisplayName(invitation.role)}</strong>.
              </p>
            )}
            <button onClick={() => navigate('/firm/dashboard')} className="btn-primary w-full flex items-center justify-center gap-2">
              <ArrowRight className="w-5 h-5" />
              Go to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  // Main form
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500 rounded-xl mb-6 shadow-lg">
            <UserPlus className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-3">Join Your Team</h1>
          <p className="text-gray-600">Complete your account setup to get started</p>
        </div>

        {/* Invitation Details */}
        {invitation && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-700">You've been invited to join</p>
                <p className="text-lg font-semibold text-blue-700">{invitation.organization_name}</p>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <Shield className="w-4 h-4" />
                    {getRoleDisplayName(invitation.role)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Mail className="w-4 h-4" />
                    {invitation.email}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Form Card */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center gap-2 mb-6">
            <Shield className="w-5 h-5 text-blue-500" />
            <h2 className="text-xl font-bold text-gray-900">Create Your Account</h2>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleAcceptInvitation} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Smith"
                  required
                  className="input-field pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Create Password *</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a secure password"
                  required
                  className="input-field pl-10 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {password && (
                <div className="mt-2">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${passwordStrength.color} transition-all`}
                        style={{ width: `${(passwordStrength.level / 4) * 100}%` }}
                      />
                    </div>
                    <span className={`text-xs font-medium ${
                      passwordStrength.level <= 1 ? 'text-red-600' :
                      passwordStrength.level === 2 ? 'text-orange-600' :
                      passwordStrength.level === 3 ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    {passwordRequirements.map((req, idx) => (
                      <div key={idx} className="flex items-center gap-1.5">
                        {req.test(password) ? (
                          <Check className="w-3.5 h-3.5 text-green-500" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-gray-400" />
                        )}
                        <span className={`text-xs ${req.test(password) ? 'text-green-700' : 'text-gray-500'}`}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password *</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  required
                  className="input-field pl-10"
                />
              </div>
              {confirmPassword && password !== confirmPassword && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <X className="w-3.5 h-3.5" /> Passwords do not match
                </p>
              )}
              {confirmPassword && password === confirmPassword && (
                <p className="mt-1 text-xs text-green-600 flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Passwords match
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !passwordRequirements.every(req => req.test(password)) || password !== confirmPassword}
              className="btn-primary w-full py-3 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Create Account & Join Team
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <button onClick={() => navigate('/login')} className="text-blue-500 hover:underline font-semibold">
                Sign In
              </button>
            </p>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
          <Shield className="w-4 h-4" />
          <span>Enterprise-grade security & SOC 2 compliant</span>
        </div>
      </motion.div>
    </div>
  );
}

export default AcceptInvitation;
