import React, { useState, useEffect } from 'react';
import {
  Building2,
  Users,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle,
  Clock,
  ChevronRight,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  RefreshCw,
  TrendingUp,
  DollarSign,
  Globe,
  Shield,
  BarChart3,
  PieChart,
  Layers,
  Network,
  Target,
  Briefcase,
  Mail,
  Phone,
  Calendar,
  Filter,
  Search,
  MoreVertical,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Eye,
  Link,
  Unlink,
  Settings,
  FileText,
  Calculator,
  Flag,
  Sparkles,
} from 'lucide-react';

interface ComponentEntity {
  id: string;
  entity_name: string;
  entity_code: string;
  legal_name: string;
  jurisdiction: string;
  ownership_percentage: number;
  consolidation_method: string;
  significance: string;
  total_assets: number;
  total_revenue: number;
  net_income: number;
  percentage_of_group_assets: number;
  percentage_of_group_revenue: number;
  audit_approach: string;
  component_materiality: number;
  risk_level: string;
  status: string;
  completion_percentage: number;
}

interface ComponentAuditor {
  id: string;
  component_entity_id: string;
  auditor_type: string;
  firm_name: string;
  lead_partner_name: string;
  lead_partner_email: string;
  independence_confirmed: boolean;
  deliverables_received: boolean;
  status: string;
}

interface EliminationEntry {
  id: string;
  entry_number: string;
  entry_type: string;
  description: string;
  debit_amount: number;
  credit_amount: number;
  status: string;
}

interface GroupRisk {
  id: string;
  risk_category: string;
  risk_title: string;
  inherent_risk: string;
  control_risk: string;
  combined_risk: string;
  pervasive: boolean;
  status: string;
}

interface GroupEngagement {
  id: string;
  group_name: string;
  ultimate_parent_name: string;
  reporting_framework: string;
  functional_currency: string;
  group_materiality: number;
  group_performance_materiality: number;
  component_materiality: number;
  clearly_trivial_threshold: number;
  status: string;
  component_count: number;
  total_assets: number;
  total_revenue: number;
}

const GroupAuditManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'components' | 'auditors' | 'eliminations' | 'risks' | 'consolidation'>('overview');
  const [showAddComponentModal, setShowAddComponentModal] = useState(false);
  const [showAddAuditorModal, setShowAddAuditorModal] = useState(false);
  const [showAddEliminationModal, setShowAddEliminationModal] = useState(false);
  const [showMaterialityModal, setShowMaterialityModal] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState<ComponentEntity | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Demo data
  const [groupEngagement, setGroupEngagement] = useState<GroupEngagement>({
    id: 'group-001',
    group_name: 'Acme Corporation Group',
    ultimate_parent_name: 'Acme Corporation Holdings, Inc.',
    reporting_framework: 'US GAAP',
    functional_currency: 'USD',
    group_materiality: 5000000,
    group_performance_materiality: 3750000,
    component_materiality: 1875000,
    clearly_trivial_threshold: 150000,
    status: 'in_progress',
    component_count: 8,
    total_assets: 2500000000,
    total_revenue: 1800000000,
  });

  const [components, setComponents] = useState<ComponentEntity[]>([
    {
      id: 'comp-001',
      entity_name: 'Acme US Operations',
      entity_code: 'ACME-US',
      legal_name: 'Acme US Operations, Inc.',
      jurisdiction: 'Delaware, USA',
      ownership_percentage: 100,
      consolidation_method: 'full_consolidation',
      significance: 'significant',
      total_assets: 1200000000,
      total_revenue: 900000000,
      net_income: 85000000,
      percentage_of_group_assets: 4800,
      percentage_of_group_revenue: 5000,
      audit_approach: 'full_scope',
      component_materiality: 2500000,
      risk_level: 'moderate',
      status: 'in_progress',
      completion_percentage: 65,
    },
    {
      id: 'comp-002',
      entity_name: 'Acme Europe GmbH',
      entity_code: 'ACME-EU',
      legal_name: 'Acme Europe GmbH',
      jurisdiction: 'Germany',
      ownership_percentage: 100,
      consolidation_method: 'full_consolidation',
      significance: 'significant',
      total_assets: 650000000,
      total_revenue: 480000000,
      net_income: 42000000,
      percentage_of_group_assets: 2600,
      percentage_of_group_revenue: 2667,
      audit_approach: 'full_scope',
      component_materiality: 1500000,
      risk_level: 'moderate',
      status: 'in_progress',
      completion_percentage: 45,
    },
    {
      id: 'comp-003',
      entity_name: 'Acme Asia Pacific',
      entity_code: 'ACME-APAC',
      legal_name: 'Acme Asia Pacific Pte. Ltd.',
      jurisdiction: 'Singapore',
      ownership_percentage: 100,
      consolidation_method: 'full_consolidation',
      significance: 'material',
      total_assets: 380000000,
      total_revenue: 280000000,
      net_income: 28000000,
      percentage_of_group_assets: 1520,
      percentage_of_group_revenue: 1556,
      audit_approach: 'specific_scope',
      component_materiality: 1000000,
      risk_level: 'high',
      status: 'pending',
      completion_percentage: 15,
    },
    {
      id: 'comp-004',
      entity_name: 'Acme Canada',
      entity_code: 'ACME-CA',
      legal_name: 'Acme Canada Ltd.',
      jurisdiction: 'Ontario, Canada',
      ownership_percentage: 100,
      consolidation_method: 'full_consolidation',
      significance: 'not_significant',
      total_assets: 120000000,
      total_revenue: 95000000,
      net_income: 8500000,
      percentage_of_group_assets: 480,
      percentage_of_group_revenue: 528,
      audit_approach: 'analytical_review',
      component_materiality: 500000,
      risk_level: 'low',
      status: 'completed',
      completion_percentage: 100,
    },
    {
      id: 'comp-005',
      entity_name: 'Acme UK Limited',
      entity_code: 'ACME-UK',
      legal_name: 'Acme UK Limited',
      jurisdiction: 'United Kingdom',
      ownership_percentage: 80,
      consolidation_method: 'full_consolidation',
      significance: 'material',
      total_assets: 150000000,
      total_revenue: 45000000,
      net_income: 12000000,
      percentage_of_group_assets: 600,
      percentage_of_group_revenue: 250,
      audit_approach: 'specific_scope',
      component_materiality: 600000,
      risk_level: 'moderate',
      status: 'in_progress',
      completion_percentage: 35,
    },
  ]);

  const [auditors, setAuditors] = useState<ComponentAuditor[]>([
    {
      id: 'aud-001',
      component_entity_id: 'comp-001',
      auditor_type: 'group_team',
      firm_name: 'Our Firm',
      lead_partner_name: 'John Smith',
      lead_partner_email: 'john.smith@ourfirm.com',
      independence_confirmed: true,
      deliverables_received: false,
      status: 'engaged',
    },
    {
      id: 'aud-002',
      component_entity_id: 'comp-002',
      auditor_type: 'network_firm',
      firm_name: 'Partner Firm Germany',
      lead_partner_name: 'Hans Mueller',
      lead_partner_email: 'h.mueller@partnerfirm.de',
      independence_confirmed: true,
      deliverables_received: false,
      status: 'engaged',
    },
    {
      id: 'aud-003',
      component_entity_id: 'comp-003',
      auditor_type: 'non_network_firm',
      firm_name: 'Singapore Audit Partners',
      lead_partner_name: 'Wei Lin',
      lead_partner_email: 'wei.lin@sgaudit.com',
      independence_confirmed: false,
      deliverables_received: false,
      status: 'pending',
    },
  ]);

  const [eliminations, setEliminations] = useState<EliminationEntry[]>([
    {
      id: 'elim-001',
      entry_number: 'ELIM-001',
      entry_type: 'intercompany_revenue',
      description: 'Eliminate intercompany sales between US and Europe',
      debit_amount: 15000000,
      credit_amount: 15000000,
      status: 'reviewed',
    },
    {
      id: 'elim-002',
      entry_number: 'ELIM-002',
      entry_type: 'intercompany_payable_receivable',
      description: 'Eliminate intercompany receivables/payables',
      debit_amount: 8500000,
      credit_amount: 8500000,
      status: 'prepared',
    },
    {
      id: 'elim-003',
      entry_number: 'ELIM-003',
      entry_type: 'intercompany_investment',
      description: 'Eliminate investment in subsidiaries',
      debit_amount: 450000000,
      credit_amount: 450000000,
      status: 'draft',
    },
    {
      id: 'elim-004',
      entry_number: 'ELIM-004',
      entry_type: 'unrealized_profit',
      description: 'Eliminate unrealized profit on intercompany inventory',
      debit_amount: 2500000,
      credit_amount: 2500000,
      status: 'reviewed',
    },
  ]);

  const [risks, setRisks] = useState<GroupRisk[]>([
    {
      id: 'risk-001',
      risk_category: 'fraud',
      risk_title: 'Management Override of Controls',
      inherent_risk: 'moderate',
      control_risk: 'moderate',
      combined_risk: 'moderate',
      pervasive: true,
      status: 'assessed',
    },
    {
      id: 'risk-002',
      risk_category: 'going_concern',
      risk_title: 'Liquidity Concerns in APAC Region',
      inherent_risk: 'high',
      control_risk: 'moderate',
      combined_risk: 'high',
      pervasive: false,
      status: 'identified',
    },
    {
      id: 'risk-003',
      risk_category: 'related_party',
      risk_title: 'Intercompany Pricing Arrangements',
      inherent_risk: 'moderate',
      control_risk: 'low',
      combined_risk: 'moderate',
      pervasive: true,
      status: 'responded',
    },
    {
      id: 'risk-004',
      risk_category: 'revenue_recognition',
      risk_title: 'Revenue Cut-off at Period End',
      inherent_risk: 'high',
      control_risk: 'moderate',
      combined_risk: 'high',
      pervasive: true,
      status: 'assessed',
    },
  ]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (basisPoints: number) => {
    return `${(basisPoints / 100).toFixed(1)}%`;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      reviewed: 'bg-green-100 text-green-800',
      prepared: 'bg-blue-100 text-blue-800',
      draft: 'bg-gray-100 text-gray-800',
      engaged: 'bg-blue-100 text-blue-800',
      assessed: 'bg-blue-100 text-blue-800',
      identified: 'bg-yellow-100 text-yellow-800',
      responded: 'bg-green-100 text-green-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getRiskColor = (level: string) => {
    const colors: Record<string, string> = {
      low: 'bg-green-100 text-green-800',
      moderate: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      very_high: 'bg-red-100 text-red-800',
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  const getSignificanceColor = (significance: string) => {
    const colors: Record<string, string> = {
      significant: 'bg-purple-100 text-purple-800',
      material: 'bg-blue-100 text-blue-800',
      not_significant: 'bg-gray-100 text-gray-800',
      immaterial: 'bg-gray-100 text-gray-600',
    };
    return colors[significance] || 'bg-gray-100 text-gray-800';
  };

  const renderOverviewTab = () => {
    const significantCount = components.filter(c => c.significance === 'significant').length;
    const completedCount = components.filter(c => c.status === 'completed').length;
    const highRiskCount = risks.filter(r => r.combined_risk === 'high' || r.combined_risk === 'very_high').length;
    const pendingDeliverables = auditors.filter(a => !a.deliverables_received).length;
    const totalEliminations = eliminations.reduce((sum, e) => sum + e.debit_amount, 0);

    return (
      <div className="space-y-6">
        {/* Header Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-5 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium">Group Materiality</p>
                <p className="text-2xl font-bold mt-1">{formatCurrency(groupEngagement.group_materiality)}</p>
                <p className="text-blue-200 text-xs mt-1">PM: {formatCurrency(groupEngagement.group_performance_materiality)}</p>
              </div>
              <div className="bg-white/20 rounded-lg p-3">
                <DollarSign className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm font-medium">Components</p>
                <p className="text-2xl font-bold mt-1">{components.length}</p>
                <p className="text-purple-200 text-xs mt-1">{significantCount} significant</p>
              </div>
              <div className="bg-white/20 rounded-lg p-3">
                <Building2 className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-5 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm font-medium">Total Assets</p>
                <p className="text-2xl font-bold mt-1">{formatCurrency(groupEngagement.total_assets)}</p>
                <p className="text-green-200 text-xs mt-1">Revenue: {formatCurrency(groupEngagement.total_revenue)}</p>
              </div>
              <div className="bg-white/20 rounded-lg p-3">
                <TrendingUp className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-5 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm font-medium">Group Risks</p>
                <p className="text-2xl font-bold mt-1">{risks.length}</p>
                <p className="text-orange-200 text-xs mt-1">{highRiskCount} high/very high</p>
              </div>
              <div className="bg-white/20 rounded-lg p-3">
                <AlertTriangle className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>

        {/* Progress and Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Component Progress */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Building2 className="w-5 h-5 text-blue-500" />
              Component Progress
            </h3>
            <div className="space-y-3">
              {components.slice(0, 5).map(component => (
                <div key={component.id} className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{component.entity_code}</span>
                      <span className="text-xs text-gray-500">{component.completion_percentage}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          component.completion_percentage === 100 ? 'bg-green-500' :
                          component.completion_percentage > 50 ? 'bg-blue-500' : 'bg-yellow-500'
                        }`}
                        style={{ width: `${component.completion_percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => setActiveTab('components')}
              className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
            >
              View all components <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Auditor Status */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-purple-500" />
              Component Auditors
            </h3>
            <div className="space-y-3">
              {auditors.map(auditor => {
                const component = components.find(c => c.id === auditor.component_entity_id);
                return (
                  <div key={auditor.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{auditor.firm_name}</p>
                      <p className="text-xs text-gray-500">{component?.entity_code || 'Unknown'}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {auditor.independence_confirmed ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <Clock className="w-4 h-4 text-yellow-500" />
                      )}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(auditor.status)}`}>
                        {auditor.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            <button
              onClick={() => setActiveTab('auditors')}
              className="mt-4 text-sm text-purple-600 hover:text-purple-700 font-medium flex items-center gap-1"
            >
              Manage auditors <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Risk Summary */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              Consolidated Risks
            </h3>
            <div className="space-y-3">
              {risks.slice(0, 4).map(risk => (
                <div key={risk.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{risk.risk_title}</p>
                    <p className="text-xs text-gray-500">{risk.risk_category.replace('_', ' ')}</p>
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    {risk.pervasive && (
                      <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">
                        Pervasive
                      </span>
                    )}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(risk.combined_risk)}`}>
                      {risk.combined_risk}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => setActiveTab('risks')}
              className="mt-4 text-sm text-orange-600 hover:text-orange-700 font-medium flex items-center gap-1"
            >
              View all risks <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Eliminations Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-blue-500" />
              Elimination Entries
            </h3>
            <span className="text-sm text-gray-500">
              Total: {formatCurrency(totalEliminations)}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {eliminations.map(entry => (
              <div key={entry.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-gray-500">{entry.entry_number}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(entry.status)}`}>
                    {entry.status}
                  </span>
                </div>
                <p className="text-sm font-medium text-gray-900 mb-1 line-clamp-2">{entry.description}</p>
                <p className="text-lg font-semibold text-gray-700">{formatCurrency(entry.debit_amount)}</p>
              </div>
            ))}
          </div>
          <button
            onClick={() => setActiveTab('eliminations')}
            className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
          >
            Manage eliminations <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  };

  const renderComponentsTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search components..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
            />
          </div>
          <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Filter className="w-4 h-4" />
            Filter
          </button>
        </div>
        <button
          onClick={() => setShowAddComponentModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Component
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Entity</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Jurisdiction</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Ownership</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Significance</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Assets</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">% of Group</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Audit Approach</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Materiality</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Risk</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Progress</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {components
                .filter(c => c.entity_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            c.entity_code.toLowerCase().includes(searchTerm.toLowerCase()))
                .map(component => (
                <tr key={component.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4">
                    <div>
                      <p className="font-medium text-gray-900">{component.entity_name}</p>
                      <p className="text-xs text-gray-500 font-mono">{component.entity_code}</p>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-700">{component.jurisdiction}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className="text-sm font-medium text-gray-900">{component.ownership_percentage}%</span>
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSignificanceColor(component.significance)}`}>
                      {component.significance.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className="text-sm font-medium text-gray-900">{formatCurrency(component.total_assets)}</span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className="text-sm text-gray-600">{formatPercentage(component.percentage_of_group_assets)}</span>
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                      {component.audit_approach.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className="text-sm font-medium text-gray-900">{formatCurrency(component.component_materiality)}</span>
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(component.risk_level)}`}>
                      {component.risk_level}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden w-20">
                        <div
                          className={`h-full rounded-full ${
                            component.completion_percentage === 100 ? 'bg-green-500' :
                            component.completion_percentage > 50 ? 'bg-blue-500' : 'bg-yellow-500'
                          }`}
                          style={{ width: `${component.completion_percentage}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8">{component.completion_percentage}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                        <Link className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Materiality Allocation Card */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-xl">
              <Calculator className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Materiality Allocation</h3>
              <p className="text-sm text-gray-600">Allocate group materiality to component entities based on risk and size</p>
            </div>
          </div>
          <button
            onClick={() => setShowMaterialityModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Allocate Materiality
          </button>
        </div>
      </div>
    </div>
  );

  const renderAuditorsTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Component Auditor Management</h2>
        <button
          onClick={() => setShowAddAuditorModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Assign Auditor
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {auditors.map(auditor => {
          const component = components.find(c => c.id === auditor.component_entity_id);
          return (
            <div key={auditor.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    auditor.auditor_type === 'group_team' ? 'bg-blue-100' :
                    auditor.auditor_type === 'network_firm' ? 'bg-purple-100' : 'bg-gray-100'
                  }`}>
                    <Users className={`w-5 h-5 ${
                      auditor.auditor_type === 'group_team' ? 'text-blue-600' :
                      auditor.auditor_type === 'network_firm' ? 'text-purple-600' : 'text-gray-600'
                    }`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{auditor.firm_name}</h3>
                    <p className="text-sm text-gray-500">{auditor.auditor_type.replace('_', ' ')}</p>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(auditor.status)}`}>
                  {auditor.status}
                </span>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <Building2 className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">Component:</span>
                  <span className="font-medium text-gray-900">{component?.entity_name || 'Unknown'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Briefcase className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">Lead Partner:</span>
                  <span className="font-medium text-gray-900">{auditor.lead_partner_name}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">Email:</span>
                  <a href={`mailto:${auditor.lead_partner_email}`} className="text-blue-600 hover:text-blue-700">
                    {auditor.lead_partner_email}
                  </a>
                </div>
              </div>

              <div className="flex items-center gap-4 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-2">
                  {auditor.independence_confirmed ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Clock className="w-4 h-4 text-yellow-500" />
                  )}
                  <span className="text-sm text-gray-600">
                    Independence {auditor.independence_confirmed ? 'Confirmed' : 'Pending'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {auditor.deliverables_received ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Clock className="w-4 h-4 text-yellow-500" />
                  )}
                  <span className="text-sm text-gray-600">
                    Deliverables {auditor.deliverables_received ? 'Received' : 'Pending'}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 mt-4">
                <button className="flex-1 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                  Send Instructions
                </button>
                <button className="flex-1 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                  View Details
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderEliminationsTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Elimination Entries</h2>
          <p className="text-sm text-gray-500">Intercompany eliminations for consolidated financial statements</p>
        </div>
        <button
          onClick={() => setShowAddEliminationModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Elimination
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Entry #</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Type</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Description</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Debit</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Credit</th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {eliminations.map(entry => (
              <tr key={entry.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-4">
                  <span className="font-mono text-sm text-gray-900">{entry.entry_number}</span>
                </td>
                <td className="px-4 py-4">
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                    {entry.entry_type.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-4">
                  <span className="text-sm text-gray-700">{entry.description}</span>
                </td>
                <td className="px-4 py-4 text-right">
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(entry.debit_amount)}</span>
                </td>
                <td className="px-4 py-4 text-right">
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(entry.credit_amount)}</span>
                </td>
                <td className="px-4 py-4 text-center">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(entry.status)}`}>
                    {entry.status}
                  </span>
                </td>
                <td className="px-4 py-4 text-right">
                  <div className="flex items-center justify-end gap-1">
                    <button className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-gray-50 border-t border-gray-200">
            <tr>
              <td colSpan={3} className="px-4 py-3 text-sm font-semibold text-gray-900">Total Eliminations</td>
              <td className="px-4 py-3 text-right text-sm font-bold text-gray-900">
                {formatCurrency(eliminations.reduce((sum, e) => sum + e.debit_amount, 0))}
              </td>
              <td className="px-4 py-3 text-right text-sm font-bold text-gray-900">
                {formatCurrency(eliminations.reduce((sum, e) => sum + e.credit_amount, 0))}
              </td>
              <td colSpan={2}></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );

  const renderRisksTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Cross-Entity Risk Consolidation</h2>
          <p className="text-sm text-gray-500">Consolidated risk assessment across all component entities</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          <Plus className="w-4 h-4" />
          Add Risk
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {risks.map(risk => (
          <div key={risk.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className={`p-2 rounded-lg ${
                  risk.combined_risk === 'high' || risk.combined_risk === 'very_high' ? 'bg-red-100' :
                  risk.combined_risk === 'moderate' ? 'bg-yellow-100' : 'bg-green-100'
                }`}>
                  <AlertTriangle className={`w-5 h-5 ${
                    risk.combined_risk === 'high' || risk.combined_risk === 'very_high' ? 'text-red-600' :
                    risk.combined_risk === 'moderate' ? 'text-yellow-600' : 'text-green-600'
                  }`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-semibold text-gray-900">{risk.risk_title}</h3>
                    {risk.pervasive && (
                      <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                        Pervasive
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mb-4">
                    Category: {risk.risk_category.replace('_', ' ')}
                  </p>
                  <div className="flex items-center gap-6">
                    <div>
                      <span className="text-xs text-gray-500">Inherent Risk</span>
                      <div className={`mt-1 px-2 py-1 rounded text-xs font-medium ${getRiskColor(risk.inherent_risk)}`}>
                        {risk.inherent_risk}
                      </div>
                    </div>
                    <div className="text-gray-300">×</div>
                    <div>
                      <span className="text-xs text-gray-500">Control Risk</span>
                      <div className={`mt-1 px-2 py-1 rounded text-xs font-medium ${getRiskColor(risk.control_risk)}`}>
                        {risk.control_risk}
                      </div>
                    </div>
                    <div className="text-gray-300">=</div>
                    <div>
                      <span className="text-xs text-gray-500">Combined Risk</span>
                      <div className={`mt-1 px-3 py-1 rounded text-sm font-semibold ${getRiskColor(risk.combined_risk)}`}>
                        {risk.combined_risk}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(risk.status)}`}>
                  {risk.status}
                </span>
                <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderConsolidationTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border border-green-100 p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-green-100 rounded-xl">
            <FileSpreadsheet className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Consolidated Financial Statement Assembly</h2>
            <p className="text-sm text-gray-600">Combine component financials with elimination adjustments</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <p className="text-sm text-gray-500 mb-1">Combined Assets</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(groupEngagement.total_assets)}</p>
            <p className="text-xs text-gray-500 mt-1">Before eliminations</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <p className="text-sm text-gray-500 mb-1">Total Eliminations</p>
            <p className="text-2xl font-bold text-red-600">
              ({formatCurrency(eliminations.reduce((sum, e) => sum + e.debit_amount, 0))})
            </p>
            <p className="text-xs text-gray-500 mt-1">{eliminations.length} entries</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <p className="text-sm text-gray-500 mb-1">Consolidated Assets</p>
            <p className="text-2xl font-bold text-green-600">
              {formatCurrency(groupEngagement.total_assets - eliminations.reduce((sum, e) => sum + e.debit_amount, 0))}
            </p>
            <p className="text-xs text-gray-500 mt-1">After eliminations</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <RefreshCw className="w-4 h-4" />
            Generate Consolidation
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-4 h-4" />
            Export Workbook
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <FileText className="w-4 h-4" />
            View Consolidated Statements
          </button>
        </div>
      </div>

      {/* Component Contributions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Component Contributions to Consolidated Totals</h3>
        <div className="space-y-3">
          {components.map(component => {
            const assetPercentage = (component.total_assets / groupEngagement.total_assets) * 100;
            return (
              <div key={component.id} className="flex items-center gap-4">
                <div className="w-32 text-sm font-medium text-gray-700">{component.entity_code}</div>
                <div className="flex-1">
                  <div className="h-8 bg-gray-100 rounded-lg overflow-hidden relative">
                    <div
                      className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-lg transition-all"
                      style={{ width: `${assetPercentage}%` }}
                    />
                    <div className="absolute inset-0 flex items-center justify-end px-3">
                      <span className="text-sm font-medium text-gray-700">
                        {formatCurrency(component.total_assets)} ({assetPercentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'components', label: 'Components', icon: Building2 },
    { id: 'auditors', label: 'Auditors', icon: Users },
    { id: 'eliminations', label: 'Eliminations', icon: Calculator },
    { id: 'risks', label: 'Risks', icon: AlertTriangle },
    { id: 'consolidation', label: 'Consolidation', icon: Layers },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                <Network className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{groupEngagement.group_name}</h1>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-sm text-gray-500">{groupEngagement.reporting_framework}</span>
                  <span className="text-gray-300">|</span>
                  <span className="text-sm text-gray-500">{components.length} Components</span>
                  <span className="text-gray-300">|</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(groupEngagement.status)}`}>
                    {groupEngagement.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                <Settings className="w-4 h-4" />
                Settings
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-1 mt-4 -mb-px">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-600 border-blue-600 bg-blue-50'
                      : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'components' && renderComponentsTab()}
        {activeTab === 'auditors' && renderAuditorsTab()}
        {activeTab === 'eliminations' && renderEliminationsTab()}
        {activeTab === 'risks' && renderRisksTab()}
        {activeTab === 'consolidation' && renderConsolidationTab()}
      </div>
    </div>
  );
};

export default GroupAuditManagement;
