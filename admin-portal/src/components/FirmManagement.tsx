import React, { useState, useEffect } from 'react';
import {
  Building2,
  Plus,
  Search,
  Settings,
  Users,
  MoreVertical,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  Shield,
  Globe
} from 'lucide-react';
import { tenantAPI, Tenant } from '../services/api';

interface ServiceToggle {
  id: string;
  name: string;
  enabled: boolean;
  category: string;
}

interface FirmWithServices extends Tenant {
  services: ServiceToggle[];
  userCount?: number;  // Computed field
}

const FirmManagement: React.FC = () => {
  const [firms, setFirms] = useState<FirmWithServices[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showServicesModal, setShowServicesModal] = useState(false);
  const [selectedFirm, setSelectedFirm] = useState<FirmWithServices | null>(null);
  const [newFirm, setNewFirm] = useState({
    firm_name: '',
    legal_name: '',
    ein: '',
    primary_contact_name: '',
    primary_contact_email: '',
    primary_contact_phone: '',
    subscription_tier: 'professional' as const,
  });

  // Available services that can be toggled per firm
  const availableServices: ServiceToggle[] = [
    // Core Services
    { id: 'analytics', name: 'Analytics', enabled: true, category: 'Core' },
    { id: 'llm', name: 'AI Language Model', enabled: true, category: 'Core' },
    { id: 'engagement', name: 'Engagement Management', enabled: true, category: 'Core' },
    { id: 'reporting', name: 'Reporting', enabled: true, category: 'Core' },

    // Audit Services
    { id: 'audit-planning', name: 'Audit Planning', enabled: true, category: 'Audit' },
    { id: 'substantive-testing', name: 'Substantive Testing', enabled: true, category: 'Audit' },
    { id: 'fraud-detection', name: 'Fraud Detection', enabled: true, category: 'Audit' },
    { id: 'financial-analysis', name: 'Financial Analysis', enabled: true, category: 'Audit' },
    { id: 'subsequent-events', name: 'Subsequent Events', enabled: true, category: 'Audit' },
    { id: 'related-party', name: 'Related Party Transactions', enabled: true, category: 'Audit' },
    { id: 'sampling', name: 'Audit Sampling', enabled: true, category: 'Audit' },
    { id: 'estimates-evaluation', name: 'Estimates Evaluation', enabled: true, category: 'Audit' },

    // Compliance & Reporting
    { id: 'disclosures', name: 'Disclosure Generation', enabled: true, category: 'Compliance' },
    { id: 'reg-ab-audit', name: 'Reg AB Audit', enabled: true, category: 'Compliance' },
    { id: 'advanced-report-generation', name: 'Advanced Report Generation', enabled: true, category: 'Compliance' },

    // Tax Services
    { id: 'tax-engine', name: 'Tax Engine', enabled: true, category: 'Tax' },
    { id: 'tax-forms', name: 'Tax Forms', enabled: true, category: 'Tax' },
    { id: 'tax-review', name: 'Tax Review', enabled: true, category: 'Tax' },
    { id: 'tax-ocr-intake', name: 'Tax OCR Intake', enabled: true, category: 'Tax' },

    // Data & Integration
    { id: 'ingestion', name: 'Data Ingestion', enabled: true, category: 'Data' },
    { id: 'normalize', name: 'Data Normalization', enabled: true, category: 'Data' },
    { id: 'connectors', name: 'Third-Party Connectors', enabled: true, category: 'Data' },
    { id: 'accounting-integrations', name: 'Accounting Integrations', enabled: true, category: 'Data' },

    // Quality & Security
    { id: 'qc', name: 'Quality Control', enabled: true, category: 'Quality' },
    { id: 'security', name: 'Security & Access Control', enabled: true, category: 'Security' },
    { id: 'data-anonymization', name: 'Data Anonymization', enabled: true, category: 'Security' },

    // Training & Support
    { id: 'training-data', name: 'Training Data Management', enabled: false, category: 'AI/ML' },
  ];

  useEffect(() => {
    loadFirms();
  }, []);

  const loadFirms = async () => {
    try {
      setLoading(true);
      const data = await tenantAPI.list();
      // Map enabled_services from backend to service toggles
      const firmsWithServices = data.map(firm => ({
        ...firm,
        services: availableServices.map(service => ({
          ...service,
          enabled: firm.enabled_services?.[service.id] ?? true  // Default to enabled if not specified
        })),
        userCount: 0  // TODO: Fetch actual user count from backend
      }));
      setFirms(firmsWithServices);
    } catch (error) {
      console.error('Error loading firms:', error);
      alert('Failed to load CPA firms. Please check your network connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFirm = async () => {
    try {
      await tenantAPI.create(newFirm);
      setShowCreateModal(false);
      setNewFirm({
        firm_name: '',
        legal_name: '',
        ein: '',
        primary_contact_name: '',
        primary_contact_email: '',
        primary_contact_phone: '',
        subscription_tier: 'professional',
      });
      loadFirms();
    } catch (error) {
      console.error('Error creating firm:', error);
    }
  };

  const handleToggleService = async (firmId: string, serviceId: string) => {
    // Optimistic UI update
    const updatedFirms = firms.map(firm => {
      if (firm.id === firmId) {
        return {
          ...firm,
          services: firm.services.map(service =>
            service.id === serviceId
              ? { ...service, enabled: !service.enabled }
              : service
          )
        };
      }
      return firm;
    });
    setFirms(updatedFirms);

    // Persist to backend
    try {
      const firm = updatedFirms.find(f => f.id === firmId);
      if (firm) {
        const enabledServices = firm.services.reduce((acc, service) => {
          acc[service.id] = service.enabled;
          return acc;
        }, {} as Record<string, boolean>);

        await tenantAPI.updateServices(firmId, enabledServices);
      }
    } catch (error) {
      console.error('Error updating services:', error);
      alert('Failed to update services. Changes will be reverted.');
      // Revert optimistic update on error
      loadFirms();
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      trial: 'bg-blue-100 text-blue-800',
      suspended: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.active;
  };

  const getTierBadge = (tier: string) => {
    const badges = {
      trial: 'bg-gray-100 text-gray-800',
      starter: 'bg-blue-100 text-blue-800',
      professional: 'bg-purple-100 text-purple-800',
      enterprise: 'bg-indigo-100 text-indigo-800',
      custom: 'bg-pink-100 text-pink-800',
    };
    return badges[tier as keyof typeof badges] || badges.professional;
  };

  const filteredFirms = firms.filter(firm =>
    firm.firm_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    firm.primary_contact_email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupedServices = availableServices.reduce((acc, service) => {
    if (!acc[service.category]) {
      acc[service.category] = [];
    }
    acc[service.category].push(service);
    return acc;
  }, {} as Record<string, ServiceToggle[]>);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">CPA Firm Management</h1>
          <p className="text-gray-600 mt-2">Manage CPA firms, subscriptions, and service access</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          Add CPA Firm
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search firms..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Firms Table */}
      <div className="bg-white rounded-lg shadow">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Firm
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Subscription
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Users
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  Loading firms...
                </td>
              </tr>
            ) : filteredFirms.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  No firms found
                </td>
              </tr>
            ) : (
              filteredFirms.map((firm) => (
                <tr key={firm.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <Building2 className="w-5 h-5 text-indigo-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{firm.firm_name}</div>
                        <div className="text-sm text-gray-500">{firm.legal_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{firm.primary_contact_name}</div>
                    <div className="text-sm text-gray-500">{firm.primary_contact_email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTierBadge(firm.subscription_tier)}`}>
                      {firm.subscription_tier.charAt(0).toUpperCase() + firm.subscription_tier.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(firm.status)}`}>
                      {firm.status.charAt(0).toUpperCase() + firm.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-sm text-gray-900">
                      <Users className="w-4 h-4 text-gray-400" />
                      {firm.usage_analytics?.active_users || 0} / {firm.limits?.max_users || '∞'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setSelectedFirm(firm);
                          setShowServicesModal(true);
                        }}
                        className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        title="Manage Services"
                      >
                        <Settings className="w-5 h-5" />
                      </button>
                      <button
                        className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                        title="Edit Firm"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Firm Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">Add New CPA Firm</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firm Name *
                </label>
                <input
                  type="text"
                  value={newFirm.firm_name}
                  onChange={(e) => setNewFirm({ ...newFirm, firm_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="ABC CPA Firm LLP"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Legal Name
                </label>
                <input
                  type="text"
                  value={newFirm.legal_name}
                  onChange={(e) => setNewFirm({ ...newFirm, legal_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="ABC CPA Firm Limited Liability Partnership"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  EIN
                </label>
                <input
                  type="text"
                  value={newFirm.ein}
                  onChange={(e) => setNewFirm({ ...newFirm, ein: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="12-3456789"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Contact Name *
                  </label>
                  <input
                    type="text"
                    value={newFirm.primary_contact_name}
                    onChange={(e) => setNewFirm({ ...newFirm, primary_contact_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="John Smith"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Contact Email *
                  </label>
                  <input
                    type="email"
                    value={newFirm.primary_contact_email}
                    onChange={(e) => setNewFirm({ ...newFirm, primary_contact_email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="john@abccpa.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={newFirm.primary_contact_phone}
                  onChange={(e) => setNewFirm({ ...newFirm, primary_contact_phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="(555) 123-4567"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subscription Tier
                </label>
                <select
                  value={newFirm.subscription_tier}
                  onChange={(e) => setNewFirm({ ...newFirm, subscription_tier: e.target.value as any })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="trial">Trial</option>
                  <option value="starter">Starter</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateFirm}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Create Firm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Services Management Modal */}
      {showServicesModal && selectedFirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold">Service Access Control</h2>
                <p className="text-gray-600 mt-1">{selectedFirm.firm_name}</p>
              </div>
              <button
                onClick={() => setShowServicesModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-6">
              {Object.entries(groupedServices).map(([category, services]) => (
                <div key={category} className="border rounded-lg p-4">
                  <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-indigo-600" />
                    {category} Services
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {services.map((service) => {
                      const firmService = selectedFirm.services.find(s => s.id === service.id);
                      const isEnabled = firmService?.enabled ?? service.enabled;

                      return (
                        <div
                          key={service.id}
                          className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                        >
                          <div className="flex items-center gap-3">
                            {isEnabled ? (
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            ) : (
                              <XCircle className="w-5 h-5 text-gray-300" />
                            )}
                            <span className="text-sm font-medium">{service.name}</span>
                          </div>
                          <button
                            onClick={() => handleToggleService(selectedFirm.id, service.id)}
                            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                              isEnabled
                                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                            }`}
                          >
                            {isEnabled ? 'Enabled' : 'Disabled'}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowServicesModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  // TODO: Save service toggles to backend
                  setShowServicesModal(false);
                }}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export { FirmManagement };
export default FirmManagement;
