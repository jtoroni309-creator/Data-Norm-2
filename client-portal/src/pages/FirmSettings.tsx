/**
 * CPA Firm Settings Page
 * Manage firm information, logo, branding, and preferences
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Upload,
  Save,
  X,
  Image as ImageIcon,
  Palette,
  Globe,
  Phone,
  MapPin,
  Clock,
  Calendar,
  Check
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { firmService } from '../services/firm.service';
import { Organization, OrganizationUpdate } from '../types';
import toast from 'react-hot-toast';

const FirmSettings: React.FC = () => {
  const navigate = useNavigate();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'branding' | 'preferences'>('general');

  // Form state
  const [formData, setFormData] = useState<OrganizationUpdate>({});
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [logoFile, setLogoFile] = useState<File | null>(null);

  useEffect(() => {
    loadOrganization();
  }, []);

  const loadOrganization = async () => {
    try {
      setLoading(true);
      const data = await firmService.getMyOrganization();
      setOrganization(data);
      setFormData({
        name: data.name,
        tax_id: data.tax_id,
        industry_code: data.industry_code,
        logo_url: data.logo_url,
        primary_color: data.primary_color,
        secondary_color: data.secondary_color,
        address: data.address,
        phone: data.phone,
        website: data.website,
        timezone: data.timezone,
        date_format: data.date_format
      });
      if (data.logo_url) {
        setLogoPreview(data.logo_url);
      }
    } catch (error) {
      console.error('Failed to load organization:', error);
      toast.error('Failed to load firm settings');
    } finally {
      setLoading(false);
    }
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Logo file size must be less than 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        toast.error('Please upload an image file');
        return;
      }
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async () => {
    if (!organization) return;

    try {
      setSaving(true);

      // Upload logo if changed
      if (logoFile) {
        const { url } = await firmService.uploadLogo(logoFile);
        formData.logo_url = url;
      }

      // Update organization
      const updated = await firmService.updateOrganization(organization.id, formData);
      setOrganization(updated);
      toast.success('Firm settings saved successfully!');
    } catch (error: any) {
      console.error('Failed to save settings:', error);
      toast.error(error.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: keyof OrganizationUpdate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const tabs = [
    { id: 'general', label: 'General Info', icon: Building2 },
    { id: 'branding', label: 'Branding', icon: Palette },
    { id: 'preferences', label: 'Preferences', icon: Clock }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/firm/dashboard')}
                className="text-sm text-gray-600 hover:text-gray-900 mb-2 flex items-center gap-1"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-3xl font-bold text-gradient">Firm Settings</h1>
              <p className="text-gray-600 mt-1">
                Manage your firm's profile, branding, and preferences
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-white rounded-lg p-1 shadow-sm">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-md font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-500 text-white shadow-md'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* General Info Tab */}
        {activeTab === 'general' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">General Information</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firm Name *
                </label>
                <input
                  type="text"
                  value={formData.name || ''}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="input-field"
                  placeholder="Enter firm name"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tax ID / EIN
                  </label>
                  <input
                    type="text"
                    value={formData.tax_id || ''}
                    onChange={(e) => handleInputChange('tax_id', e.target.value)}
                    className="input-field"
                    placeholder="XX-XXXXXXX"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Industry Code
                  </label>
                  <input
                    type="text"
                    value={formData.industry_code || ''}
                    onChange={(e) => handleInputChange('industry_code', e.target.value)}
                    className="input-field"
                    placeholder="NAICS Code"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Address
                </label>
                <textarea
                  value={formData.address || ''}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  className="input-field"
                  rows={3}
                  placeholder="Street address, city, state, ZIP"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Phone className="w-4 h-4 inline mr-1" />
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.phone || ''}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="input-field"
                    placeholder="(555) 123-4567"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Globe className="w-4 h-4 inline mr-1" />
                    Website
                  </label>
                  <input
                    type="url"
                    value={formData.website || ''}
                    onChange={(e) => handleInputChange('website', e.target.value)}
                    className="input-field"
                    placeholder="https://yourfirm.com"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Branding Tab */}
        {activeTab === 'branding' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">Branding & Logo</h2>
            <div className="space-y-8">
              {/* Logo Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  <ImageIcon className="w-4 h-4 inline mr-1" />
                  Firm Logo
                </label>
                <div className="flex items-start gap-6">
                  {/* Logo Preview */}
                  <div className="w-32 h-32 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center bg-gray-50 overflow-hidden">
                    {logoPreview ? (
                      <img
                        src={logoPreview}
                        alt="Logo preview"
                        className="w-full h-full object-contain"
                      />
                    ) : (
                      <ImageIcon className="w-12 h-12 text-gray-400" />
                    )}
                  </div>

                  {/* Upload Button */}
                  <div className="flex-1">
                    <label className="btn-primary cursor-pointer inline-flex items-center gap-2">
                      <Upload className="w-4 h-4" />
                      Upload Logo
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleLogoChange}
                        className="hidden"
                      />
                    </label>
                    {logoPreview && (
                      <button
                        onClick={() => {
                          setLogoPreview(null);
                          setLogoFile(null);
                          handleInputChange('logo_url', null);
                        }}
                        className="btn-secondary ml-2"
                      >
                        <X className="w-4 h-4" />
                        Remove
                      </button>
                    )}
                    <p className="text-sm text-gray-600 mt-2">
                      Recommended: Square image, at least 200x200px, PNG or JPG, max 5MB
                    </p>
                  </div>
                </div>
              </div>

              {/* Color Scheme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  <Palette className="w-4 h-4 inline mr-1" />
                  Color Scheme
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-2">
                      Primary Color
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="color"
                        value={formData.primary_color || '#2563eb'}
                        onChange={(e) => handleInputChange('primary_color', e.target.value)}
                        className="w-12 h-12 rounded-lg border-2 border-gray-300 cursor-pointer"
                      />
                      <input
                        type="text"
                        value={formData.primary_color || '#2563eb'}
                        onChange={(e) => handleInputChange('primary_color', e.target.value)}
                        className="input-field flex-1"
                        placeholder="#2563eb"
                        pattern="^#[0-9A-Fa-f]{6}$"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-2">
                      Secondary Color
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="color"
                        value={formData.secondary_color || '#7c3aed'}
                        onChange={(e) => handleInputChange('secondary_color', e.target.value)}
                        className="w-12 h-12 rounded-lg border-2 border-gray-300 cursor-pointer"
                      />
                      <input
                        type="text"
                        value={formData.secondary_color || '#7c3aed'}
                        onChange={(e) => handleInputChange('secondary_color', e.target.value)}
                        className="input-field flex-1"
                        placeholder="#7c3aed"
                        pattern="^#[0-9A-Fa-f]{6}$"
                      />
                    </div>
                  </div>
                </div>

                {/* Color Preview */}
                <div className="mt-6 p-6 rounded-lg border-2 border-gray-200 bg-gray-50">
                  <p className="text-sm font-medium text-gray-700 mb-3">Preview</p>
                  <div className="flex gap-4">
                    <div
                      className="flex-1 h-20 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
                      style={{ backgroundColor: formData.primary_color || '#2563eb' }}
                    >
                      Primary
                    </div>
                    <div
                      className="flex-1 h-20 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
                      style={{ backgroundColor: formData.secondary_color || '#7c3aed' }}
                    >
                      Secondary
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">Preferences</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Timezone
                </label>
                <select
                  value={formData.timezone || 'America/New_York'}
                  onChange={(e) => handleInputChange('timezone', e.target.value)}
                  className="input-field"
                >
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  <option value="America/Anchorage">Alaska Time (AKT)</option>
                  <option value="Pacific/Honolulu">Hawaii Time (HT)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Date Format
                </label>
                <select
                  value={formData.date_format || 'MM/DD/YYYY'}
                  onChange={(e) => handleInputChange('date_format', e.target.value)}
                  className="input-field"
                >
                  <option value="MM/DD/YYYY">MM/DD/YYYY (e.g., 12/31/2024)</option>
                  <option value="DD/MM/YYYY">DD/MM/YYYY (e.g., 31/12/2024)</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD (e.g., 2024-12-31)</option>
                </select>
              </div>
            </div>
          </motion.div>
        )}

        {/* Save Button */}
        <div className="flex items-center justify-end gap-3 mt-6">
          <button
            onClick={() => navigate('/firm/dashboard')}
            className="btn-secondary"
            disabled={saving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary flex items-center gap-2"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FirmSettings;
