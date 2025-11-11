import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Save,
  Bell,
  Shield,
  Palette,
  Globe,
  Key,
  Database,
  Mail,
  Smartphone,
  Lock,
} from 'lucide-react';
import { Card, CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';

interface SettingsSection {
  id: string;
  title: string;
  icon: React.ReactNode;
}

const sections: SettingsSection[] = [
  { id: 'general', title: 'General', icon: <Globe size={20} /> },
  { id: 'security', title: 'Security', icon: <Shield size={20} /> },
  { id: 'notifications', title: 'Notifications', icon: <Bell size={20} /> },
  { id: 'appearance', title: 'Appearance', icon: <Palette size={20} /> },
  { id: 'api', title: 'API Keys', icon: <Key size={20} /> },
  { id: 'database', title: 'Database', icon: <Database size={20} /> },
];

export const Settings: React.FC = () => {
  const [activeSection, setActiveSection] = useState('general');
  const [settings, setSettings] = useState({
    siteName: 'Data-Norm Admin',
    siteUrl: 'https://admin.datanorm.com',
    supportEmail: 'support@datanorm.com',
    timezone: 'UTC',
    language: 'en',
    twoFactorEnabled: true,
    emailNotifications: true,
    pushNotifications: false,
    theme: 'light',
  });

  const handleSave = () => {
    console.log('Saving settings:', settings);
    // Add toast notification here
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Site Information</h3>
        <div className="space-y-4">
          <Input
            label="Site Name"
            variant="outlined"
            value={settings.siteName}
            onChange={(e) => setSettings({ ...settings, siteName: e.target.value })}
          />
          <Input
            label="Site URL"
            variant="outlined"
            value={settings.siteUrl}
            onChange={(e) => setSettings({ ...settings, siteUrl: e.target.value })}
          />
          <Input
            label="Support Email"
            variant="outlined"
            type="email"
            value={settings.supportEmail}
            onChange={(e) => setSettings({ ...settings, supportEmail: e.target.value })}
            icon={<Mail size={18} />}
          />
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Localization</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Timezone</label>
            <select
              className="md-input-outlined"
              value={settings.timezone}
              onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
            >
              <option value="UTC">UTC</option>
              <option value="EST">Eastern Time</option>
              <option value="PST">Pacific Time</option>
              <option value="CST">Central Time</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Language</label>
            <select
              className="md-input-outlined"
              value={settings.language}
              onChange={(e) => setSettings({ ...settings, language: e.target.value })}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Authentication</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-surface-container-low">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                <Lock size={20} className="text-primary-600" />
              </div>
              <div>
                <p className="font-medium text-neutral-900">Two-Factor Authentication</p>
                <p className="text-sm text-neutral-600">Add an extra layer of security</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={settings.twoFactorEnabled}
                onChange={(e) => setSettings({ ...settings, twoFactorEnabled: e.target.checked })}
              />
              <div className="w-11 h-6 bg-neutral-300 peer-focus:ring-4 peer-focus:ring-primary-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="p-4 rounded-xl bg-warning-50 border border-warning-200">
            <div className="flex items-start gap-3">
              <Shield size={20} className="text-warning-600 mt-0.5" />
              <div>
                <p className="font-medium text-warning-900">Session Management</p>
                <p className="text-sm text-warning-700 mt-1">
                  You can view and manage all active sessions from your account
                </p>
                <Button variant="text" size="small" className="mt-3">
                  Manage Sessions
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Password</h3>
        <div className="space-y-4">
          <Input label="Current Password" variant="outlined" type="password" />
          <Input label="New Password" variant="outlined" type="password" />
          <Input label="Confirm New Password" variant="outlined" type="password" />
          <Button variant="outlined">Change Password</Button>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-surface-container-low">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                <Mail size={20} className="text-primary-600" />
              </div>
              <div>
                <p className="font-medium text-neutral-900">Email Notifications</p>
                <p className="text-sm text-neutral-600">Receive updates via email</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={settings.emailNotifications}
                onChange={(e) => setSettings({ ...settings, emailNotifications: e.target.checked })}
              />
              <div className="w-11 h-6 bg-neutral-300 peer-focus:ring-4 peer-focus:ring-primary-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl bg-surface-container-low">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary-100 flex items-center justify-center">
                <Smartphone size={20} className="text-secondary-600" />
              </div>
              <div>
                <p className="font-medium text-neutral-900">Push Notifications</p>
                <p className="text-sm text-neutral-600">Get push notifications on your device</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={settings.pushNotifications}
                onChange={(e) => setSettings({ ...settings, pushNotifications: e.target.checked })}
              />
              <div className="w-11 h-6 bg-neutral-300 peer-focus:ring-4 peer-focus:ring-primary-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'general':
        return renderGeneralSettings();
      case 'security':
        return renderSecuritySettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'appearance':
        return <div className="text-neutral-600">Appearance settings coming soon...</div>;
      case 'api':
        return <div className="text-neutral-600">API key management coming soon...</div>;
      case 'database':
        return <div className="text-neutral-600">Database settings coming soon...</div>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Settings</h1>
          <p className="text-neutral-600 mt-1">Manage your application settings and preferences</p>
        </div>
      </motion.div>

      {/* Settings Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card variant="elevated">
            <CardContent padding="small">
              <nav className="space-y-1">
                {sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`
                      w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all
                      ${
                        activeSection === section.id
                          ? 'bg-secondary-100 text-secondary-700 font-medium elevation-1'
                          : 'text-neutral-700 hover:bg-surface-container-high'
                      }
                    `}
                  >
                    {section.icon}
                    <span>{section.title}</span>
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3"
        >
          <Card variant="elevated">
            <CardHeader
              title={sections.find(s => s.id === activeSection)?.title || 'Settings'}
              subtitle="Configure your preferences"
            />
            <CardContent>
              {renderContent()}
            </CardContent>
            <CardFooter>
              <div className="flex items-center justify-between">
                <Button variant="outlined">Reset to Defaults</Button>
                <Button variant="filled" icon={<Save size={18} />} onClick={handleSave}>
                  Save Changes
                </Button>
              </div>
            </CardFooter>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};
