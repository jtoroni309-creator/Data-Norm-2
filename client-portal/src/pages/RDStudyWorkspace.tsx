/**
 * R&D Study Workspace - Fully Functional
 * Comprehensive workspace for managing R&D tax credit studies
 * with AI-powered data import, payroll integrations, and complete study generation
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical,
  ArrowLeft,
  Building2,
  Calendar,
  DollarSign,
  Users,
  FileText,
  CheckCircle,
  AlertTriangle,
  Clock,
  Upload,
  Calculator,
  Download,
  Check,
  X,
  ChevronRight,
  Brain,
  Target,
  TrendingUp,
  Loader2,
  RefreshCw,
  FileSpreadsheet,
  File,
  Wand2,
  UploadCloud,
  Link,
  Edit,
  Trash2,
  Plus,
  ChevronDown,
  ChevronUp,
  Info,
  Database,
  Zap,
  Mail,
  Send,
  Copy,
  ExternalLink,
} from 'lucide-react';
import { rdStudyService } from '../services/rd-study.service';
import { RDStudy, RDProject, RDEmployee, RDStudyStatus } from '../types';
import toast from 'react-hot-toast';

type TabId = 'data-collection' | 'client-invitations' | 'employees' | 'projects' | 'qres' | 'calculations' | 'generate';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const statusConfig: Record<RDStudyStatus, { label: string; color: string; bgColor: string }> = {
  draft: { label: 'Draft', color: 'text-gray-600', bgColor: 'bg-gray-100' },
  intake: { label: 'Intake', color: 'text-blue-600', bgColor: 'bg-blue-100' },
  data_collection: { label: 'Data Collection', color: 'text-indigo-600', bgColor: 'bg-indigo-100' },
  ai_analysis: { label: 'AI Analysis', color: 'text-purple-600', bgColor: 'bg-purple-100' },
  cpa_review: { label: 'CPA Review', color: 'text-orange-600', bgColor: 'bg-orange-100' },
  calculation: { label: 'Calculation', color: 'text-cyan-600', bgColor: 'bg-cyan-100' },
  narrative_generation: { label: 'Narratives', color: 'text-pink-600', bgColor: 'bg-pink-100' },
  final_review: { label: 'Final Review', color: 'text-amber-600', bgColor: 'bg-amber-100' },
  approved: { label: 'Approved', color: 'text-green-600', bgColor: 'bg-green-100' },
  finalized: { label: 'Finalized', color: 'text-emerald-600', bgColor: 'bg-emerald-100' },
  locked: { label: 'Locked', color: 'text-slate-600', bgColor: 'bg-slate-100' },
};

const tabs: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: 'data-collection', label: 'Data Collection', icon: Database },
  { id: 'client-invitations', label: 'Client Invitations', icon: Mail },
  { id: 'employees', label: 'Employees', icon: Users },
  { id: 'projects', label: 'Projects', icon: FlaskConical },
  { id: 'qres', label: 'QRE Summary', icon: DollarSign },
  { id: 'calculations', label: 'Calculations', icon: Calculator },
  { id: 'generate', label: 'Generate & Export', icon: Download },
];

// Interfaces
interface UploadAnalysis {
  filename: string;
  sheets: {
    sheet_name: string;
    category: string;
    category_confidence: number;
    row_count: number;
    column_mappings: {
      source_column: string;
      target_field: string;
      confidence: number;
      sample_values: any[];
    }[];
    issues: string[];
    preview_data: any[];
  }[];
  missing_data_types: string[];
  recommendations: string[];
}

interface QRECategory {
  count: number;
  gross: number;
  qualified: number;
}

interface QRESummary {
  by_category: Record<string, QRECategory>;
  total_gross: number;
  total_qualified: number;
}

interface ClientInvitation {
  id: string;
  client_email: string;
  client_name: string;
  study_id: string;
  study_name: string;
  tax_year: number;
  firm_id: string;
  firm_name: string;
  invited_by_user_id: string;
  invited_by_name: string;
  token: string;
  deadline?: string;
  status: 'pending' | 'accepted' | 'expired';
  expires_at: string;
  accepted_at?: string;
  created_at: string;
}

// Client Invitations Tab - CPA firms can invite clients to submit R&D data
const ClientInvitationsTab: React.FC<{
  studyId: string;
  study: RDStudy | null;
  onRefresh: () => void;
}> = ({ studyId, study, onRefresh }) => {
  const [invitations, setInvitations] = useState<ClientInvitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [sending, setSending] = useState(false);
  const [resending, setResending] = useState<string | null>(null);

  const [newInvite, setNewInvite] = useState({
    client_name: '',
    client_email: '',
    deadline: '',
    message: '',
  });

  const loadInvitations = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/identity/rd-study/client-invitations?study_id=${studyId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setInvitations(data);
      }
    } catch (error) {
      console.error('Failed to load invitations:', error);
    } finally {
      setLoading(false);
    }
  }, [studyId]);

  useEffect(() => {
    loadInvitations();
  }, [loadInvitations]);

  const handleSendInvitation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!study) return;

    setSending(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/identity/rd-study/client-invitations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_email: newInvite.client_email,
          client_name: newInvite.client_name,
          study_id: studyId,
          study_name: study.name,
          tax_year: study.tax_year,
          deadline: newInvite.deadline || null,
          message: newInvite.message || null,
        }),
      });

      if (response.ok) {
        toast.success(`Invitation sent to ${newInvite.client_email}`);
        setShowInviteModal(false);
        setNewInvite({ client_name: '', client_email: '', deadline: '', message: '' });
        loadInvitations();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to send invitation');
      }
    } catch (error) {
      console.error('Failed to send invitation:', error);
      toast.error('Failed to send invitation');
    } finally {
      setSending(false);
    }
  };

  const handleResendInvitation = async (invitationId: string) => {
    setResending(invitationId);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/identity/rd-study/client-invitations/${invitationId}/resend`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        toast.success('Invitation resent successfully');
        loadInvitations();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to resend invitation');
      }
    } catch (error) {
      console.error('Failed to resend invitation:', error);
      toast.error('Failed to resend invitation');
    } finally {
      setResending(null);
    }
  };

  const copyInviteLink = (token: string) => {
    const url = `${window.location.origin}/rd-study-data-collection?token=${token}`;
    navigator.clipboard.writeText(url);
    toast.success('Link copied to clipboard');
  };

  const getStatusBadge = (status: string, expiresAt: string) => {
    const isExpired = new Date(expiresAt) < new Date();
    if (status === 'accepted') {
      return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">Completed</span>;
    }
    if (isExpired || status === 'expired') {
      return <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-medium">Expired</span>;
    }
    return <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs rounded-full font-medium">Pending</span>;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Client Data Collection</h3>
          <p className="text-sm text-gray-500">
            Invite clients to submit their R&D data. Clients can upload or manually enter employees, projects, and documents.
          </p>
        </div>
        <button
          onClick={() => setShowInviteModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          Invite Client
        </button>
      </div>

      {/* Info Card */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <Info className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h4 className="font-medium text-blue-900">How Client Invitations Work</h4>
            <ul className="mt-2 space-y-1 text-sm text-blue-700">
              <li>• Clients receive a secure link to submit their R&D data</li>
              <li>• They can upload Excel files or manually enter employees and projects</li>
              <li>• AI assists clients in writing project descriptions</li>
              <li>• Clients <strong>cannot</strong> see calculations, credits, or final reports</li>
              <li>• All data is automatically imported into this study when submitted</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Invitations List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
        </div>
      ) : invitations.length === 0 ? (
        <div className="card text-center py-12">
          <Mail className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h4 className="text-gray-900 font-medium mb-2">No invitations sent yet</h4>
          <p className="text-gray-500 text-sm mb-4">
            Invite your client to submit their R&D data for this study
          </p>
          <button
            onClick={() => setShowInviteModal(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send First Invitation
          </button>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Client</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Email</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Sent</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Expires</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {invitations.map(inv => (
                <tr key={inv.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{inv.client_name}</td>
                  <td className="px-4 py-3 text-gray-600">{inv.client_email}</td>
                  <td className="px-4 py-3 text-center">{getStatusBadge(inv.status, inv.expires_at)}</td>
                  <td className="px-4 py-3 text-gray-500 text-sm">{formatDate(inv.created_at)}</td>
                  <td className="px-4 py-3 text-gray-500 text-sm">{formatDate(inv.expires_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => copyInviteLink(inv.token)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                        title="Copy link"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      {inv.status === 'pending' && (
                        <button
                          onClick={() => handleResendInvitation(inv.id)}
                          disabled={resending === inv.id}
                          className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded"
                          title="Resend invitation"
                        >
                          {resending === inv.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <RefreshCw className="w-4 h-4" />
                          )}
                        </button>
                      )}
                      <a
                        href={`/rd-study-data-collection?token=${inv.token}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                        title="Preview client view"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Send Invitation Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl w-full max-w-lg"
          >
            <div className="p-6 border-b flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Send className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Invite Client</h2>
                  <p className="text-sm text-gray-500">Request R&D data for {study?.name}</p>
                </div>
              </div>
              <button onClick={() => setShowInviteModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSendInvitation} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client Name *</label>
                <input
                  type="text"
                  value={newInvite.client_name}
                  onChange={(e) => setNewInvite(prev => ({ ...prev, client_name: e.target.value }))}
                  required
                  placeholder="John Smith"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client Email *</label>
                <input
                  type="email"
                  value={newInvite.client_email}
                  onChange={(e) => setNewInvite(prev => ({ ...prev, client_email: e.target.value }))}
                  required
                  placeholder="john@company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Deadline (optional)</label>
                <input
                  type="date"
                  value={newInvite.deadline}
                  onChange={(e) => setNewInvite(prev => ({ ...prev, deadline: e.target.value }))}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Personal Message (optional)</label>
                <textarea
                  value={newInvite.message}
                  onChange={(e) => setNewInvite(prev => ({ ...prev, message: e.target.value }))}
                  rows={3}
                  placeholder="Add a personal note to include in the invitation email..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <strong>What the client will receive:</strong>
                </p>
                <ul className="mt-1 text-xs text-gray-500 space-y-1">
                  <li>• Professional email from your firm</li>
                  <li>• Secure link to submit R&D data (valid for 30 days)</li>
                  <li>• Instructions for what data to provide</li>
                </ul>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sending}
                  className="btn-primary flex items-center gap-2"
                >
                  {sending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Send Invitation
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// Data Collection Tab
const DataCollectionTab: React.FC<{
  studyId: string;
  onDataImported: () => void;
}> = ({ studyId, onDataImported }) => {
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<UploadAnalysis | null>(null);
  const [showMappingModal, setShowMappingModal] = useState(false);
  const [payrollProvider, setPayrollProvider] = useState('');
  const [connectingPayroll, setConnectingPayroll] = useState(false);
  const [expandedSheet, setExpandedSheet] = useState<number>(0);
  const [dataStatus, setDataStatus] = useState({
    employees: 'missing',
    payroll: 'missing',
    projects: 'missing',
    time_tracking: 'missing',
    supplies: 'missing',
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rd-study/studies/${studyId}/upload/analyze`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysis(result);
        setShowMappingModal(true);
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to analyze file');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleImportData = async () => {
    if (!analysis) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rd-study/studies/${studyId}/upload/import`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: analysis.filename,
        }),
      });

      if (response.ok) {
        toast.success('Data imported successfully!');
        setShowMappingModal(false);
        setAnalysis(null);
        onDataImported();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to import data');
      }
    } catch (error) {
      console.error('Import failed:', error);
      toast.error('Failed to import data');
    }
  };

  const handleConnectPayroll = async () => {
    if (!payrollProvider) return;

    setConnectingPayroll(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rd-study/studies/${studyId}/payroll/connect`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ provider: payrollProvider }),
      });

      if (response.ok) {
        const { auth_url } = await response.json();
        window.location.href = auth_url;
      } else {
        toast.error('Failed to connect payroll provider');
      }
    } catch (error) {
      console.error('Payroll connection failed:', error);
      toast.error('Failed to connect payroll provider');
    } finally {
      setConnectingPayroll(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'partial': return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      default: return <X className="w-5 h-5 text-red-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Excel Upload */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <UploadCloud className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Import Excel Data</h3>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded-full">
                <Wand2 className="w-3 h-3" /> AI-Powered
              </span>
            </div>
          </div>

          <p className="text-sm text-gray-500 mb-4">
            Upload Excel files with payroll, employee, project, or time tracking data.
            Our AI will automatically detect data types and map columns.
          </p>

          <label className="flex flex-col items-center justify-center h-40 border-2 border-dashed border-purple-300 rounded-xl bg-purple-50/50 hover:bg-purple-100/50 cursor-pointer transition-colors">
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
            {uploading ? (
              <div className="flex flex-col items-center">
                <Loader2 className="w-10 h-10 text-purple-500 animate-spin" />
                <p className="mt-2 text-sm text-purple-600">Analyzing file...</p>
              </div>
            ) : (
              <>
                <Upload className="w-10 h-10 text-purple-400" />
                <p className="mt-2 text-sm text-gray-600">Click or drag Excel/CSV files</p>
                <p className="text-xs text-gray-400">Supports .xlsx, .xls, .csv</p>
              </>
            )}
          </label>

          <div className="mt-4 flex flex-wrap gap-2">
            {['Payroll/W-2', 'Employees', 'Time Tracking', 'Projects', 'GL/Expenses', 'Contracts'].map(type => (
              <span key={type} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                {type}
              </span>
            ))}
          </div>
        </div>

        {/* Payroll Integration */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Link className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Connect Payroll Provider</h3>
              <p className="text-xs text-gray-500">Automatic data sync</p>
            </div>
          </div>

          <p className="text-sm text-gray-500 mb-4">
            Connect directly to your payroll provider to automatically import employee and wage data.
          </p>

          <div className="space-y-3">
            {[
              { id: 'adp', name: 'ADP Workforce Now', icon: '🅰️' },
              { id: 'justworks', name: 'Justworks', icon: '💼' },
              { id: 'paychex', name: 'Paychex Flex', icon: '📊' },
            ].map(provider => (
              <button
                key={provider.id}
                onClick={() => setPayrollProvider(provider.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-colors ${
                  payrollProvider === provider.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="text-xl">{provider.icon}</span>
                <span className="font-medium text-gray-700">{provider.name}</span>
                {payrollProvider === provider.id && (
                  <CheckCircle className="w-5 h-5 text-blue-500 ml-auto" />
                )}
              </button>
            ))}
          </div>

          <button
            onClick={handleConnectPayroll}
            disabled={!payrollProvider || connectingPayroll}
            className="mt-4 w-full btn-primary flex items-center justify-center gap-2"
          >
            {connectingPayroll ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            Connect & Import
          </button>

          <div className="mt-3 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-700 flex items-center gap-2">
              <Info className="w-4 h-4" />
              Secure OAuth connection. We never store your credentials.
            </p>
          </div>
        </div>
      </div>

      {/* Data Status */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Data Collection Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(dataStatus).map(([key, status]) => (
            <div key={key} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              {getStatusIcon(status)}
              <div>
                <p className="text-sm font-medium text-gray-700 capitalize">
                  {key.replace('_', ' ')}
                </p>
                <p className="text-xs text-gray-500 capitalize">{status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Column Mapping Modal */}
      {showMappingModal && analysis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">AI Data Analysis</h2>
                  <p className="text-sm text-gray-500">{analysis.filename}</p>
                </div>
              </div>
              <button onClick={() => setShowMappingModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {analysis.sheets.map((sheet, idx) => (
                <div key={idx} className="mb-4 border rounded-lg overflow-hidden">
                  <button
                    onClick={() => setExpandedSheet(expandedSheet === idx ? -1 : idx)}
                    className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100"
                  >
                    <div className="flex items-center gap-3">
                      <FileSpreadsheet className="w-5 h-5 text-gray-400" />
                      <span className="font-medium text-gray-900">{sheet.sheet_name}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        sheet.category_confidence > 0.7
                          ? 'bg-green-100 text-green-700'
                          : sheet.category_confidence > 0.4
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {sheet.category} ({(sheet.category_confidence * 100).toFixed(0)}%)
                      </span>
                      <span className="text-sm text-gray-500">{sheet.row_count} rows</span>
                    </div>
                    {expandedSheet === idx ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </button>

                  {expandedSheet === idx && (
                    <div className="p-4 border-t">
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Column Mappings</h4>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-3 py-2 text-left text-gray-600">Source Column</th>
                              <th className="px-3 py-2 text-left text-gray-600">Maps To</th>
                              <th className="px-3 py-2 text-center text-gray-600">Confidence</th>
                              <th className="px-3 py-2 text-left text-gray-600">Sample Values</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y">
                            {sheet.column_mappings.map((mapping, midx) => (
                              <tr key={midx} className="hover:bg-gray-50">
                                <td className="px-3 py-2 font-medium">{mapping.source_column}</td>
                                <td className="px-3 py-2">
                                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                                    {mapping.target_field}
                                  </span>
                                </td>
                                <td className="px-3 py-2 text-center">
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                                    mapping.confidence > 0.7
                                      ? 'bg-green-100 text-green-700'
                                      : mapping.confidence > 0.4
                                      ? 'bg-amber-100 text-amber-700'
                                      : 'bg-red-100 text-red-700'
                                  }`}>
                                    {(mapping.confidence * 100).toFixed(0)}%
                                  </span>
                                </td>
                                <td className="px-3 py-2 text-gray-500 text-xs">
                                  {mapping.sample_values.slice(0, 2).join(', ')}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {sheet.issues.length > 0 && (
                        <div className="mt-3 p-3 bg-amber-50 rounded-lg">
                          <p className="text-sm text-amber-700 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            {sheet.issues.join('. ')}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}

              {analysis.recommendations.length > 0 && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="text-sm font-medium text-blue-800 mb-2">Recommendations</h4>
                  <ul className="space-y-1">
                    {analysis.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm text-blue-700 flex items-center gap-2">
                        <Info className="w-4 h-4 flex-shrink-0" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="p-6 border-t bg-gray-50 flex justify-end gap-3">
              <button onClick={() => setShowMappingModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={handleImportData} className="btn-primary flex items-center gap-2">
                <Download className="w-4 h-4" />
                Import Data
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// Employees Tab
const EmployeesTab: React.FC<{
  studyId: string;
  employees: RDEmployee[];
  onRefresh: () => void;
}> = ({ studyId, employees, onRefresh }) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const totalWages = employees.reduce((sum, e) => sum + (e.total_wages || 0), 0);
  const totalQualified = employees.reduce((sum, e) => sum + (e.qualified_wages || 0), 0);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const handleUpdateEmployee = async (employeeId: string, updates: Partial<RDEmployee>) => {
    setSaving(true);
    try {
      await rdStudyService.updateEmployee(studyId, employeeId, updates);
      toast.success('Employee updated');
      setEditingId(null);
      onRefresh();
    } catch (error) {
      toast.error('Failed to update employee');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{employees.length} Employees</h3>
          <p className="text-sm text-gray-500">
            Total W-2: {formatCurrency(totalWages)} | Qualified: {formatCurrency(totalQualified)}
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Employee
          </button>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Title</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Department</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">W-2 Wages</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Qualified %</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Qualified Wages</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Source</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Reviewed</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {employees.map(emp => (
                <tr key={emp.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{emp.name}</td>
                  <td className="px-4 py-3 text-gray-600">{emp.title || '-'}</td>
                  <td className="px-4 py-3 text-gray-600">{emp.department || '-'}</td>
                  <td className="px-4 py-3 text-right text-gray-900">{formatCurrency(emp.total_wages || 0)}</td>
                  <td className="px-4 py-3 text-right">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      (emp.qualified_time_percentage || 0) >= 50
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {emp.qualified_time_percentage || 0}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-medium text-green-600">
                    {formatCurrency(emp.qualified_wages || 0)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      {emp.qualified_time_source || 'Manual'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {emp.cpa_reviewed ? (
                      <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                    ) : (
                      <Clock className="w-5 h-5 text-gray-400 mx-auto" />
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => setEditingId(emp.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50 font-medium">
              <tr>
                <td className="px-4 py-3" colSpan={3}>Total</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totalWages)}</td>
                <td className="px-4 py-3"></td>
                <td className="px-4 py-3 text-right text-green-600">{formatCurrency(totalQualified)}</td>
                <td className="px-4 py-3" colSpan={3}></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
};

// Projects Tab
const ProjectsTab: React.FC<{
  studyId: string;
  projects: RDProject[];
  onRefresh: () => void;
}> = ({ studyId, projects, onRefresh }) => {
  const qualified = projects.filter(p => p.qualification_status === 'qualified').length;
  const partial = projects.filter(p => p.qualification_status === 'partially_qualified').length;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'qualified': return 'bg-green-100 text-green-700';
      case 'partially_qualified': return 'bg-amber-100 text-amber-700';
      case 'not_qualified': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{projects.length} Projects</h3>
          <p className="text-sm text-gray-500">
            {qualified} Qualified | {partial} Partially Qualified
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Project
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map(project => (
          <div key={project.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-900">{project.name}</h4>
                <p className="text-sm text-gray-500">{project.department}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(project.qualification_status || 'pending')}`}>
                {(project.qualification_status || 'pending').replace('_', ' ')}
              </span>
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.description}</p>

            <div className="border-t pt-3">
              <p className="text-xs text-gray-500 mb-2">4-Part Test Scores</p>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { label: 'Purpose', value: project.permitted_purpose_score },
                  { label: 'Tech', value: project.technological_nature_score },
                  { label: 'Uncertain', value: project.uncertainty_score },
                  { label: 'Experiment', value: project.experimentation_score },
                ].map(score => (
                  <div key={score.label} className="text-center">
                    <div className={`text-lg font-bold ${
                      (score.value || 0) >= 0.7 ? 'text-green-600' :
                      (score.value || 0) >= 0.5 ? 'text-amber-600' : 'text-red-600'
                    }`}>
                      {((score.value || 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">{score.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between mt-4 pt-3 border-t">
              <span className="text-sm text-gray-600">
                QRE: <strong>{formatCurrency(project.total_qre || 0)}</strong>
              </span>
              <button className="text-purple-600 hover:text-purple-700 text-sm font-medium">
                Edit Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// QRE Summary Tab
const QRESummaryTab: React.FC<{
  studyId: string;
  qreSummary: QRESummary | null;
  study: RDStudy | null;
}> = ({ studyId, qreSummary, study }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const categories = qreSummary?.by_category || {};
  const totalQRE = study?.total_qre || qreSummary?.total_qualified || 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <p className="text-purple-100 text-sm">Total QRE</p>
          <p className="text-2xl font-bold">{formatCurrency(totalQRE)}</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <p className="text-green-100 text-sm">Federal Credit</p>
          <p className="text-2xl font-bold">{formatCurrency(study?.federal_credit_final || 0)}</p>
        </div>
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <p className="text-blue-100 text-sm">State Credits</p>
          <p className="text-2xl font-bold">{formatCurrency(study?.total_state_credits || 0)}</p>
        </div>
        <div className="card bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
          <p className="text-emerald-100 text-sm">Total Credits</p>
          <p className="text-2xl font-bold">{formatCurrency(study?.total_credits || 0)}</p>
        </div>
      </div>

      {/* QRE Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">QRE by Category</h3>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Category</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">IRC Ref</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">Amount</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">%</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr>
                <td className="px-4 py-3">Wages</td>
                <td className="px-4 py-3 text-gray-500">§41(b)(2)(A)</td>
                <td className="px-4 py-3 text-right">{formatCurrency(categories.wages?.qualified || 0)}</td>
                <td className="px-4 py-3 text-right text-gray-500">
                  {totalQRE ? ((categories.wages?.qualified || 0) / totalQRE * 100).toFixed(1) : 0}%
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3">Supplies</td>
                <td className="px-4 py-3 text-gray-500">§41(b)(2)(C)</td>
                <td className="px-4 py-3 text-right">{formatCurrency(categories.supplies?.qualified || 0)}</td>
                <td className="px-4 py-3 text-right text-gray-500">
                  {totalQRE ? ((categories.supplies?.qualified || 0) / totalQRE * 100).toFixed(1) : 0}%
                </td>
              </tr>
              <tr>
                <td className="px-4 py-3">Contract Research</td>
                <td className="px-4 py-3 text-gray-500">§41(b)(3)</td>
                <td className="px-4 py-3 text-right">{formatCurrency(categories.contract?.qualified || 0)}</td>
                <td className="px-4 py-3 text-right text-gray-500">
                  {totalQRE ? ((categories.contract?.qualified || 0) / totalQRE * 100).toFixed(1) : 0}%
                </td>
              </tr>
            </tbody>
            <tfoot className="bg-gray-50 font-medium">
              <tr>
                <td className="px-4 py-3" colSpan={2}>Total</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totalQRE)}</td>
                <td className="px-4 py-3 text-right">100%</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Credit Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Total QRE</span>
              <span className="font-medium">{formatCurrency(totalQRE)}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Calculation Method</span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded font-medium">
                {study?.selected_method?.toUpperCase() || 'ASC'}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Federal Credit</span>
              <span className="font-medium">{formatCurrency(study?.federal_credit_final || 0)}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">State Credits ({study?.states?.length || 0} states)</span>
              <span className="font-medium">{formatCurrency(study?.total_state_credits || 0)}</span>
            </div>
            <div className="flex justify-between py-3 bg-green-50 -mx-4 px-4 rounded-lg">
              <span className="font-semibold text-gray-900">Total Credits</span>
              <span className="text-xl font-bold text-green-600">{formatCurrency(study?.total_credits || 0)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Calculations Tab
const CalculationsTab: React.FC<{
  studyId: string;
  study: RDStudy | null;
  onCalculate: () => void;
  calculating: boolean;
}> = ({ studyId, study, onCalculate, calculating }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Credit Calculations</h3>
        <button
          onClick={onCalculate}
          disabled={calculating}
          className="btn-primary flex items-center gap-2"
        >
          {calculating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Calculator className="w-4 h-4" />
          )}
          {calculating ? 'Calculating...' : 'Recalculate'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Regular Method */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-gray-900">Federal - Regular Method</h4>
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">20% Credit Rate</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Total QRE</span>
              <span>{formatCurrency(study?.total_qre || 0)}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Base Amount</span>
              <span>{formatCurrency(study?.regular_base_amount || 0)}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Excess QRE</span>
              <span>{formatCurrency(Math.max(0, (study?.total_qre || 0) - (study?.regular_base_amount || 0)))}</span>
            </div>
            <div className="flex justify-between py-3 bg-blue-50 -mx-4 px-4 rounded-lg">
              <span className="font-semibold">Regular Credit</span>
              <span className="text-xl font-bold text-blue-600">{formatCurrency(study?.federal_credit_regular || 0)}</span>
            </div>
          </div>
        </div>

        {/* ASC Method */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-gray-900">Federal - ASC Method</h4>
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">14% Credit Rate</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Total QRE</span>
              <span>{formatCurrency(study?.total_qre || 0)}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Base Amount (50% avg)</span>
              <span>{formatCurrency(study?.asc_base_amount || 0)}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Excess QRE</span>
              <span>{formatCurrency(Math.max(0, (study?.total_qre || 0) - (study?.asc_base_amount || 0)))}</span>
            </div>
            <div className="flex justify-between py-3 bg-indigo-50 -mx-4 px-4 rounded-lg">
              <span className="font-semibold">ASC Credit</span>
              <span className="text-xl font-bold text-indigo-600">{formatCurrency(study?.federal_credit_asc || 0)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      {study?.recommended_method && (
        <div className="card bg-green-50 border-green-200">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-semibold text-green-800">
                Recommended: {study.recommended_method === 'asc' ? 'ASC' : 'Regular'} Method
              </p>
              {study.method_selection_reason && (
                <p className="text-sm text-green-700">{study.method_selection_reason}</p>
              )}
            </div>
            <div className="ml-auto text-right">
              <p className="text-sm text-green-600">Final Federal Credit</p>
              <p className="text-2xl font-bold text-green-700">{formatCurrency(study.federal_credit_final || 0)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Generate & Export Tab
const GenerateExportTab: React.FC<{
  studyId: string;
  study: RDStudy | null;
}> = ({ studyId, study }) => {
  const [generating, setGenerating] = useState<string | null>(null);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const handleGenerate = async (type: 'pdf' | 'excel' | 'form_6765', isFinal: boolean = false) => {
    setGenerating(type);
    try {
      const token = localStorage.getItem('access_token');
      const endpoint = type === 'pdf'
        ? `${API_BASE_URL}/rd-study/studies/${studyId}/generate/pdf?is_final=${isFinal}`
        : type === 'excel'
        ? `${API_BASE_URL}/rd-study/studies/${studyId}/generate/excel`
        : `${API_BASE_URL}/rd-study/studies/${studyId}/generate/form-6765`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = type === 'pdf'
          ? `RD_Study_${study?.entity_name}_${study?.tax_year}${isFinal ? '_FINAL' : '_DRAFT'}.pdf`
          : type === 'excel'
          ? `RD_Study_Workbook_${study?.entity_name}_${study?.tax_year}.xlsx`
          : `Form_6765_${study?.entity_name}_${study?.tax_year}.pdf`;
        a.click();
        toast.success(`${type.toUpperCase()} generated successfully!`);
      } else {
        toast.error('Failed to generate document');
      }
    } catch (error) {
      console.error('Generate failed:', error);
      toast.error('Failed to generate document');
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* PDF Report */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <File className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">PDF Study Report</h3>
              <p className="text-sm text-gray-500">Comprehensive audit-ready report</p>
            </div>
          </div>

          <ul className="space-y-2 mb-6 text-sm text-gray-600">
            {[
              'Professional Cover Page',
              'Executive Summary',
              'Methodology & Qualification Analysis',
              'QRE Schedules & Breakdowns',
              'Federal & State Credit Calculations',
              'Project Narratives',
              'IRC Section 41 Citations',
            ].map(item => (
              <li key={item} className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                {item}
              </li>
            ))}
          </ul>

          <div className="flex gap-3">
            <button
              onClick={() => handleGenerate('pdf', false)}
              disabled={generating === 'pdf'}
              className="flex-1 btn-secondary flex items-center justify-center gap-2"
            >
              {generating === 'pdf' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Download Draft
            </button>
            <button
              onClick={() => handleGenerate('pdf', true)}
              disabled={generating === 'pdf'}
              className="flex-1 btn-primary flex items-center justify-center gap-2"
            >
              {generating === 'pdf' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Download Final
            </button>
          </div>
        </div>

        {/* Excel Workbook */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <FileSpreadsheet className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Excel Workbook</h3>
              <p className="text-sm text-gray-500">Detailed multi-sheet workbook</p>
            </div>
          </div>

          <ul className="space-y-2 mb-6 text-sm text-gray-600">
            {[
              'Summary Dashboard',
              'QRE Summary with Charts',
              'Employee Schedule',
              'Project Analysis',
              'Wage/Supply/Contract QRE Detail',
              'Federal Regular & ASC Calculations',
              'State Credit Worksheets',
              'Reconciliation & Sanity Checks',
              'Form 6765 Data',
            ].map(item => (
              <li key={item} className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                {item}
              </li>
            ))}
          </ul>

          <button
            onClick={() => handleGenerate('excel')}
            disabled={generating === 'excel'}
            className="w-full btn-primary bg-green-600 hover:bg-green-700 flex items-center justify-center gap-2"
          >
            {generating === 'excel' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Download Excel Workbook
          </button>
        </div>
      </div>

      {/* Credit Summary */}
      <div className="card bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold">{study?.entity_name}</h3>
            <p className="text-purple-200">Tax Year {study?.tax_year}</p>
            <div className="mt-2 flex items-center gap-4 text-sm text-purple-200">
              <span>Federal: {formatCurrency(study?.federal_credit_final || 0)}</span>
              <span>|</span>
              <span>State: {formatCurrency(study?.total_state_credits || 0)}</span>
              <span>|</span>
              <span>Method: {study?.selected_method?.toUpperCase() || 'ASC'}</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-purple-200 text-sm">Total R&D Credit</p>
            <p className="text-3xl font-bold">{formatCurrency(study?.total_credits || 0)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Component
const RDStudyWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [study, setStudy] = useState<RDStudy | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabId>('data-collection');
  const [projects, setProjects] = useState<RDProject[]>([]);
  const [employees, setEmployees] = useState<RDEmployee[]>([]);
  const [qreSummary, setQreSummary] = useState<QRESummary | null>(null);
  const [calculating, setCalculating] = useState(false);

  const loadStudy = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await rdStudyService.getStudy(id);
      setStudy(data);
    } catch (error) {
      console.error('Failed to load study:', error);
      toast.error('Failed to load study');
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadTabData = useCallback(async () => {
    if (!study) return;

    try {
      switch (activeTab) {
        case 'projects':
          const projectData = await rdStudyService.listProjects(study.id);
          setProjects(projectData);
          break;
        case 'employees':
          const employeeData = await rdStudyService.listEmployees(study.id);
          setEmployees(employeeData);
          break;
        case 'qres':
          const qreData = await rdStudyService.getQRESummary(study.id);
          setQreSummary(qreData);
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${activeTab} data:`, error);
    }
  }, [study, activeTab]);

  useEffect(() => {
    loadStudy();
  }, [loadStudy]);

  useEffect(() => {
    loadTabData();
  }, [loadTabData]);

  const handleCalculate = async () => {
    if (!study) return;
    setCalculating(true);
    try {
      await rdStudyService.calculateCredits(study.id);
      toast.success('Credits calculated successfully');
      loadStudy();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Calculation failed');
    } finally {
      setCalculating(false);
    }
  };

  const handleDataImported = () => {
    loadStudy();
    loadTabData();
    toast.success('Data imported successfully!');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
          <p className="text-gray-600">Loading study...</p>
        </div>
      </div>
    );
  }

  if (!study) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl text-gray-600">Study not found</h2>
        <button onClick={() => navigate('/firm/rd-studies')} className="btn-primary mt-4">
          Back to Studies
        </button>
      </div>
    );
  }

  const status = statusConfig[study.status] || statusConfig.draft;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={() => navigate('/firm/rd-studies')}
            className="text-sm text-gray-600 hover:text-gray-900 mb-3 flex items-center gap-1"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to R&D Studies
          </button>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center">
              <FlaskConical className="w-7 h-7 text-purple-600" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">{study.name}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${status.bgColor} ${status.color}`}>
                  {status.label}
                </span>
              </div>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {study.entity_name}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  Tax Year {study.tax_year}
                </span>
                {study.ein && <span>EIN: {study.ein}</span>}
              </div>
            </div>
          </div>
        </div>

        <div className="text-right">
          <p className="text-sm text-gray-500">Total R&D Credit</p>
          <p className="text-3xl font-bold text-green-600">{formatCurrency(study.total_credits || 0)}</p>
        </div>
      </div>

      {/* Credit Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total QRE</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(study.total_qre || 0)}</p>
            </div>
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Federal Credit</p>
              <p className="text-2xl font-bold text-blue-600">{formatCurrency(study.federal_credit_final || 0)}</p>
              <p className="text-xs text-gray-400">{study.selected_method === 'asc' ? 'ASC Method' : 'Regular Method'}</p>
            </div>
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">State Credits</p>
              <p className="text-2xl font-bold text-indigo-600">{formatCurrency(study.total_state_credits || 0)}</p>
              <p className="text-xs text-gray-400">{study.states?.length || 0} state(s)</p>
            </div>
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Total Credits</p>
              <p className="text-2xl font-bold">{formatCurrency(study.total_credits || 0)}</p>
            </div>
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  isActive
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'data-collection' && (
            <DataCollectionTab studyId={study.id} onDataImported={handleDataImported} />
          )}
          {activeTab === 'client-invitations' && (
            <ClientInvitationsTab studyId={study.id} study={study} onRefresh={loadStudy} />
          )}
          {activeTab === 'employees' && (
            <EmployeesTab studyId={study.id} employees={employees} onRefresh={loadTabData} />
          )}
          {activeTab === 'projects' && (
            <ProjectsTab studyId={study.id} projects={projects} onRefresh={loadTabData} />
          )}
          {activeTab === 'qres' && (
            <QRESummaryTab studyId={study.id} qreSummary={qreSummary} study={study} />
          )}
          {activeTab === 'calculations' && (
            <CalculationsTab studyId={study.id} study={study} onCalculate={handleCalculate} calculating={calculating} />
          )}
          {activeTab === 'generate' && (
            <GenerateExportTab studyId={study.id} study={study} />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default RDStudyWorkspace;
