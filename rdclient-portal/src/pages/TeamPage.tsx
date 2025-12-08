/**
 * Team Page
 * Invite and manage team members who can contribute to the R&D study
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Plus,
  Mail,
  User,
  Clock,
  CheckCircle,
  X,
  Send,
  RefreshCw,
  Trash2,
  AlertCircle,
  Info,
  Loader2,
  UserPlus,
} from 'lucide-react';
import { useAuthStore } from '../store/auth';
import studyService from '../services/study.service';
import toast from 'react-hot-toast';
import type { TeamInvitation } from '../types';

export default function TeamPage() {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [invitations, setInvitations] = useState<TeamInvitation[]>([]);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviting, setInviting] = useState(false);
  const [resending, setResending] = useState<string | null>(null);

  // Invite form
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');

  useEffect(() => {
    loadInvitations();
  }, []);

  const loadInvitations = async () => {
    try {
      const data = await studyService.getTeamInvitations();
      setInvitations(data);
    } catch (error) {
      console.error('Failed to load invitations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail || !inviteName) {
      toast.error('Please fill in all fields');
      return;
    }

    setInviting(true);
    try {
      const invitation = await studyService.inviteTeamMember({
        email: inviteEmail,
        name: inviteName,
      });
      setInvitations([...invitations, invitation]);
      setShowInviteModal(false);
      setInviteEmail('');
      setInviteName('');
      toast.success(`Invitation sent to ${inviteEmail}`);
    } catch {
      toast.error('Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  const handleResend = async (invitationId: string) => {
    setResending(invitationId);
    try {
      await studyService.resendInvitation(invitationId);
      toast.success('Invitation resent');
    } catch {
      toast.error('Failed to resend invitation');
    } finally {
      setResending(null);
    }
  };

  const handleCancel = async (invitationId: string) => {
    if (!confirm('Are you sure you want to cancel this invitation?')) return;

    try {
      await studyService.cancelInvitation(invitationId);
      setInvitations(invitations.filter((i) => i.id !== invitationId));
      toast.success('Invitation cancelled');
    } catch {
      toast.error('Failed to cancel invitation');
    }
  };

  const getStatusBadge = (status: TeamInvitation['status']) => {
    switch (status) {
      case 'accepted':
        return (
          <span className="flex items-center gap-1 text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs font-medium">
            <CheckCircle className="w-3 h-3" />
            Accepted
          </span>
        );
      case 'expired':
        return (
          <span className="flex items-center gap-1 text-red-600 bg-red-100 px-2 py-1 rounded-full text-xs font-medium">
            <AlertCircle className="w-3 h-3" />
            Expired
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-orange-600 bg-orange-100 px-2 py-1 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const isPrimaryUser = user?.role === 'primary';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Team Members</h1>
              <p className="text-gray-600">Invite colleagues to help provide information</p>
            </div>
          </div>
          {isPrimaryUser && (
            <button onClick={() => setShowInviteModal(true)} className="fluent-btn-primary">
              <UserPlus className="w-5 h-5" />
              Invite Team Member
            </button>
          )}
        </div>
      </motion.div>

      {/* Info Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fluent-card p-4 bg-blue-50 border-blue-200"
      >
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900">Collaborate with your team</p>
            <p className="text-sm text-blue-800 mt-1">
              Invite team members who can help provide project details, employee information, or
              other R&D documentation. Each team member will have their own account to contribute.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Current User Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="fluent-card p-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center text-white font-bold">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{user?.full_name}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
            </div>
          </div>
          <span className="text-xs bg-primary-100 text-primary-700 px-3 py-1 rounded-full font-medium">
            {user?.role === 'primary' ? 'Primary Contact' : 'Team Member'}
          </span>
        </div>
      </motion.div>

      {/* Invitations List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="fluent-card overflow-hidden"
      >
        <div className="p-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Team Invitations</h2>
        </div>

        {invitations.length === 0 ? (
          <div className="p-8 text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">No team members invited yet</p>
            {isPrimaryUser && (
              <p className="text-sm text-gray-500">
                Click "Invite Team Member" to add colleagues
              </p>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {invitations.map((invitation) => (
              <div key={invitation.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-gray-500" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{invitation.name}</p>
                    <p className="text-sm text-gray-500">{invitation.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(invitation.status)}
                  {invitation.status === 'pending' && isPrimaryUser && (
                    <>
                      <button
                        onClick={() => handleResend(invitation.id)}
                        disabled={resending === invitation.id}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                        title="Resend invitation"
                      >
                        {resending === invitation.id ? (
                          <Loader2 className="w-4 h-4 text-gray-600 animate-spin" />
                        ) : (
                          <RefreshCw className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                      <button
                        onClick={() => handleCancel(invitation.id)}
                        className="p-2 hover:bg-red-50 rounded-lg"
                        title="Cancel invitation"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Invite Modal */}
      <AnimatePresence>
        {showInviteModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
            onClick={() => setShowInviteModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-md bg-white rounded-2xl shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900">Invite Team Member</h2>
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="fluent-label">Full Name</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={inviteName}
                      onChange={(e) => setInviteName(e.target.value)}
                      className="fluent-input pl-10"
                      placeholder="Enter their name"
                    />
                  </div>
                </div>

                <div>
                  <label className="fluent-label">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      className="fluent-input pl-10"
                      placeholder="colleague@company.com"
                    />
                  </div>
                </div>

                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    An email invitation will be sent with a link to create their account and
                    access this R&D study.
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
                <button onClick={() => setShowInviteModal(false)} className="fluent-btn-secondary">
                  Cancel
                </button>
                <button onClick={handleInvite} disabled={inviting} className="fluent-btn-primary">
                  {inviting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Send Invitation
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
