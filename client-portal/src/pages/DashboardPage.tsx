import React from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Calendar,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  Link,
  MessageCircle,
  Shield,
  Sparkles,
  UploadCloud,
  Users,
} from 'lucide-react';

const overallProgress = 72;
const circumference = 2 * Math.PI * 52;

const metricCards = [
  {
    label: 'Documents received',
    value: '48 / 62',
    meta: '4 approved today',
    icon: FileText,
    accent: 'bg-primary-50 text-primary-600',
  },
  {
    label: 'Data connections',
    value: '5 / 6',
    meta: 'Payroll refresh in 22m',
    icon: Link,
    accent: 'bg-success-50 text-success-600',
  },
  {
    label: 'Engagement progress',
    value: '72%',
    meta: 'On track',
    icon: Activity,
    accent: 'bg-accent-50 text-accent-600',
  },
  {
    label: 'Team responses',
    value: '3 pending',
    meta: 'Avg. SLA 2h',
    icon: Users,
    accent: 'bg-warning-50 text-warning-700',
  },
];

const workstreams = [
  { name: 'Financial statements', owner: 'Controller', progress: 82, status: 'On track' },
  { name: 'Internal controls', owner: 'Compliance', progress: 64, status: 'Monitoring' },
  { name: 'Tax & payroll', owner: 'Payroll', progress: 58, status: 'Action needed' },
  { name: 'Reg AB schedules', owner: 'Treasury', progress: 38, status: 'Behind' },
];

const actionItems = [
  {
    id: 1,
    title: 'Upload signed management representation letter',
    detail: 'Signed by CFO & Controller',
    due: 'Due tomorrow • 9:00 AM',
    priority: 'critical',
  },
  {
    id: 2,
    title: 'Approve Q4 bank confirmations',
    detail: '2 confirmations awaiting signature',
    due: 'Due in 3 days',
    priority: 'high',
  },
  {
    id: 3,
    title: 'Schedule walkthrough with engagement team',
    detail: 'Focus on revenue recognition',
    due: 'Due next week',
    priority: 'medium',
  },
];

const recentActivity = [
  {
    id: 1,
    title: 'Bank confirmations approved',
    detail: 'Primary, Sweep, Payroll accounts',
    time: 'Today • 09:12 AM',
    status: 'Completed',
  },
  {
    id: 2,
    title: 'QuickBooks sync finished',
    detail: 'Imported 1,248 transactions',
    time: 'Yesterday • 05:18 PM',
    status: 'Synced',
  },
  {
    id: 3,
    title: 'Control evidence uploaded',
    detail: 'Revenue cut-off walkthrough files',
    time: 'Yesterday • 02:44 PM',
    status: 'Reviewed',
  },
];

const documentStatus = [
  { label: 'Trial balance', status: 'Approved', tone: 'text-success-600 bg-success-50', icon: ClipboardCheck },
  { label: 'Bank recs', status: 'In review', tone: 'text-warning-700 bg-warning-50', icon: FileText },
  { label: 'Contracts', status: 'Pending upload', tone: 'text-primary-600 bg-primary-50', icon: UploadCloud },
];

const integrationStatus = [
  { label: 'QuickBooks Online', status: 'Connected', meta: 'Synced 12m ago', tone: 'text-success-600 bg-success-50' },
  { label: 'ADP Workforce', status: 'Syncing', meta: 'Payroll batch running', tone: 'text-warning-700 bg-warning-50' },
  { label: 'Plaid Banking', status: 'Secure hold', meta: 'Waiting on MFA', tone: 'text-accent-600 bg-accent-50' },
];

export const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#eef5ff,_#f8fafc_45%,_#f4f6fb)] px-6 py-10">
      <div className="mx-auto flex w-full max-w-[1440px] flex-col gap-8">
        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.1, 0.9, 0.2, 1] }}
          className="relative overflow-hidden rounded-[32px] border border-white/60 bg-gradient-to-br from-[#0f5ed5] via-[#2563eb] to-[#4f46e5] p-10 text-white shadow-[0_20px_60px_rgba(15,94,213,0.25)]"
        >
          <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 20% 20%, rgba(255,255,255,0.4), transparent 40%)' }} />
          <div className="relative grid gap-10 md:grid-cols-[1.6fr_1fr]">
            <div className="space-y-6">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-white/80">
                Anderson &amp; Co. • Financial Statement Audit
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full bg-white/15 px-4 py-1 text-sm font-medium backdrop-blur">
                  FY24 Audit Binder
                </span>
                <span className="rounded-full bg-white/10 px-4 py-1 text-sm font-medium backdrop-blur">
                  Due Jan 30, 2025
                </span>
                <span className="rounded-full bg-emerald-500/20 px-4 py-1 text-sm font-medium">
                  Status • On track
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-8">
                <div>
                  <p className="text-sm uppercase tracking-[0.2em] text-white/70">Overall progress</p>
                  <div className="mt-2 flex items-end gap-3">
                    <span className="text-6xl font-semibold leading-none">{overallProgress}%</span>
                    <span className="text-white/70">(+6% this week)</span>
                  </div>
                </div>
                <div className="relative h-32 w-32">
                  <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
                    <circle
                      cx="60"
                      cy="60"
                      r="52"
                      stroke="rgba(255,255,255,0.2)"
                      strokeWidth="12"
                      fill="none"
                    />
                    <circle
                      cx="60"
                      cy="60"
                      r="52"
                      stroke="url(#progressGradient)"
                      strokeWidth="12"
                      strokeLinecap="round"
                      fill="none"
                      strokeDasharray={circumference}
                      strokeDashoffset={circumference - (overallProgress / 100) * circumference}
                    />
                    <defs>
                      <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#a5b4fc" />
                        <stop offset="100%" stopColor="#22d3ee" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <p className="text-sm text-white/80">Phase</p>
                    <p className="text-xl font-semibold">Fieldwork</p>
                  </div>
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <button className="flex items-center justify-between rounded-2xl bg-white/10 px-6 py-4 text-left text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/20">
                  <div>
                    <p className="text-sm text-white/70">Next milestone</p>
                    <p className="text-lg font-semibold">Management letter draft</p>
                  </div>
                  <ArrowUpRight className="h-5 w-5" />
                </button>
                <button className="flex items-center justify-between rounded-2xl border border-white/30 px-6 py-4 text-left text-white/90 backdrop-blur transition hover:bg-white/10">
                  <div>
                    <p className="text-sm">Engagement lead</p>
                    <p className="text-lg font-semibold">Sloane Mitchell, CPA</p>
                  </div>
                  <MessageCircle className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="rounded-[28px] border border-white/30 bg-white/15 p-6 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5" />
                <div>
                  <p className="text-sm uppercase tracking-[0.25em] text-white/70">
                    Critical timeline
                  </p>
                  <p className="text-lg font-semibold">Next 7 days</p>
                </div>
              </div>
              <div className="mt-6 space-y-5">
                {[
                  { label: 'Walkthrough w/ audit senior', time: 'Tomorrow • 10:00 AM' },
                  { label: 'Revenue controls evidence', time: 'In 3 days • Upload window' },
                  { label: 'Fieldwork checkpoint', time: 'Jan 18 • Partner & CFO' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-4 rounded-2xl border border-white/20 px-4 py-3">
                    <Calendar className="h-10 w-10 text-white/70" />
                    <div>
                      <p className="text-sm text-white/70">{item.time}</p>
                      <p className="font-semibold">{item.label}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>

        {/* Metrics */}
        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {metricCards.map((card) => (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="rounded-3xl border border-white/60 bg-white/80 p-6 shadow-[0_4px_24px_rgba(15,23,42,0.05)] backdrop-blur"
            >
              <div className="flex items-center gap-3">
                <div className={`rounded-2xl px-3 py-2 text-sm font-semibold ${card.accent}`}>
                  <card.icon className="h-4 w-4" />
                </div>
                <p className="text-sm font-medium text-neutral-500">{card.label}</p>
              </div>
              <p className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900">
                {card.value}
              </p>
              <p className="mt-1 text-sm text-neutral-500">{card.meta}</p>
            </motion.div>
          ))}
        </section>

        {/* Workstreams & Activity */}
        <section className="grid gap-6 xl:grid-cols-[2fr_1.3fr]">
          <div className="rounded-3xl border border-white/80 bg-white/90 p-6 shadow-[0_15px_45px_rgba(15,23,42,0.08)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-500">Workstreams</p>
                <p className="text-2xl font-semibold text-neutral-900">Engagement readiness</p>
              </div>
              <span className="rounded-full bg-primary-50 px-4 py-1 text-sm font-semibold text-primary-600">
                Fieldwork phase
              </span>
            </div>
            <div className="mt-6 space-y-5">
              {workstreams.map((stream) => (
                <div
                  key={stream.name}
                  className="rounded-2xl border border-neutral-100 bg-neutral-50/60 p-5"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-neutral-900">{stream.name}</p>
                      <p className="text-sm text-neutral-500">Owner • {stream.owner}</p>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-neutral-600 shadow-sm">
                      {stream.status}
                    </span>
                  </div>
                  <div className="mt-4 h-2 rounded-full bg-neutral-200">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary-500 to-cyan-400 transition-all"
                      style={{ width: `${stream.progress}%` }}
                    />
                  </div>
                  <p className="mt-2 text-sm font-medium text-neutral-600">{stream.progress}% complete</p>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-white/80 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-neutral-900">Action center</h3>
                <span className="text-sm font-medium text-neutral-500">High-priority queue</span>
              </div>
              <div className="mt-4 space-y-4">
                {actionItems.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-2xl border border-neutral-100 bg-neutral-50/60 p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-neutral-900">{item.title}</p>
                        <p className="text-sm text-neutral-500">{item.detail}</p>
                      </div>
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          item.priority === 'critical'
                            ? 'bg-error-50 text-error-600'
                            : item.priority === 'high'
                            ? 'bg-warning-50 text-warning-700'
                            : 'bg-neutral-100 text-neutral-600'
                        }`}
                      >
                        {item.due}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-white/80 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-primary-500" />
                <div>
                  <p className="text-sm font-semibold text-primary-500">AI assistant</p>
                  <p className="text-xl font-semibold text-neutral-900">Insights & nudges</p>
                </div>
              </div>
              <ul className="mt-4 space-y-3 text-sm text-neutral-600">
                <li className="flex items-start gap-3 rounded-2xl bg-primary-50/80 p-4">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 text-primary-500" />
                  Revenue cut-off testing can start once contracts upload completes.
                </li>
                <li className="flex items-start gap-3 rounded-2xl bg-neutral-50 p-4">
                  <AlertTriangle className="mt-0.5 h-4 w-4 text-warning-700" />
                  2 payroll variance items exceed 15% threshold — flag for reviewer.
                </li>
                <li className="flex items-start gap-3 rounded-2xl bg-neutral-50 p-4">
                  <Shield className="mt-0.5 h-4 w-4 text-success-600" />
                  SOC 1 Type II report uploaded and ready for auditor download.
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Activity & Systems */}
        <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
          <div className="rounded-3xl border border-white/80 bg-white p-6 shadow-[0_25px_65px_rgba(15,23,42,0.06)]">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-semibold text-neutral-900">Engagement timeline</h3>
              <span className="text-sm text-neutral-500">Last 24 hours</span>
            </div>
            <div className="mt-6 space-y-6">
              {recentActivity.map((event) => (
                <div key={event.id} className="flex items-start gap-4">
                  <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-50">
                    <span className="text-sm font-semibold text-primary-600">{event.status}</span>
                    <span className="absolute -bottom-6 left-1/2 h-6 w-px -translate-x-1/2 bg-neutral-200" />
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-neutral-900">{event.title}</p>
                    <p className="text-sm text-neutral-500">{event.detail}</p>
                    <p className="text-sm text-neutral-400">{event.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-white/80 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-neutral-900">Document readiness</h3>
                <span className="text-sm text-neutral-500">Live sync</span>
              </div>
              <div className="mt-4 space-y-3">
                {documentStatus.map((doc) => (
                  <div
                    key={doc.label}
                    className="flex items-center justify-between rounded-2xl border border-neutral-100 px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <doc.icon className="h-5 w-5 text-neutral-500" />
                      <span className="font-medium text-neutral-800">{doc.label}</span>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${doc.tone}`}>
                      {doc.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-white/80 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-neutral-900">Integration health</h3>
                <span className="rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-600">
                  SOC 2 compliant
                </span>
              </div>
              <div className="mt-4 space-y-3">
                {integrationStatus.map((integration) => (
                  <div key={integration.label} className="rounded-2xl border border-neutral-100 px-4 py-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-neutral-900">{integration.label}</p>
                        <p className="text-sm text-neutral-500">{integration.meta}</p>
                      </div>
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${integration.tone}`}>
                        {integration.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Support */}
        <section className="rounded-[32px] border border-white/70 bg-white/90 p-8 shadow-[0_20px_65px_rgba(15,23,42,0.05)]">
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-neutral-500">
                Concierge support
              </p>
              <p className="mt-2 text-2xl font-semibold text-neutral-900">
                CPA engagement team on standby
              </p>
              <p className="mt-1 text-neutral-500">
                Dedicated audit channel with guaranteed 1-hour SLA during fieldwork
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <button className="rounded-2xl border border-neutral-200 px-5 py-3 text-sm font-semibold text-neutral-700 transition hover:bg-neutral-50">
                Message audit senior
              </button>
              <button className="rounded-2xl bg-neutral-900 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-neutral-900/20 transition hover:bg-neutral-800">
                Book checkpoint
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
