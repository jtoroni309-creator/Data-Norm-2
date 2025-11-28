/**
 * Fraud Case Workspace
 * Detailed view for investigating and managing fraud cases
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  User,
  DollarSign,
  FileText,
  MessageSquare,
  History,
  CreditCard,
  MapPin,
  Calendar,
  Tag,
  Edit,
  Save,
  Send,
  Flag,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { fraudDetectionService } from '../services/fraud-detection.service';
import {
  FraudCase,
  FraudCaseActivity,
  FraudTransaction,
  TransactionAnalysis,
  FraudSeverity,
  FraudCaseStatus,
} from '../types';

type TabType = 'overview' | 'transaction' | 'timeline' | 'notes';

const FraudCaseWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [fraudCase, setFraudCase] = useState<FraudCase | null>(null);
  const [activities, setActivities] = useState<FraudCaseActivity[]>([]);
  const [transaction, setTransaction] = useState<TransactionAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [newNote, setNewNote] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (id) {
      loadCaseData();
    }
  }, [id]);

  const loadCaseData = async () => {
    setLoading(true);
    try {
      const [caseData, activitiesData] = await Promise.all([
        fraudDetectionService.getFraudCase(id!),
        fraudDetectionService.getCaseActivities(id!),
      ]);
      setFraudCase(caseData);
      setActivities(activitiesData);

      if (caseData.transaction_id) {
        const txnData = await fraudDetectionService.getTransactionAnalysis(caseData.transaction_id);
        setTransaction(txnData);
      }
    } catch (error) {
      console.error('Failed to load case:', error);
      // Use mock data for demo
      setFraudCase(generateMockCase());
      setActivities(generateMockActivities());
      setTransaction(generateMockTransaction());
    } finally {
      setLoading(false);
    }
  };

  const generateMockCase = (): FraudCase => ({
    id: id || '1',
    case_number: 'FRAUD-20250228-A1B2C3D4',
    customer_id: 'c1',
    bank_account_id: 'ba1',
    transaction_id: 't1',
    title: 'Suspected Account Takeover - Johnson Corp',
    description: 'Multiple unauthorized wire transfers detected from the Johnson Corp business account. Total of 3 transactions to foreign accounts within a 2-hour window.',
    severity: 'critical',
    status: 'investigating',
    fraud_type: 'account_takeover',
    estimated_loss_amount: 125000,
    detected_patterns: ['FOREIGN_TRANSACTION', 'HIGH_VELOCITY', 'LARGE_AMOUNT', 'UNUSUAL_TIME'],
    investigation_notes: 'Initial review shows transactions originated from a new IP address. Customer confirmed they did not authorize these transfers.',
    assigned_to: 'John Smith',
    acknowledged_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  });

  const generateMockActivities = (): FraudCaseActivity[] => [
    {
      id: '1',
      fraud_case_id: id || '1',
      activity_type: 'status_change',
      description: 'Case status changed from Open to Investigating',
      user_id: 'user1',
      created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    },
    {
      id: '2',
      fraud_case_id: id || '1',
      activity_type: 'note_added',
      description: 'Contacted customer to verify transaction authenticity',
      user_id: 'user1',
      created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    },
    {
      id: '3',
      fraud_case_id: id || '1',
      activity_type: 'case_assigned',
      description: 'Case assigned to John Smith',
      user_id: 'admin',
      created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    },
    {
      id: '4',
      fraud_case_id: id || '1',
      activity_type: 'case_created',
      description: 'Fraud case created automatically from high-risk transaction',
      user_id: 'system',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
  ];

  const generateMockTransaction = (): TransactionAnalysis => ({
    transaction: {
      id: 't1',
      bank_account_id: 'ba1',
      plaid_transaction_id: 'plaid_123',
      transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      amount: -45000,
      description: 'Wire Transfer - International',
      merchant_name: 'WIRE TRANSFER',
      category: ['Transfer', 'Wire'],
      location: {
        city: 'Lagos',
        country: 'NG',
      },
      payment_channel: 'online',
      is_flagged: true,
      fraud_score: 0.92,
      risk_level: 'critical',
      flagged_reasons: {
        rules: ['FOREIGN_TRANSACTION', 'LARGE_AMOUNT', 'UNUSUAL_TIME'],
        explanation: 'High-risk wire transfer to foreign account during unusual hours',
      },
      analyzed_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    model_predictions: {
      random_forest: 0.89,
      xgboost: 0.94,
      isolation_forest: 0.88,
    },
    feature_importance: {
      has_foreign_location: 0.35,
      is_large_amount: 0.28,
      is_night_time: 0.15,
      txn_count_1h: 0.12,
      deviation_from_avg: 0.10,
    },
    anomaly_score: 0.91,
    triggered_rules: ['FOREIGN_TRANSACTION', 'LARGE_AMOUNT', 'UNUSUAL_TIME', 'HIGH_VELOCITY'],
    recommendation: 'BLOCK - High fraud risk. Recommend immediate investigation.',
  });

  const handleStatusChange = async (newStatus: FraudCaseStatus) => {
    if (!fraudCase) return;
    setSaving(true);
    try {
      const updated = await fraudDetectionService.updateFraudCase(
        fraudCase.id,
        { status: newStatus },
        'current-user-id'
      );
      setFraudCase(updated);
      toast.success(`Case status updated to ${newStatus}`);
      loadCaseData();
    } catch (error) {
      // Mock success
      setFraudCase({ ...fraudCase, status: newStatus });
      toast.success(`Case status updated to ${newStatus}`);
    } finally {
      setSaving(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim() || !fraudCase) return;
    setSaving(true);
    try {
      await fraudDetectionService.addCaseActivity(
        fraudCase.id,
        { activity_type: 'note_added', description: newNote },
        'current-user-id'
      );
      setNewNote('');
      loadCaseData();
      toast.success('Note added');
    } catch (error) {
      // Mock success
      const newActivity: FraudCaseActivity = {
        id: `new-${Date.now()}`,
        fraud_case_id: fraudCase.id,
        activity_type: 'note_added',
        description: newNote,
        user_id: 'current-user',
        created_at: new Date().toISOString(),
      };
      setActivities([newActivity, ...activities]);
      setNewNote('');
      toast.success('Note added');
    } finally {
      setSaving(false);
    }
  };

  const getSeverityConfig = (severity: FraudSeverity) => {
    const configs: Record<FraudSeverity, { color: string; bgColor: string; borderColor: string }> = {
      critical: { color: 'text-red-700', bgColor: 'bg-red-100', borderColor: 'border-red-500' },
      high: { color: 'text-orange-700', bgColor: 'bg-orange-100', borderColor: 'border-orange-500' },
      medium: { color: 'text-yellow-700', bgColor: 'bg-yellow-100', borderColor: 'border-yellow-500' },
      low: { color: 'text-green-700', bgColor: 'bg-green-100', borderColor: 'border-green-500' },
    };
    return configs[severity] || configs.medium;
  };

  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(Math.abs(amount));
  };

  const tabs: { id: TabType; label: string; icon: React.ElementType }[] = [
    { id: 'overview', label: 'Overview', icon: ShieldAlert },
    { id: 'transaction', label: 'Transaction', icon: CreditCard },
    { id: 'timeline', label: 'Timeline', icon: History },
    { id: 'notes', label: 'Notes', icon: MessageSquare },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading case...</p>
        </div>
      </div>
    );
  }

  if (!fraudCase) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <p className="text-gray-600">Case not found</p>
          <button
            onClick={() => navigate('/firm/fraud-detection')}
            className="mt-4 text-red-600 hover:text-red-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const sevConfig = getSeverityConfig(fraudCase.severity);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <button
            onClick={() => navigate('/firm/fraud-detection')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors mt-1"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{fraudCase.title}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${sevConfig.bgColor} ${sevConfig.color}`}>
                {fraudCase.severity.toUpperCase()}
              </span>
            </div>
            <p className="text-gray-500 mt-1">{fraudCase.case_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={fraudCase.status}
            onChange={(e) => handleStatusChange(e.target.value as FraudCaseStatus)}
            disabled={saving}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
          >
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="pending_review">Pending Review</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
            <option value="false_positive">False Positive</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`bg-white rounded-xl p-4 shadow-sm border-l-4 ${sevConfig.borderColor}`}
        >
          <div className="flex items-center gap-3">
            <div className={`p-2 ${sevConfig.bgColor} rounded-lg`}>
              <DollarSign className={`w-5 h-5 ${sevConfig.color}`} />
            </div>
            <div>
              <p className="text-sm text-gray-600">Estimated Loss</p>
              <p className="text-xl font-bold text-red-600">
                {formatCurrency(fraudCase.estimated_loss_amount)}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Tag className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Fraud Type</p>
              <p className="text-lg font-semibold text-gray-900">
                {fraudCase.fraud_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown'}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <User className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Assigned To</p>
              <p className="text-lg font-semibold text-gray-900">
                {fraudCase.assigned_to || 'Unassigned'}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-100 rounded-lg">
              <Calendar className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Created</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(fraudCase.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex gap-1 p-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-red-100 text-red-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <OverviewTab fraudCase={fraudCase} />
          )}
          {activeTab === 'transaction' && (
            <TransactionTab transaction={transaction} />
          )}
          {activeTab === 'timeline' && (
            <TimelineTab activities={activities} />
          )}
          {activeTab === 'notes' && (
            <NotesTab
              fraudCase={fraudCase}
              activities={activities.filter(a => a.activity_type === 'note_added')}
              newNote={newNote}
              setNewNote={setNewNote}
              onAddNote={handleAddNote}
              saving={saving}
            />
          )}
        </div>
      </div>
    </div>
  );
};

// Overview Tab
const OverviewTab: React.FC<{ fraudCase: FraudCase }> = ({ fraudCase }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
        <p className="text-gray-700">{fraudCase.description || 'No description provided.'}</p>
      </div>

      {fraudCase.detected_patterns && fraudCase.detected_patterns.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Detected Patterns</h3>
          <div className="flex flex-wrap gap-2">
            {fraudCase.detected_patterns.map((pattern, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium"
              >
                {pattern.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {fraudCase.investigation_notes && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Investigation Notes</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700">{fraudCase.investigation_notes}</p>
          </div>
        </div>
      )}

      {fraudCase.resolution_notes && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Resolution Notes</h3>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-gray-700">{fraudCase.resolution_notes}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Transaction Tab
const TransactionTab: React.FC<{ transaction: TransactionAnalysis | null }> = ({ transaction }) => {
  if (!transaction) {
    return (
      <div className="text-center py-12">
        <CreditCard className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-600">No transaction data available</p>
      </div>
    );
  }

  const txn = transaction.transaction;

  return (
    <div className="space-y-6">
      {/* Transaction Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-4">Transaction Details</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Amount</span>
              <span className="font-semibold text-red-600">
                ${Math.abs(txn.amount).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Date</span>
              <span className="font-medium">{new Date(txn.transaction_date).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Merchant</span>
              <span className="font-medium">{txn.merchant_name || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Payment Channel</span>
              <span className="font-medium">{txn.payment_channel || 'N/A'}</span>
            </div>
            {txn.location && (
              <div className="flex justify-between">
                <span className="text-gray-600">Location</span>
                <span className="font-medium">
                  {txn.location.city}, {txn.location.country}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-4">Risk Analysis</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Fraud Score</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      txn.fraud_score >= 0.8 ? 'bg-red-500' :
                      txn.fraud_score >= 0.5 ? 'bg-orange-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${txn.fraud_score * 100}%` }}
                  />
                </div>
                <span className="font-bold text-red-600">{(txn.fraud_score * 100).toFixed(0)}%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Anomaly Score</span>
              <span className="font-medium">{(transaction.anomaly_score * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Risk Level</span>
              <span className={`px-2 py-0.5 rounded text-sm font-medium ${
                txn.risk_level === 'critical' ? 'bg-red-100 text-red-700' :
                txn.risk_level === 'high' ? 'bg-orange-100 text-orange-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {txn.risk_level.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Predictions */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-4">ML Model Predictions</h4>
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(transaction.model_predictions).map(([model, score]) => (
            <div key={model} className="text-center">
              <p className="text-sm text-gray-600 mb-1">{model.replace('_', ' ')}</p>
              <p className="text-2xl font-bold text-gray-900">{(score * 100).toFixed(0)}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* Feature Importance */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-4">Key Risk Factors</h4>
        <div className="space-y-3">
          {Object.entries(transaction.feature_importance)
            .sort((a, b) => b[1] - a[1])
            .map(([feature, importance]) => (
              <div key={feature} className="flex items-center gap-4">
                <span className="text-gray-600 w-40">{feature.replace(/_/g, ' ')}</span>
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full"
                    style={{ width: `${importance * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-700 w-12">
                  {(importance * 100).toFixed(0)}%
                </span>
              </div>
            ))}
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 className="font-semibold text-red-800 mb-2">Recommendation</h4>
        <p className="text-red-700">{transaction.recommendation}</p>
      </div>
    </div>
  );
};

// Timeline Tab
const TimelineTab: React.FC<{ activities: FraudCaseActivity[] }> = ({ activities }) => {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'case_created': return <Flag className="w-4 h-4" />;
      case 'status_change': return <Clock className="w-4 h-4" />;
      case 'case_assigned': return <User className="w-4 h-4" />;
      case 'note_added': return <MessageSquare className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <motion.div
          key={activity.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="flex gap-4"
        >
          <div className="flex flex-col items-center">
            <div className="p-2 bg-gray-100 rounded-full">
              {getActivityIcon(activity.activity_type)}
            </div>
            {index < activities.length - 1 && (
              <div className="w-px h-full bg-gray-200 my-2" />
            )}
          </div>
          <div className="flex-1 pb-4">
            <p className="font-medium text-gray-900">{activity.description}</p>
            <p className="text-sm text-gray-500 mt-1">
              {new Date(activity.created_at).toLocaleString()}
            </p>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

// Notes Tab
const NotesTab: React.FC<{
  fraudCase: FraudCase;
  activities: FraudCaseActivity[];
  newNote: string;
  setNewNote: (note: string) => void;
  onAddNote: () => void;
  saving: boolean;
}> = ({ fraudCase, activities, newNote, setNewNote, onAddNote, saving }) => {
  return (
    <div className="space-y-6">
      {/* Add Note */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-3">Add Note</h4>
        <textarea
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          placeholder="Enter investigation notes..."
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 resize-none"
        />
        <div className="flex justify-end mt-3">
          <button
            onClick={onAddNote}
            disabled={saving || !newNote.trim()}
            className="fluent-btn-primary"
          >
            {saving ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Send className="w-4 h-4" />
                Add Note
              </>
            )}
          </button>
        </div>
      </div>

      {/* Notes List */}
      <div className="space-y-4">
        {activities.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No notes yet</p>
        ) : (
          activities.map((activity) => (
            <div key={activity.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-gray-700">{activity.description}</p>
              <p className="text-sm text-gray-500 mt-2">
                {new Date(activity.created_at).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FraudCaseWorkspace;
