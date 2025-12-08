/**
 * Settings Page
 * User profile and account settings
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  User,
  Mail,
  Phone,
  Lock,
  Save,
  Loader2,
  CheckCircle,
  Building2,
} from 'lucide-react';
import { useAuthStore } from '../store/auth';
import authService from '../services/auth.service';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  // Profile form
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState(user?.phone || '');

  // Password form
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleUpdateProfile = async () => {
    setSaving(true);
    try {
      const updated = await authService.updateProfile({
        full_name: fullName,
        phone: phone || undefined,
      });
      setUser(updated);
      toast.success('Profile updated successfully');
    } catch {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setChangingPassword(true);
    try {
      await authService.changePassword(currentPassword, newPassword);
      toast.success('Password changed successfully');
      setShowPasswordForm(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch {
      toast.error('Failed to change password. Please check your current password.');
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <Settings className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Manage your profile and account settings</p>
          </div>
        </div>
      </motion.div>

      {/* Profile Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fluent-card p-6"
      >
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Profile Information</h2>

        <div className="space-y-4">
          {/* Avatar and Company Info */}
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{user?.full_name}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
              <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
                <Building2 className="w-4 h-4" />
                <span>{user?.company_name}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="fluent-label">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="fluent-input pl-10"
              />
            </div>
          </div>

          <div>
            <label className="fluent-label">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="fluent-input pl-10 bg-gray-50 text-gray-500 cursor-not-allowed"
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Email cannot be changed. Contact support if needed.
            </p>
          </div>

          <div>
            <label className="fluent-label">Phone Number</label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="(555) 123-4567"
                className="fluent-input pl-10"
              />
            </div>
          </div>

          <button
            onClick={handleUpdateProfile}
            disabled={saving}
            className="fluent-btn-primary"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Changes
          </button>
        </div>
      </motion.div>

      {/* Password Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Password</h2>
          {!showPasswordForm && (
            <button
              onClick={() => setShowPasswordForm(true)}
              className="fluent-btn-secondary"
            >
              <Lock className="w-4 h-4" />
              Change Password
            </button>
          )}
        </div>

        {showPasswordForm ? (
          <div className="space-y-4">
            <div>
              <label className="fluent-label">Current Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Enter current password"
                  className="fluent-input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="fluent-label">New Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                  className="fluent-input pl-10"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">Minimum 8 characters</p>
            </div>

            <div>
              <label className="fluent-label">Confirm New Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  className="fluent-input pl-10"
                />
              </div>
              {confirmPassword && newPassword === confirmPassword && (
                <p className="mt-1 text-xs text-green-600 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Passwords match
                </p>
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleChangePassword}
                disabled={changingPassword}
                className="fluent-btn-primary"
              >
                {changingPassword ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Lock className="w-4 h-4" />
                )}
                Update Password
              </button>
              <button
                onClick={() => {
                  setShowPasswordForm(false);
                  setCurrentPassword('');
                  setNewPassword('');
                  setConfirmPassword('');
                }}
                className="fluent-btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <p className="text-gray-600">
            Your password was last changed on{' '}
            <span className="font-medium">January 15, 2024</span>
          </p>
        )}
      </motion.div>

      {/* Account Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="fluent-card p-6"
      >
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Account Type</span>
            <span className="font-medium text-gray-900">
              {user?.role === 'primary' ? 'Primary Contact' : 'Team Member'}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Company</span>
            <span className="font-medium text-gray-900">{user?.company_name}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">CPA Firm</span>
            <span className="font-medium text-gray-900">{user?.firm_name}</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-500">Account Created</span>
            <span className="font-medium text-gray-900">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : 'N/A'}
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
