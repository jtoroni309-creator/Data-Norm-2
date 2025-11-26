/**
 * Firm Clients Page
 * Client management for CPA firms - add, view, and manage audit clients
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building2,
  Plus,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Phone,
  Mail,
  MapPin,
  Calendar,
  X,
  User,
  Briefcase,
  CheckCircle2,
  AlertCircle,
  Circle,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { clientService, Client, ClientCreate } from '../services/client.service';
import toast from 'react-hot-toast';

const FirmClients: React.FC = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMenu, setShowMenu] = useState<string | null>(null);
  const [editingClient, setEditingClient] = useState<Client | null>(null);

  // Create/Edit form state
  const [formData, setFormData] = useState<ClientCreate>({
    name: '',
    ein: '',
    industry: '',
    address: '',
    phone: '',
    email: '',
    primary_contact_name: '',
    primary_contact_email: '',
    primary_contact_phone: '',
    status: 'active',
    fiscal_year_end: '',
    notes: '',
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const data = await clientService.listClients();
      setClients(data);
    } catch (error: any) {
      console.error('Failed to load clients:', error);
      toast.error(error.response?.data?.detail || 'Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.name) {
      toast.error('Client name is required');
      return;
    }

    try {
      if (editingClient) {
        await clientService.updateClient(editingClient.id, formData);
        toast.success('Client updated successfully!');
      } else {
        await clientService.createClient(formData);
        toast.success('Client created successfully!');
      }

      setShowCreateModal(false);
      setEditingClient(null);
      resetForm();
      loadClients();
    } catch (error: any) {
      console.error('Failed to save client:', error);
      toast.error(error.response?.data?.detail || 'Failed to save client');
    }
  };

  const handleEdit = (client: Client) => {
    setEditingClient(client);
    setFormData({
      name: client.name,
      ein: client.ein || '',
      industry: client.industry || '',
      address: client.address || '',
      phone: client.phone || '',
      email: client.email || '',
      primary_contact_name: client.primary_contact_name || '',
      primary_contact_email: client.primary_contact_email || '',
      primary_contact_phone: client.primary_contact_phone || '',
      status: client.status,
      fiscal_year_end: client.fiscal_year_end || '',
      notes: client.notes || '',
    });
    setShowCreateModal(true);
    setShowMenu(null);
  };

  const handleDelete = async (client: Client) => {
    if (!confirm(`Are you sure you want to delete "${client.name}"?`)) {
      return;
    }

    try {
      await clientService.deleteClient(client.id);
      toast.success('Client deleted successfully');
      loadClients();
    } catch (error: any) {
      console.error('Failed to delete client:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete client');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      ein: '',
      industry: '',
      address: '',
      phone: '',
      email: '',
      primary_contact_name: '',
      primary_contact_email: '',
      primary_contact_phone: '',
      status: 'active',
      fiscal_year_end: '',
      notes: '',
    });
  };

  const filteredClients = clients.filter((client) => {
    const matchesSearch =
      client.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (client.email && client.email.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (client.primary_contact_name && client.primary_contact_name.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || client.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusConfig = (status: string) => {
    const configs = {
      active: { label: 'Active', color: 'green', icon: CheckCircle2 },
      inactive: { label: 'Inactive', color: 'gray', icon: Circle },
      prospect: { label: 'Prospect', color: 'yellow', icon: AlertCircle },
    };
    return configs[status as keyof typeof configs] || configs.active;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading clients...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div>
          <h1 className="text-display text-neutral-900 mb-1">Clients</h1>
          <p className="text-body text-neutral-600">
            Manage your audit clients and their information
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            resetForm();
            setEditingClient(null);
            setShowCreateModal(true);
          }}
          className="fluent-btn-primary"
        >
          <Plus className="w-4 h-4" />
          Add Client
        </motion.button>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Clients', value: clients.length, color: 'primary' },
          {
            label: 'Active',
            value: clients.filter((c) => c.status === 'active').length,
            color: 'success',
          },
          {
            label: 'Prospects',
            value: clients.filter((c) => c.status === 'prospect').length,
            color: 'accent',
          },
          { label: 'Inactive', value: clients.filter((c) => c.status === 'inactive').length, color: 'neutral' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="fluent-card p-4"
          >
            <p className="text-caption text-neutral-600 mb-1">{stat.label}</p>
            <p className={`text-title-large text-${stat.color}-600 font-semibold`}>{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <div className="fluent-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search clients..."
              className="fluent-input pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="prospect">Prospect</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Clients List */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredClients.map((client, index) => {
          const statusConfig = getStatusConfig(client.status);
          const StatusIcon = statusConfig.icon;

          return (
            <motion.div
              key={client.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.03 }}
              className="fluent-card-interactive p-5 relative"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-body-strong text-neutral-900 truncate mb-1">{client.name}</h3>
                  {client.industry && (
                    <div className="flex items-center gap-2 text-caption text-neutral-600">
                      <Briefcase className="w-3.5 h-3.5" />
                      <span className="truncate">{client.industry}</span>
                    </div>
                  )}
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowMenu(showMenu === client.id ? null : client.id)}
                    className="p-1.5 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
                  >
                    <MoreVertical className="w-4 h-4 text-neutral-600" />
                  </button>
                  <AnimatePresence>
                    {showMenu === client.id && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -5 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="absolute right-0 top-full mt-1 bg-white rounded-fluent shadow-fluent-8 py-1 z-10 min-w-[140px]"
                      >
                        <button
                          onClick={() => handleEdit(client)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50"
                        >
                          <Edit className="w-4 h-4" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(client)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-body text-error-600 hover:bg-error-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-3">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-${statusConfig.color}-50 text-${statusConfig.color}-700`}>
                  <StatusIcon className="w-3.5 h-3.5" />
                  {statusConfig.label}
                </span>
              </div>

              <div className="space-y-2 text-caption text-neutral-600">
                {client.primary_contact_name && (
                  <div className="flex items-center gap-2">
                    <User className="w-3.5 h-3.5" />
                    <span className="truncate">{client.primary_contact_name}</span>
                  </div>
                )}
                {client.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-3.5 h-3.5" />
                    <span className="truncate">{client.email}</span>
                  </div>
                )}
                {client.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-3.5 h-3.5" />
                    <span>{client.phone}</span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredClients.length === 0 && (
        <div className="fluent-card text-center py-16">
          <Building2 className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-title text-neutral-900 mb-2">No clients found</h3>
          <p className="text-body text-neutral-600 mb-6">Get started by adding your first client</p>
          <button onClick={() => setShowCreateModal(true)} className="fluent-btn-primary">
            <Plus className="w-4 h-4" />
            Add Client
          </button>
        </div>
      )}

      {/* Create/Edit Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => {
              setShowCreateModal(false);
              setEditingClient(null);
              resetForm();
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-3xl w-full shadow-fluent-16 max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-title-large text-neutral-900">
                  {editingClient ? 'Edit Client' : 'Add New Client'}
                </h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingClient(null);
                    resetForm();
                  }}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Basic Information */}
                <div>
                  <h3 className="text-body-strong text-neutral-900 mb-4">Basic Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-body-strong text-neutral-700 mb-2">Client Name *</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="fluent-input"
                        placeholder="ABC Corporation"
                      />
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">EIN</label>
                      <input
                        type="text"
                        value={formData.ein}
                        onChange={(e) => setFormData({ ...formData, ein: e.target.value })}
                        className="fluent-input"
                        placeholder="XX-XXXXXXX"
                      />
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Industry</label>
                      <input
                        type="text"
                        value={formData.industry}
                        onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                        className="fluent-input"
                        placeholder="Manufacturing, Healthcare, etc."
                      />
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Status</label>
                      <select
                        value={formData.status}
                        onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                        className="fluent-input"
                      >
                        <option value="active">Active</option>
                        <option value="prospect">Prospect</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Fiscal Year End</label>
                      <input
                        type="date"
                        value={formData.fiscal_year_end}
                        onChange={(e) => setFormData({ ...formData, fiscal_year_end: e.target.value })}
                        className="fluent-input"
                      />
                    </div>
                  </div>
                </div>

                {/* Contact Information */}
                <div>
                  <h3 className="text-body-strong text-neutral-900 mb-4">Contact Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-body-strong text-neutral-700 mb-2">Primary Contact Name</label>
                      <input
                        type="text"
                        value={formData.primary_contact_name}
                        onChange={(e) => setFormData({ ...formData, primary_contact_name: e.target.value })}
                        className="fluent-input"
                        placeholder="John Doe"
                      />
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Contact Email</label>
                      <input
                        type="email"
                        value={formData.primary_contact_email}
                        onChange={(e) => setFormData({ ...formData, primary_contact_email: e.target.value })}
                        className="fluent-input"
                        placeholder="contact@client.com"
                      />
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Contact Phone</label>
                      <input
                        type="tel"
                        value={formData.primary_contact_phone}
                        onChange={(e) => setFormData({ ...formData, primary_contact_phone: e.target.value })}
                        className="fluent-input"
                        placeholder="(555) 123-4567"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-body-strong text-neutral-700 mb-2">Client Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="fluent-input"
                        placeholder="info@client.com"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-body-strong text-neutral-700 mb-2">Address</label>
                      <textarea
                        value={formData.address}
                        onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                        className="fluent-input"
                        rows={2}
                        placeholder="Street address, city, state, ZIP"
                      />
                    </div>

                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Phone</label>
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="fluent-input"
                        placeholder="(555) 123-4567"
                      />
                    </div>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Notes</label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="fluent-input"
                    rows={3}
                    placeholder="Additional notes about this client..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingClient(null);
                    resetForm();
                  }}
                  className="fluent-btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button onClick={handleCreate} className="fluent-btn-primary flex-1">
                  {editingClient ? 'Update Client' : 'Add Client'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FirmClients;
