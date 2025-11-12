/**
 * Client Portal - Regulation A/B Audit Page
 *
 * Allows clients to submit CMBS deals for audit and track progress
 */

import { useState, useEffect } from 'react';
import { Plus, CheckCircle, Clock, FileText } from 'lucide-react';

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
      const response = await fetch(
        `${import.meta.env.VITE_REG_AB_API_URL || 'http://localhost:8011'}/api/engagements`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setEngagements(data);
        if (data.length > 0) {
          setSelectedEngagement(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching engagements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDeals = async (engagementId: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_REG_AB_API_URL || 'http://localhost:8011'}/api/engagements/${engagementId}/deals`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDeals(data);
      }
    } catch (error) {
      console.error('Error fetching deals:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      active: { label: 'Active', className: 'bg-green-100 text-green-800' },
      pending_audit: { label: 'Pending Audit', className: 'bg-yellow-100 text-yellow-800' },
      audit_complete: { label: 'Complete', className: 'bg-green-100 text-green-800' },
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-800' },
      ai_processing: { label: 'Processing', className: 'bg-blue-100 text-blue-800' },
      cpa_review: { label: 'CPA Review', className: 'bg-purple-100 text-purple-800' },
      finalized: { label: 'Finalized', className: 'bg-green-100 text-green-800' },
    };

    const statusInfo = statusMap[status] || { label: status, className: 'bg-gray-100 text-gray-800' };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusInfo.className}`}>
        {statusInfo.label}
      </span>
    );
  };

  const currentEngagement = engagements.find((e) => e.id === selectedEngagement);
  const progress = currentEngagement
    ? (currentEngagement.processed_deals / Math.max(currentEngagement.total_cmbs_deals, 1)) * 100
    : 0;

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Regulation A/B Audit
        </h1>
        <p className="text-gray-600">
          Submit and track CMBS deals for Regulation A/B compliance auditing
        </p>
      </div>

      {engagements.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-blue-800 font-semibold mb-2">No Active Engagements</h3>
          <p className="text-blue-700">
            Contact your CPA firm to initiate a Regulation A/B audit engagement.
          </p>
        </div>
      ) : (
        <>
          {/* Engagement Summary */}
          {currentEngagement && (
            <div className="bg-white rounded-lg shadow-md mb-6">
              <div className="border-b border-gray-200 p-6 flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {currentEngagement.audit_name}
                  </h2>
                  <p className="text-sm text-gray-600">Status: {currentEngagement.status}</p>
                </div>
                {getStatusBadge(currentEngagement.status)}
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                  <div>
                    <div className="text-3xl font-bold text-blue-600">
                      {currentEngagement.total_cmbs_deals}
                    </div>
                    <div className="text-sm text-gray-600">Total Deals</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-green-600">
                      {currentEngagement.processed_deals}
                    </div>
                    <div className="text-sm text-gray-600">Processed</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-blue-500">
                      {currentEngagement.passed_compliance_checks}
                    </div>
                    <div className="text-sm text-gray-600">Checks Passed</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-red-600">
                      {currentEngagement.failed_compliance_checks}
                    </div>
                    <div className="text-sm text-gray-600">Checks Failed</div>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-600">Processing Progress</span>
                    <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mb-6 flex justify-end">
            <button
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={() => setOpenDialog(true)}
            >
              <Plus size={20} />
              Add CMBS Deal
            </button>
          </div>

          {/* Deals Table */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deal Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deal Number</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CUSIP</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Current Balance</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">DSCR</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">LTV</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Submitted</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {deals.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-12 text-center">
                        <p className="text-gray-500">
                          No CMBS deals submitted yet. Click "Add CMBS Deal" to get started.
                        </p>
                      </td>
                    </tr>
                  ) : (
                    deals.map((deal) => (
                      <tr key={deal.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{deal.deal_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{deal.deal_number}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{deal.cusip || '—'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                          ${deal.current_balance.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
                          {deal.dscr ? deal.dscr.toFixed(2) : '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
                          {deal.ltv ? `${deal.ltv.toFixed(1)}%` : '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(deal.status)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {deal.submitted_at ? new Date(deal.submitted_at).toLocaleDateString() : '—'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Add Deal Dialog - Simplified for demo */}
      {openDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Add CMBS Deal</h2>
            </div>
            <div className="p-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-blue-800 text-sm">
                  This is a simplified form. In production, this would include comprehensive CMBS deal data entry.
                </p>
              </div>
              <div className="space-y-4">
                <input type="text" placeholder="Deal Name" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                <input type="text" placeholder="Deal Number" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                <input type="text" placeholder="CUSIP" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                <input type="number" placeholder="Current Balance" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                <input type="number" placeholder="DSCR" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
                <input type="number" placeholder="LTV (%)" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setOpenDialog(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setOpenDialog(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Submit Deal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
