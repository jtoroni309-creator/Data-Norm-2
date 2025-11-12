import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  Lock,
  PlugZap,
  RefreshCw,
  Shield,
  Sparkles,
} from 'lucide-react';
import { integrationService } from '../services/integration.service';
import type { IntegrationType } from '@/types';

interface UIIntegration {
  id: string;
  name: string;
  type: IntegrationType;
  description: string;
  category: 'accounting' | 'payroll' | 'banking' | 'erp';
  badge: string;
  connected: boolean;
  lastSync?: string;
  status?: 'active' | 'error' | 'syncing';
}

const initialIntegrations: UIIntegration[] = [
  {
    id: 'qb',
    name: 'QuickBooks Online',
    type: 'quickbooks',
    description: 'Two-way sync for GL, subledgers, and class tracking',
    category: 'accounting',
    badge: 'Accounting',
    connected: true,
    lastSync: new Date(Date.now() - 12 * 60000).toISOString(),
    status: 'active',
  },
  {
    id: 'xero',
    name: 'Xero',
    type: 'xero',
    description: 'Multi-entity financial data ingestion with auto-tagging',
    category: 'accounting',
    badge: 'Multi-entity',
    connected: false,
  },
  {
    id: 'adp',
    name: 'ADP Workforce',
    type: 'adp',
    description: 'Payroll, tax, and benefits sync with SOC 1 evidence',
    category: 'payroll',
    badge: 'Payroll',
    connected: true,
    lastSync: new Date(Date.now() - 45 * 60000).toISOString(),
    status: 'syncing',
  },
  {
    id: 'gusto',
    name: 'Gusto',
    type: 'gusto',
    description: 'Automated payroll variance testing & approvals',
    category: 'payroll',
    badge: 'People Ops',
    connected: false,
  },
  {
    id: 'plaid',
    name: 'Plaid Banking',
    type: 'plaid',
    description: 'Real-time banking feeds, confirmation packages, and alerts',
    category: 'banking',
    badge: 'Treasury',
    connected: true,
    lastSync: new Date(Date.now() - 5 * 60000).toISOString(),
    status: 'active',
  },
  {
    id: 'netsuite',
    name: 'NetSuite ERP',
    type: 'netsuite',
    description: 'Consolidations, intercompany eliminations, and SOX support',
    category: 'erp',
    badge: 'ERP',
    connected: false,
  },
];

const categoryChips: Record<UIIntegration['category'], string> = {
  accounting: 'bg-primary-50 text-primary-600',
  payroll: 'bg-success-50 text-success-600',
  banking: 'bg-accent-50 text-accent-600',
  erp: 'bg-purple-50 text-purple-600',
};

const formatLastSync = (dateString?: string) => {
  if (!dateString) return 'Never';
  const diffMinutes = Math.floor((Date.now() - new Date(dateString).getTime()) / 60000);
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} minutes ago`;
  if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)} hours ago`;
  return `${Math.floor(diffMinutes / 1440)} days ago`;
};

export const IntegrationsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<UIIntegration[]>(initialIntegrations);
  const [connecting, setConnecting] = useState<string | null>(null);

  const handleConnect = async (integration: UIIntegration) => {
    setConnecting(integration.id);
    try {
      const response = await integrationService.connect(integration.type);
      window.open(response.authUrl, '_blank', 'width=600,height=700');

      setTimeout(() => {
        setIntegrations((prev) =>
          prev.map((item) =>
            item.id === integration.id
              ? { ...item, connected: true, status: 'active', lastSync: new Date().toISOString() }
              : item
          )
        );
        setConnecting(null);
      }, 1500);
    } catch (error) {
      console.error('Connection failed:', error);
      alert('Failed to connect integration');
      setConnecting(null);
    }
  };

  const handleDisconnect = async (integration: UIIntegration) => {
    if (!confirm('Disconnect this integration?')) return;
    try {
      await integrationService.disconnect(integration.id);
      setIntegrations((prev) =>
        prev.map((item) =>
          item.id === integration.id
            ? { ...item, connected: false, lastSync: undefined, status: undefined }
            : item
        )
      );
    } catch (error) {
      console.error('Disconnect failed:', error);
      alert('Failed to disconnect integration');
    }
  };

  const handleSync = async (integration: UIIntegration) => {
    try {
      setIntegrations((prev) =>
        prev.map((item) => (item.id === integration.id ? { ...item, status: 'syncing' } : item))
      );

      await integrationService.syncData(integration.id);

      setIntegrations((prev) =>
        prev.map((item) =>
          item.id === integration.id
            ? { ...item, status: 'active', lastSync: new Date().toISOString() }
            : item
        )
      );
    } catch (error) {
      console.error('Sync failed:', error);
      setIntegrations((prev) =>
        prev.map((item) => (item.id === integration.id ? { ...item, status: 'error' } : item))
      );
    }
  };

  const statusLabel = (status?: UIIntegration['status']) => {
    if (status === 'syncing') return 'Syncing';
    if (status === 'error') return 'Attention';
    if (status === 'active') return 'Connected';
    return 'Not connected';
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#eef5ff,_#f8fafc_45%,_#f4f6fb)] px-6 py-10">
      <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-8">
        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-[32px] border border-white/70 bg-gradient-to-br from-[#0f5ed5] via-[#2563eb] to-[#4f46e5] p-8 text-white shadow-[0_30px_80px_rgba(15,94,213,0.25)]"
        >
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-white/70">Trusted data fabric</p>
              <h1 className="mt-2 text-3xl font-semibold">Enterprise-grade integrations</h1>
              <p className="mt-1 text-white/80">
                OAuth 2.0 + mutual TLS • SOC 2 Type II • Continuous monitoring &amp; alerting
              </p>
            </div>
            <div className="rounded-2xl bg-white/10 px-4 py-3 text-center backdrop-blur">
              <p className="text-sm uppercase tracking-[0.3em] text-white/70">Uptime</p>
              <p className="text-2xl font-semibold">99.99%</p>
            </div>
          </div>
        </motion.section>

        <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
          {/* Integrations */}
          <div className="rounded-[32px] border border-white/80 bg-white/95 p-6 shadow-[0_25px_70px_rgba(15,23,42,0.06)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-500">Connected surfaces</p>
                <p className="text-2xl font-semibold text-neutral-900">Data pipelines</p>
              </div>
              <span className="rounded-full bg-neutral-100 px-4 py-1 text-xs font-semibold text-neutral-600">
                Real-time monitoring
              </span>
            </div>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {integrations.map((integration) => (
                <div
                  key={integration.id}
                  className="rounded-[24px] border border-neutral-100 bg-neutral-50/70 p-5 shadow-inner shadow-white/60"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-neutral-900">{integration.name}</p>
                      <p className="text-sm text-neutral-500">{integration.description}</p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${categoryChips[integration.category]}`}
                    >
                      {integration.badge}
                    </span>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        integration.connected
                          ? integration.status === 'error'
                            ? 'bg-error-50 text-error-600'
                            : 'bg-success-50 text-success-600'
                          : 'bg-neutral-100 text-neutral-600'
                      }`}
                    >
                      {statusLabel(integration.status)}
                    </span>
                    {integration.connected && (
                      <span className="text-xs text-neutral-500">Last sync • {formatLastSync(integration.lastSync)}</span>
                    )}
                  </div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    {integration.connected ? (
                      <>
                    <button
                      onClick={() => handleSync(integration)}
                      disabled={integration.status === 'syncing'}
                      className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-neutral-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-neutral-800 disabled:opacity-60"
                    >
                          <RefreshCw className={`h-4 w-4 ${integration.status === 'syncing' ? 'animate-spin' : ''}`} />
                          {integration.status === 'syncing' ? 'Syncing' : 'Sync now'}
                        </button>
                    <button
                      onClick={() => handleDisconnect(integration)}
                      className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-neutral-300 px-4 py-2 text-sm font-semibold text-neutral-700 transition hover:bg-neutral-100"
                    >
                          Disconnect
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => handleConnect(integration)}
                        disabled={connecting === integration.id}
                        className="flex w-full items-center justify-center gap-2 rounded-2xl border border-neutral-300 bg-white px-4 py-2 text-sm font-semibold text-neutral-900 transition hover:border-neutral-400 disabled:opacity-60"
                      >
                        {connecting === integration.id ? (
                          <>
                            <RefreshCw className="h-4 w-4 animate-spin" />
                            Authorizing...
                          </>
                        ) : (
                          <>
                            <ExternalLink className="h-4 w-4" />
                            Connect securely
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Security / Status */}
          <div className="space-y-6">
            <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-primary-500" />
                <div>
                  <p className="text-sm font-semibold text-primary-500">Security posture</p>
                  <p className="text-xl font-semibold text-neutral-900">Zero-trust integration bus</p>
                </div>
              </div>
              <ul className="mt-4 space-y-3 text-sm text-neutral-600">
                <li className="rounded-2xl bg-neutral-50 p-4">OAuth 2.0 + PKCE with scoped, revocable tokens.</li>
                <li className="rounded-2xl bg-neutral-50 p-4">Secrets stored in Azure Key Vault (HSM-backed).</li>
                <li className="rounded-2xl bg-neutral-50 p-4">Automatic anomaly detection and replay protection.</li>
              </ul>
            </div>

            <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center gap-3">
                <PlugZap className="h-5 w-5 text-accent-500" />
                <div>
                  <p className="text-sm font-semibold text-accent-500">Connection center</p>
                  <p className="text-xl font-semibold text-neutral-900">Observability</p>
                </div>
              </div>
              <div className="mt-4 space-y-3 text-sm text-neutral-600">
                <p>• 3 active webhooks • 152k events this week</p>
                <p>• 0 failed OAuth refresh tokens</p>
                <p>• 7 queued sync jobs • avg throughput 1.2s</p>
              </div>
            </div>

            <div className="rounded-[28px] border border-white/70 bg-neutral-900/90 p-6 text-white shadow-2xl">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-amber-300" />
                <div>
                  <p className="text-sm uppercase tracking-[0.3em] text-white/70">Concierge</p>
                  <p className="text-xl font-semibold">White-glove onboarding</p>
                </div>
              </div>
              <p className="mt-2 text-sm text-white/80">
                Let our solutions architects connect ERP, payroll, and custom data lakes without leaving
                the portal.
              </p>
              <button className="mt-5 w-full rounded-2xl border border-white/30 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
                Schedule integration session
              </button>
              <div className="mt-4 flex items-center gap-2 text-xs text-white/70">
                <Lock className="h-4 w-4" />
                NDA-backed access, SOC 1 / SOC 2 controls enforced
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
