/**
 * Client Portal - Regulation A/B Audit Page
 * Redesigned with Microsoft Fluent Design System
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  CheckCircle,
  Clock,
  FileText,
  TrendingUp,
  AlertCircle,
  DollarSign,
  Activity,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface CMBSDeal {
  id: string;
  deal_name: string;
  deal_number: string;
  cusip?: string;
  current_balance: number;
  dscr?: number;
  ltv?: number;
  status: string;
  submitted_at?: string;
}

interface AuditEngagement {
  id: string;
  audit_name: string;
  status: string;
  total_cmbs_deals: number;
  processed_deals: number;
  total_compliance_checks: number;
  passed_compliance_checks: number;
  failed_compliance_checks: number;
}

export default function RegABAuditPage() {
  const [engagements, setEngagements] = useState<AuditEngagement[]>([]);
  const [selectedEngagement, setSelectedEngagement] = useState<string | null>(null);
  const [deals, setDeals] = useState<CMBSDeal[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);

  useEffect(() => {
    fetchEngagements();
  }, []);

  useEffect(() => {
    if (selectedEngagement) {
      fetchDeals(selectedEngagement);
    }
  }, [selectedEngagement]);

  const fetchEngagements = async () => {
    try {
      setLoading(true);
      const apiUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:5001';
      const response = await fetch(`${apiUrl}/api/client/reg-ab/engagements`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch engagements');
      const data = await response.json();
      setEngagements(data);
    } catch (error) {
      console.error('Error fetching engagements:', error);
      toast.error('Failed to load audit engagements');
    } finally {
      setLoading(false);
    }
  };

  const fetchDeals = async (engagementId: string) => {
    try {
      setLoading(true);
      const apiUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:5001';
      const response = await fetch(`${apiUrl}/api/client/reg-ab/engagements/${engagementId}/deals`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch deals');
      const data = await response.json();
      setDeals(data);
    } catch (error) {
      console.error('Error fetching deals:', error);
      toast.error('Failed to load CMBS deals');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Deal submitted for audit');
    setOpenDialog(false);
    if (selectedEngagement) {
      fetchDeals(selectedEngagement);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { class: string; icon: JSX.Element }> = {
      completed: { class: 'fluent-badge-success', icon: <CheckCircle size={14} /> },
      in_progress: { class: 'fluent-badge-info', icon: <Clock size={14} /> },
      pending: { class: 'fluent-badge-warning', icon: <AlertCircle size={14} /> },
    };

    const config = statusConfig[status.toLowerCase()] || statusConfig.pending;
    return (
      <span className={`${config.class} inline-flex items-center gap-1`}>
        {config.icon}
        {status}
      </span>
    );
  };

  if (loading && engagements.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
          <p className="text-secondary">Loading audit engagements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-fluent-gray-10 via-white to-fluent-blue-50 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-display-large text-primary font-semibold">
              Regulation A/B Audit
            </h1>
            <p className="text-body text-secondary mt-2">
              Submit and track CMBS deals for compliance audit
            </p>
          </div>
          <button
            onClick={() => setOpenDialog(true)}
            className="fluent-button-primary inline-flex items-center gap-2"
          >
            <Plus size={20} />
            Submit Deal
          </button>
        </div>
      </motion.div>

      {/* Stats Cards */}
      {selectedEngagement && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          {[
            {
              title: 'Total Deals',
              value: engagements.find(e => e.id === selectedEngagement)?.total_cmbs_deals || 0,
              icon: <FileText size={24} className="text-fluent-blue-500" />,
              color: 'bg-fluent-blue-50',
            },
            {
              title: 'Processed',
              value: engagements.find(e => e.id === selectedEngagement)?.processed_deals || 0,
              icon: <CheckCircle size={24} className="text-fluent-green-500" />,
              color: 'bg-fluent-green-50',
            },
            {
              title: 'Compliance Checks',
              value: engagements.find(e => e.id === selectedEngagement)?.total_compliance_checks || 0,
              icon: <Activity size={24} className="text-fluent-purple-500" />,
              color: 'bg-fluent-purple-50',
            },
            {
              title: 'Pass Rate',
              value: `${Math.round(((engagements.find(e => e.id === selectedEngagement)?.passed_compliance_checks || 0) / (engagements.find(e => e.id === selectedEngagement)?.total_compliance_checks || 1)) * 100)}%`,
              icon: <TrendingUp size={24} className="text-fluent-teal-500" />,
              color: 'bg-fluent-teal-50',
            },
          ].map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="fluent-card p-6"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-body text-secondary mb-2">{stat.title}</p>
                  <p className="text-display text-primary font-semibold">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 rounded-fluent flex items-center justify-center ${stat.color}`}>
                  {stat.icon}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Engagements */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Engagement List */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="fluent-card p-6"
        >
          <h2 className="text-title text-primary font-semibold mb-4">Audit Engagements</h2>
          <div className="space-y-2">
            {engagements.map((engagement) => (
              <button
                key={engagement.id}
                onClick={() => setSelectedEngagement(engagement.id)}
                className={`w-full text-left p-4 rounded-fluent transition-all ${
                  selectedEngagement === engagement.id
                    ? 'bg-fluent-blue-50 border-2 border-brand'
                    : 'bg-fluent-gray-10 hover:bg-fluent-gray-20 border-2 border-transparent'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-subtitle text-primary">{engagement.audit_name}</h3>
                  {getStatusBadge(engagement.status)}
                </div>
                <div className="flex items-center gap-4 text-caption text-secondary">
                  <span>{engagement.total_cmbs_deals} deals</span>
                  <span>•</span>
                  <span>{engagement.processed_deals} processed</span>
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Deals Table */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-2 fluent-card p-6"
        >
          <h2 className="text-title text-primary font-semibold mb-4">CMBS Deals</h2>
          {selectedEngagement ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-fluent-gray-40">
                    <th className="text-left py-3 px-4 text-body font-semibold text-secondary">Deal Name</th>
                    <th className="text-left py-3 px-4 text-body font-semibold text-secondary">Deal #</th>
                    <th className="text-right py-3 px-4 text-body font-semibold text-secondary">Balance</th>
                    <th className="text-left py-3 px-4 text-body font-semibold text-secondary">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {deals.map((deal) => (
                    <tr key={deal.id} className="border-b border-fluent-gray-30 hover:bg-fluent-gray-10 transition-colors">
                      <td className="py-3 px-4 text-body text-primary">{deal.deal_name}</td>
                      <td className="py-3 px-4 text-body text-secondary">{deal.deal_number}</td>
                      <td className="py-3 px-4 text-body text-primary text-right">
                        ${deal.current_balance.toLocaleString()}
                      </td>
                      <td className="py-3 px-4">{getStatusBadge(deal.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <FileText size={48} className="mx-auto text-fluent-gray-70 mb-4" />
              <p className="text-body text-secondary">Select an engagement to view deals</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Submit Dialog */}
      {openDialog && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="acrylic rounded-fluent-lg p-6 max-w-md w-full depth-64"
          >
            <h2 className="text-title text-primary font-semibold mb-4">Submit CMBS Deal</h2>
            <form onSubmit={handleSubmitDeal} className="space-y-4">
              <div>
                <label className="block text-body text-secondary mb-2">Deal Name</label>
                <input type="text" className="fluent-input" placeholder="Enter deal name" required />
              </div>
              <div>
                <label className="block text-body text-secondary mb-2">Deal Number</label>
                <input type="text" className="fluent-input" placeholder="Enter deal number" required />
              </div>
              <div>
                <label className="block text-body text-secondary mb-2">Current Balance</label>
                <input type="number" className="fluent-input" placeholder="0.00" required />
              </div>
              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setOpenDialog(false)} className="fluent-button-secondary flex-1">
                  Cancel
                </button>
                <button type="submit" className="fluent-button-primary flex-1">
                  Submit
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
}
