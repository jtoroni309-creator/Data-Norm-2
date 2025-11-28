/**
 * Employee Management Page
 * Manage team members, invitations, roles, and permissions
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  UserPlus,
  Mail,
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Shield,
  X,
  Check,
  Clock,
  ChevronDown,
  Eye,
  EyeOff,
  Copy,
  RefreshCw,
  Info,
  CheckCircle
} from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { firmService } from '../services/firm.service';
import {
  FirmUser,
  UserInvitation,
  UserPermission,
  UserRole,
  UserInvitationCreate,
  UserPermissionUpdate
} from '../types';
import toast from 'react-hot-toast';

const EmployeeManagement: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [users, setUsers] = useState<FirmUser[]>([]);
  const [invitations, setInvitations] = useState<UserInvitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'employees' | 'invitations'>('employees');
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<UserRole | 'all'>('all');

  // Modal states
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<FirmUser | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<UserPermission | null>(null);

  // Invite form state
  const [inviteForm, setInviteForm] = useState<UserInvitationCreate>({
    email: '',
    role: 'staff',
    message: ''
  });

  useEffect(() => {
    loadData();
    // Check if action=invite in URL
    if (searchParams.get('action') === 'invite') {
      setShowInviteModal(true);
    }
  }, [searchParams]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usersData, invitationsData] = await Promise.all([
        firmService.listUsers(),
        firmService.listInvitations()
      ]);
      setUsers(usersData);
      setInvitations(invitationsData);
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load employee data');
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async () => {
    if (!inviteForm.email || !inviteForm.role) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      await firmService.createInvitation(inviteForm);
      toast.success(`Invitation sent to ${inviteForm.email}`);
      setShowInviteModal(false);
      setInviteForm({ email: '', role: 'staff', message: '' });
      loadData();
    } catch (error: any) {
      console.error('Failed to send invitation:', error);
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleDeactivateUser = async (user: FirmUser) => {
    if (!confirm(`Are you sure you want to deactivate ${user.full_name}?`)) {
      return;
    }

    try {
      await firmService.deactivateUser(user.id);
      toast.success('User deactivated successfully');
      loadData();
    } catch (error: any) {
      console.error('Failed to deactivate user:', error);
      toast.error(error.response?.data?.detail || 'Failed to deactivate user');
    }
  };

  const handleLoadPermissions = async (user: FirmUser) => {
    try {
      const permissions = await firmService.getUserPermissions(user.id);
      setSelectedUser(user);
      setSelectedPermissions(permissions);
      setShowPermissionsModal(true);
    } catch (error: any) {
      console.error('Failed to load permissions:', error);
      toast.error('Failed to load user permissions');
    }
  };

  const handleUpdatePermissions = async (updates: UserPermissionUpdate) => {
    if (!selectedUser) return;

    try {
      const updated = await firmService.updateUserPermissions(selectedUser.id, updates);
      setSelectedPermissions(updated);
      toast.success('Permissions updated successfully');
    } catch (error: any) {
      console.error('Failed to update permissions:', error);
      toast.error(error.response?.data?.detail || 'Failed to update permissions');
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const activeInvitations = invitations.filter(inv => !inv.is_expired && !inv.accepted_at);
  const expiredInvitations = invitations.filter(inv => inv.is_expired || inv.accepted_at);

  const roles: { value: UserRole; label: string; color: string; description: string }[] = [
    { value: 'partner', label: 'Partner', color: 'purple', description: 'Full access including firm settings, billing, and user management' },
    { value: 'manager', label: 'Manager', color: 'blue', description: 'Manage engagements, supervise staff, and invite team members' },
    { value: 'senior', label: 'Senior', color: 'green', description: 'Lead fieldwork, review workpapers, and edit engagements' },
    { value: 'staff', label: 'Staff', color: 'gray', description: 'Perform testing procedures and upload documents' },
    { value: 'qc_reviewer', label: 'QC Reviewer', color: 'orange', description: 'Review completed work and approve quality control' },
    { value: 'client_contact', label: 'Client Contact', color: 'pink', description: 'View shared documents and communicate with audit team' }
  ];

  // Copy invitation link to clipboard
  const copyInvitationLink = async (invitation: UserInvitation) => {
    const baseUrl = window.location.origin;
    const link = `${baseUrl}/accept-invitation?token=${invitation.token}`;
    try {
      await navigator.clipboard.writeText(link);
      toast.success('Invitation link copied to clipboard');
    } catch {
      toast.error('Failed to copy link');
    }
  };

  // Resend invitation
  const handleResendInvitation = async (invitation: UserInvitation) => {
    try {
      await firmService.resendInvitation(invitation.id);
      toast.success(`Invitation resent to ${invitation.email}`);
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to resend invitation');
    }
  };

  const getRoleBadgeColor = (role: UserRole) => {
    const roleConfig = roles.find(r => r.value === role);
    return roleConfig?.color || 'gray';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600">Loading employees...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/firm/dashboard')}
                className="text-sm text-gray-600 hover:text-gray-900 mb-2 flex items-center gap-1"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-3xl font-bold text-gradient">Employee Management</h1>
              <p className="text-gray-600 mt-1">
                Manage your team members, invitations, and permissions
              </p>
            </div>

            <button
              onClick={() => setShowInviteModal(true)}
              className="btn-primary flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              Invite Employee
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('employees')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'employees'
                ? 'bg-white shadow-md text-blue-600'
                : 'bg-white/50 text-gray-600 hover:bg-white'
            }`}
          >
            <Users className="w-5 h-5" />
            Employees
            <span className="badge-primary">{users.length}</span>
          </button>
          <button
            onClick={() => setActiveTab('invitations')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'invitations'
                ? 'bg-white shadow-md text-blue-600'
                : 'bg-white/50 text-gray-600 hover:bg-white'
            }`}
          >
            <Mail className="w-5 h-5" />
            Invitations
            {activeInvitations.length > 0 && (
              <span className="badge-warning">{activeInvitations.length}</span>
            )}
          </button>
        </div>

        {/* Employees Tab */}
        {activeTab === 'employees' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Search and Filter */}
            <div className="card">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search employees..."
                    className="input-field pl-10"
                  />
                </div>
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value as UserRole | 'all')}
                  className="input-field w-full sm:w-48"
                >
                  <option value="all">All Roles</option>
                  {roles.map(role => (
                    <option key={role.value} value={role.value}>{role.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Employee List */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredUsers.map((user, index) => {
                const roleColor = getRoleBadgeColor(user.role);
                return (
                  <motion.div
                    key={user.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="card hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg flex-shrink-0">
                          {user.full_name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900 truncate">
                              {user.full_name}
                            </h3>
                            {user.is_active && (
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 truncate">{user.email}</p>
                          <span className={`badge-${roleColor} mt-2 inline-block text-xs`}>
                            {roles.find(r => r.value === user.role)?.label}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-2">
                        <button
                          onClick={() => handleLoadPermissions(user)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                          title="Manage permissions"
                        >
                          <Shield className="w-4 h-4 text-gray-600" />
                        </button>
                        <button
                          onClick={() => handleDeactivateUser(user)}
                          className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                          title="Deactivate user"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </div>
                    {user.last_login_at && (
                      <p className="text-xs text-gray-500 mt-3">
                        Last login: {new Date(user.last_login_at).toLocaleDateString()}
                      </p>
                    )}
                  </motion.div>
                );
              })}
            </div>

            {filteredUsers.length === 0 && (
              <div className="card text-center py-12">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No employees found</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Invitations Tab */}
        {activeTab === 'invitations' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Active Invitations */}
            <div className="card">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-orange-500" />
                Pending Invitations
              </h2>
              {activeInvitations.length > 0 ? (
                <div className="space-y-3">
                  {activeInvitations.map((invitation) => (
                    <div
                      key={invitation.id}
                      className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-200"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{invitation.email}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <span className={`badge-${getRoleBadgeColor(invitation.role)} text-xs`}>
                            {roles.find(r => r.value === invitation.role)?.label}
                          </span>
                          <span className="text-xs text-gray-600">
                            Expires: {new Date(invitation.expires_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => copyInvitationLink(invitation)}
                          className="p-2 hover:bg-orange-100 rounded-lg transition-colors"
                          title="Copy invitation link"
                        >
                          <Copy className="w-4 h-4 text-gray-600" />
                        </button>
                        <button
                          onClick={() => handleResendInvitation(invitation)}
                          className="p-2 hover:bg-orange-100 rounded-lg transition-colors"
                          title="Resend invitation email"
                        >
                          <RefreshCw className="w-4 h-4 text-gray-600" />
                        </button>
                        <span className="badge-warning">Pending</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600 text-center py-8">No pending invitations</p>
              )}
            </div>

            {/* Expired/Accepted Invitations */}
            {expiredInvitations.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Past Invitations</h2>
                <div className="space-y-3">
                  {expiredInvitations.map((invitation) => (
                    <div
                      key={invitation.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-700">{invitation.email}</p>
                        <span className={`badge-${getRoleBadgeColor(invitation.role)} text-xs mt-1 inline-block`}>
                          {roles.find(r => r.value === invitation.role)?.label}
                        </span>
                      </div>
                      {invitation.accepted_at ? (
                        <span className="badge-success">Accepted</span>
                      ) : (
                        <span className="badge-error">Expired</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Invite Modal */}
      <AnimatePresence>
        {showInviteModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowInviteModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl p-6 max-w-md w-full shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Invite Employee</h2>
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                    className="input-field"
                    placeholder="colleague@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role *
                  </label>
                  <select
                    value={inviteForm.role}
                    onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value as UserRole })}
                    className="input-field"
                  >
                    {roles.map(role => (
                      <option key={role.value} value={role.value}>{role.label}</option>
                    ))}
                  </select>
                  {/* Role Description */}
                  <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Info className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-blue-800">
                          {roles.find(r => r.value === inviteForm.role)?.label}
                        </p>
                        <p className="text-xs text-blue-600 mt-0.5">
                          {roles.find(r => r.value === inviteForm.role)?.description}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message (Optional)
                  </label>
                  <textarea
                    value={inviteForm.message}
                    onChange={(e) => setInviteForm({ ...inviteForm, message: e.target.value })}
                    className="input-field"
                    rows={3}
                    placeholder="Welcome to the team!"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={handleInvite}
                  className="btn-primary flex-1"
                >
                  Send Invitation
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Permissions Modal */}
      <AnimatePresence>
        {showPermissionsModal && selectedUser && selectedPermissions && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto"
            onClick={() => setShowPermissionsModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl p-6 max-w-2xl w-full shadow-2xl my-8"
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Manage Permissions</h2>
                  <p className="text-gray-600 mt-1">{selectedUser.full_name}</p>
                </div>
                <button
                  onClick={() => setShowPermissionsModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Engagement Permissions */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Engagement Permissions</h3>
                  <div className="space-y-2">
                    {['can_create_engagements', 'can_edit_engagements', 'can_delete_engagements', 'can_view_all_engagements'].map(perm => (
                      <label key={perm} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                        <input
                          type="checkbox"
                          checked={selectedPermissions[perm as keyof UserPermission] as boolean}
                          onChange={(e) => handleUpdatePermissions({ [perm]: e.target.checked })}
                          className="w-5 h-5 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-900">
                          {perm.replace(/_/g, ' ').replace(/can /g, 'Can ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* User Management Permissions */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">User Management</h3>
                  <div className="space-y-2">
                    {['can_invite_users', 'can_manage_users', 'can_manage_roles'].map(perm => (
                      <label key={perm} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                        <input
                          type="checkbox"
                          checked={selectedPermissions[perm as keyof UserPermission] as boolean}
                          onChange={(e) => handleUpdatePermissions({ [perm]: e.target.checked })}
                          className="w-5 h-5 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-900">
                          {perm.replace(/_/g, ' ').replace(/can /g, 'Can ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Firm Settings Permissions */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Firm Settings</h3>
                  <div className="space-y-2">
                    {['can_edit_firm_settings', 'can_manage_billing'].map(perm => (
                      <label key={perm} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                        <input
                          type="checkbox"
                          checked={selectedPermissions[perm as keyof UserPermission] as boolean}
                          onChange={(e) => handleUpdatePermissions({ [perm]: e.target.checked })}
                          className="w-5 h-5 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-900">
                          {perm.replace(/_/g, ' ').replace(/can /g, 'Can ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Document Permissions */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Document Management</h3>
                  <div className="space-y-2">
                    {['can_upload_documents', 'can_delete_documents'].map(perm => (
                      <label key={perm} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                        <input
                          type="checkbox"
                          checked={selectedPermissions[perm as keyof UserPermission] as boolean}
                          onChange={(e) => handleUpdatePermissions({ [perm]: e.target.checked })}
                          className="w-5 h-5 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-900">
                          {perm.replace(/_/g, ' ').replace(/can /g, 'Can ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6 pt-6 border-t">
                <button
                  onClick={() => setShowPermissionsModal(false)}
                  className="btn-primary"
                >
                  Done
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EmployeeManagement;
