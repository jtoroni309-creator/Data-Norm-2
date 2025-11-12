import React, { useState } from 'react';
import { ExternalLink, Check, AlertCircle, RefreshCw, Settings } from 'lucide-react';
import { integrationService } from '../services/integration.service';

interface Integration {
  id: string;
  name: string;
  type: string;
  description: string;
  icon: string;
  connected: boolean;
  lastSync?: string;
  status?: 'active' | 'error' | 'syncing';
}

export const IntegrationsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: '1',
      name: 'QuickBooks Online',
      type: 'quickbooks',
      description: 'Sync your QuickBooks accounting data automatically',
      icon: '💼',
      connected: false,
    },
    {
      id: '2',
      name: 'Xero',
      type: 'xero',
      description: 'Connect to Xero for automated financial data import',
      icon: '📊',
      connected: false,
    },
    {
      id: '3',
      name: 'ADP Workforce',
      type: 'adp',
      description: 'Import payroll and HR data from ADP',
      icon: '👥',
      connected: false,
    },
    {
      id: '4',
      name: 'Gusto',
      type: 'gusto',
      description: 'Sync payroll and benefits data from Gusto',
      icon: '💰',
      connected: false,
    },
    {
      id: '5',
      name: 'Plaid (Banking)',
      type: 'plaid',
      description: 'Connect your bank accounts for transaction monitoring',
      icon: '🏦',
      connected: false,
    },
  ]);

  const [connecting, setConnecting] = useState<string | null>(null);

  const handleConnect = async (integration: Integration) => {
    setConnecting(integration.id);

    try {
      // Initiate OAuth flow
      const response = await integrationService.connect(integration.type);

      // In real implementation, this would redirect to OAuth provider
      window.open(response.authUrl, '_blank', 'width=600,height=700');

      // Simulate connection after OAuth
      setTimeout(() => {
        setIntegrations((prev) =>
          prev.map((int) =>
            int.id === integration.id
              ? {
                  ...int,
                  connected: true,
                  lastSync: new Date().toISOString(),
                  status: 'active' as const,
                }
              : int
          )
        );
        setConnecting(null);
      }, 2000);
    } catch (error) {
      console.error('Connection failed:', error);
      alert('Failed to connect integration');
      setConnecting(null);
    }
  };

  const handleDisconnect = async (integrationId: string, type: string) => {
    if (!confirm('Are you sure you want to disconnect this integration?')) return;

    try {
      await integrationService.disconnect(type);

      setIntegrations((prev) =>
        prev.map((int) =>
          int.id === integrationId
            ? { ...int, connected: false, lastSync: undefined, status: undefined }
            : int
        )
      );
    } catch (error) {
      console.error('Disconnect failed:', error);
      alert('Failed to disconnect integration');
    }
  };

  const handleSync = async (type: string) => {
    try {
      setIntegrations((prev) =>
        prev.map((int) =>
          int.type === type ? { ...int, status: 'syncing' as const } : int
        )
      );

      await integrationService.syncData(type);

      setIntegrations((prev) =>
        prev.map((int) =>
          int.type === type
            ? { ...int, lastSync: new Date().toISOString(), status: 'active' as const }
            : int
        )
      );
    } catch (error) {
      console.error('Sync failed:', error);
      setIntegrations((prev) =>
        prev.map((int) =>
          int.type === type ? { ...int, status: 'error' as const } : int
        )
      );
    }
  };

  const formatLastSync = (dateString?: string) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
    return `${Math.floor(diffMins / 1440)} days ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
          <p className="text-gray-600 mt-2">
            Connect your accounting, payroll, and banking systems for automated data sync
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900">Secure OAuth Integration</h3>
              <p className="text-sm text-blue-800 mt-1">
                All integrations use industry-standard OAuth 2.0 for secure authentication.
                We never store your passwords and can only access data you explicitly authorize.
              </p>
            </div>
          </div>
        </div>

        {/* Integrations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {integrations.map((integration) => (
            <div
              key={integration.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="text-4xl">{integration.icon}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {integration.name}
                    </h3>
                    <p className="text-sm text-gray-600">{integration.description}</p>
                  </div>
                </div>
              </div>

              {integration.connected ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <span className="inline-flex items-center gap-1 text-green-600 font-medium">
                      <Check className="w-4 h-4" />
                      Connected
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Last Sync:</span>
                    <span className="text-gray-900">
                      {formatLastSync(integration.lastSync)}
                    </span>
                  </div>

                  {integration.status === 'syncing' && (
                    <div className="text-sm text-blue-600 flex items-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Syncing data...
                    </div>
                  )}

                  {integration.status === 'error' && (
                    <div className="text-sm text-red-600 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      Sync failed - please reconnect
                    </div>
                  )}

                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={() => handleSync(integration.type)}
                      disabled={integration.status === 'syncing'}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Sync Now
                    </button>
                    <button
                      onClick={() => handleDisconnect(integration.id, integration.type)}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => handleConnect(integration)}
                  disabled={connecting === integration.id}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {connecting === integration.id ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <ExternalLink className="w-4 h-4" />
                      Connect
                    </>
                  )}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
