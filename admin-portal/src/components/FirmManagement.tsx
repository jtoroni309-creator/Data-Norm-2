import React, { useState, useEffect } from 'react';
import {
  Building2,
  Plus,
  Search,
  Settings,
  Users,
  CheckCircle,
  XCircle,
  Edit,
  Shield,
  X,
  Loader2,
  AlertCircle,
  Eye,
  Mail,
} from 'lucide-react';
import { tenantAPI, userAPI, Tenant, CreateTenantRequest, UserListItem } from '../services/api';
import { SERVICE_CATALOG } from '../config';

interface ServiceToggle {
  id: string;
  name: string;
  enabled: boolean;
  category: string;
}

interface FirmWithServices extends Tenant {
  services: ServiceToggle[];
  userCount: number;
}

type SubscriptionTier = 'starter' | 'professional' | 'enterprise';

const FirmManagement: React.FC = () => {
  const [firms, setFirms] = useState<FirmWithServices[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showServicesModal, setShowServicesModal] = useState(false);
  const [showUsersModal, setShowUsersModal] = useState(false);
  const [firmUsers, setFirmUsers] = useState<UserListItem[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [selectedFirm, setSelectedFirm] = useState<FirmWithServices | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [newFirm, setNewFirm] = useState<CreateTenantRequest>({
    firm_name: '',
    legal_name: '',
    ein: '',
    primary_contact_name: '',
    primary_contact_email: '',
    primary_contact_phone: '',
    subscription_tier: 'professional',
  });

  // Available services that can be toggled per firm - imported from config
  const availableServices: ServiceToggle[] = SERVICE_CATALOG.map(service => ({
    id: service.id,
    name: service.name,
    enabled: service.defaultEnabled,
    category: service.category,
  }));

  useEffect(() => {
    loadFirms();
  }, []);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 10000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const loadFirms = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await tenantAPI.list();

      // Load user counts for each firm
      const firmsWithServices = await Promise.all(
        data.map(async (firm) => {
          let userCount = 0;
          try {
            const users = await userAPI.list({ tenantId: firm.id });
            userCount = users.length;
          } catch {
            userCount = 0;
          }

          return {
            ...firm,
            services: availableServices.map(service => ({
              ...service,
              enabled: firm.enabled_services?.[service.id] ?? service.enabled,
            })),
            userCount,
          };
        })
      );
      setFirms(firmsWithServices);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load CPA firms';
      setError(errorMessage);
      console.error('Error loading firms:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadFirmUsers = async (firm: FirmWithServices) => {
    setSelectedFirm(firm);
    setShowUsersModal(true);
    setLoadingUsers(true);
    try {
      const users = await tenantAPI.getUsers(firm.id);
      setFirmUsers(users);
    } catch (err) {
      console.error('Failed to load firm users:', err);
      setFirmUsers([]);
    } finally {
      setLoadingUsers(false);
    }
  };

  const validateForm = (): string | null => {
    if (!newFirm.firm_name.trim()) {
      return 'Firm name is required';
    }
    if (!newFirm.primary_contact_email.trim()) {
      return 'Primary contact email is required';
    }
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newFirm.primary_contact_email)) {
      return 'Please enter a valid email address';
    }
    return null;
  };

  const handleCreateFirm = async () => {
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);
      setError(null);
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
      setSuccessMessage('CPA Firm created successfully!');
      await loadFirms();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create firm';
      setError(errorMessage);
      console.error('Error creating firm:', err);
    } finally {
      setSaving(false);
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
          ),
        };
      }
      return firm;
    });
    setFirms(updatedFirms);

    // Also update selectedFirm if it's open
    if (selectedFirm && selectedFirm.id === firmId) {
      setSelectedFirm({
        ...selectedFirm,
        services: selectedFirm.services.map(service =>
          service.id === serviceId
            ? { ...service, enabled: !service.enabled }
            : service
        ),
      });
    }
  };

  const handleSaveServices = async () => {
    if (!selectedFirm) return;

    try {
      setSaving(true);
      setError(null);

      const enabledServices = selectedFirm.services.reduce((acc, service) => {
        acc[service.id] = service.enabled;
        return acc;
      }, {} as Record<string, boolean>);

      await tenantAPI.updateServices(selectedFirm.id, enabledServices);
      setSuccessMessage('Services updated successfully!');
      setShowServicesModal(false);
      await loadFirms();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update services';
      setError(errorMessage);
      console.error('Error updating services:', err);
    } finally {
      setSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      trial: 'bg-blue-100 text-blue-800',
      suspended: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || colors.active;
  };

  const getTierBadge = (tier: string) => {
    const badges: Record<string, string> = {
      trial: 'bg-gray-100 text-gray-800',
      starter: 'bg-blue-100 text-blue-800',
      professional: 'bg-purple-100 text-purple-800',
      enterprise: 'bg-indigo-100 text-indigo-800',
      custom: 'bg-pink-100 text-pink-800',
    };
    return badges[tier] || badges.professional;
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

      {/* Success Message */}
      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-800">{successMessage}</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
          <button onClick={() => setError(null)} className="ml-auto text-red-600 hover:text-red-800">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

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
                <td colSpan={6} className="px-6 py-12 text-center">
                  <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-2" />
                  <span className="text-gray-500">Loading firms...</span>
                </td>
              </tr>
            ) : filteredFirms.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  {searchTerm ? 'No firms match your search' : 'No CPA firms found. Click "Add CPA Firm" to create one.'}
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
                        <div className="text-sm text-gray-500">{firm.legal_name || '-'}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{firm.primary_contact_name || '-'}</div>
                    <div className="text-sm text-gray-500">{firm.primary_contact_email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTierBadge(firm.subscription_tier)}`}>
                      {firm.subscription_tier.charAt(0).toUpperCase() + firm.subscription_tier.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(firm.subscription_status)}`}>
                      {firm.subscription_status.charAt(0).toUpperCase() + firm.subscription_status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-sm text-gray-900">
                      <Users className="w-4 h-4 text-gray-400" />
                      {firm.userCount} / {firm.max_users === -1 ? '∞' : firm.max_users}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => loadFirmUsers(firm)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="View Users"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
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
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Add New CPA Firm</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firm Name <span className="text-red-500">*</span>
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
                    Primary Contact Name
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
                    Primary Contact Email <span className="text-red-500">*</span>
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
                  onChange={(e) => setNewFirm({ ...newFirm, subscription_tier: e.target.value as SubscriptionTier })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="starter">Starter</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                disabled={saving}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateFirm}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Firm'
                )}
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
                <X className="w-6 h-6" />
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
                disabled={saving}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveServices}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Users Modal */}
      {showUsersModal && selectedFirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold">Firm Users</h2>
                <p className="text-gray-600 mt-1">{selectedFirm.firm_name}</p>
              </div>
              <button
                onClick={() => {
                  setShowUsersModal(false);
                  setFirmUsers([]);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {loadingUsers ? (
              <div className="py-12 text-center">
                <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-2" />
                <span className="text-gray-500">Loading users...</span>
              </div>
            ) : firmUsers.length === 0 ? (
              <div className="py-12 text-center text-gray-500">
                <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No users found for this firm</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Login
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {firmUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center text-white font-semibold">
                              {user.firstName?.[0] || user.email[0].toUpperCase()}
                            </div>
                            <div>
                              <div className="font-medium text-gray-900">
                                {user.firstName && user.lastName
                                  ? `${user.firstName} ${user.lastName}`
                                  : user.email}
                              </div>
                              <div className="text-sm text-gray-500 flex items-center gap-1">
                                <Mail className="w-3 h-3" />
                                {user.email}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                            {user.role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                            user.isActive
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {user.isActive ? (
                              <CheckCircle className="w-3 h-3" />
                            ) : (
                              <XCircle className="w-3 h-3" />
                            )}
                            {user.isActive ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-600">
                          {user.lastLoginAt
                            ? new Date(user.lastLoginAt).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                              })
                            : 'Never'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="flex justify-end mt-6">
              <button
                onClick={() => {
                  setShowUsersModal(false);
                  setFirmUsers([]);
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Close
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
