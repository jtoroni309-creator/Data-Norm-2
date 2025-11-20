'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  FileSpreadsheet,
  Sparkles,
  Download,
  Eye,
  RefreshCw,
  CheckCircle2,
  TrendingUp,
  Calculator,
  FileText,
  DollarSign,
  BarChart3,
  Edit,
  Trash2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface WorkpaperGeneratorProps {
  engagementId: string;
}

interface Workpaper {
  id: string;
  workpaper_type: string;
  account: string;
  title: string;
  status: 'draft' | 'in_progress' | 'review' | 'completed';
  generated_at: string;
  completed_by?: string;
  data?: any;
  metadata?: any;
}

export function WorkpaperGenerator({ engagementId }: WorkpaperGeneratorProps) {
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  const [previewWorkpaper, setPreviewWorkpaper] = useState<Workpaper | null>(null);

  // Fetch engagement
  const { data: engagement } = useQuery({
    queryKey: ['engagement', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}`);
      return (response as any).data;
    },
  });

  // Fetch workpapers
  const { data: workpapers = [], isLoading, refetch } = useQuery({
    queryKey: ['workpapers', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/workpapers`);
      return (response as any).data;
    },
  });

  // Fetch trial balance
  const { data: trialBalance = [] } = useQuery({
    queryKey: ['trial-balance', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/trial-balance`);
      return (response as any).data;
    },
  });

  // Generate workpaper mutation
  const generateMutation = useMutation<{ data: any }, unknown, { type: string; account: string }>({
    mutationFn: async (data: { type: string; account: string }) => {
      return api.post(`/engagements/${engagementId}/workpapers/generate`, data);
    },
    onSuccess: (response) => {
      toast.success('Workpaper generated successfully');
      refetch();
      setPreviewWorkpaper(response.data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate workpaper');
    },
  });

  // Delete workpaper mutation
  const deleteMutation = useMutation({
    mutationFn: async (workpaperId: string) => {
      return api.delete(`/engagements/${engagementId}/workpapers/${workpaperId}`);
    },
    onSuccess: () => {
      toast.success('Workpaper deleted successfully');
      refetch();
    },
    onError: () => {
      toast.error('Failed to delete workpaper');
    },
  });

  // Download workpaper mutation
  const downloadMutation = useMutation<{ data: Blob }, unknown, string>({
    mutationFn: async (workpaperId: string) => {
      return api.get(`/engagements/${engagementId}/workpapers/${workpaperId}/download`, {
        responseType: 'blob',
      });
    },
    onSuccess: (response, workpaperId) => {
      const workpaper = workpapers.find((w: Workpaper) => w.id === workpaperId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = window.document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${workpaper?.title || 'workpaper'}.xlsx`);
      window.document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Workpaper downloaded successfully');
    },
    onError: () => {
      toast.error('Failed to download workpaper');
    },
  });

  const workpaperTypes = [
    {
      type: 'lead_schedule',
      label: 'Lead Schedule',
      description: 'Detailed account reconciliation with tie-outs to trial balance',
      icon: FileSpreadsheet,
      color: 'blue',
      features: ['Account rollforward', 'Prior year comparison', 'Variance analysis', 'Tie-outs'],
    },
    {
      type: 'analytical_procedures',
      label: 'Analytical Procedures',
      description: 'Ratio analysis, trend analysis, and variance explanations',
      icon: TrendingUp,
      color: 'green',
      features: ['Ratio calculations', 'Industry benchmarks', 'Trend charts', 'Variance explanations'],
    },
    {
      type: 'substantive_testing',
      label: 'Substantive Testing',
      description: 'Detail testing samples and recalculations',
      icon: Calculator,
      color: 'purple',
      features: ['Sample selection', 'Test procedures', 'Exception tracking', 'Conclusions'],
    },
    {
      type: 'disclosure_checklist',
      label: 'Disclosure Checklist',
      description: 'Comprehensive disclosure requirements checklist',
      icon: FileText,
      color: 'orange',
      features: ['ASC requirements', 'Completion status', 'Reference links', 'Review notes'],
    },
    {
      type: 'cash_flow',
      label: 'Cash Flow Analysis',
      description: 'Cash flow statement preparation and analysis',
      icon: DollarSign,
      color: 'indigo',
      features: ['Operating activities', 'Investing activities', 'Financing activities', 'Reconciliation'],
    },
    {
      type: 'ratio_analysis',
      label: 'Ratio Analysis',
      description: 'Financial ratios with industry comparison',
      icon: BarChart3,
      color: 'pink',
      features: ['Liquidity ratios', 'Profitability ratios', 'Leverage ratios', 'Activity ratios'],
    },
  ];

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-700' },
      in_progress: { label: 'In Progress', className: 'bg-blue-100 text-blue-700' },
      review: { label: 'Under Review', className: 'bg-yellow-100 text-yellow-700' },
      completed: { label: 'Completed', className: 'bg-green-100 text-green-700' },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getTypeInfo = (type: string) => {
    return workpaperTypes.find((wt) => wt.type === type) || workpaperTypes[0];
  };

  const handleGenerate = () => {
    if (!selectedType) {
      toast.error('Please select a workpaper type');
      return;
    }
    if (!selectedAccount) {
      toast.error('Please select an account');
      return;
    }

    generateMutation.mutate({ type: selectedType, account: selectedAccount });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Workpaper Generator</h2>
          <p className="text-gray-600 mt-1">
            AI-powered workpaper automation for {engagement?.client_name || 'engagement'}
          </p>
        </div>
        <Button
          onClick={() => refetch()}
          variant="outline"
          className="flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </Button>
      </div>

      {/* Generator */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          Generate New Workpaper
        </h3>

        {/* Workpaper Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Workpaper Type
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workpaperTypes.map((typeInfo) => {
              const Icon = typeInfo.icon;
              const isSelected = selectedType === typeInfo.type;

              return (
                <button
                  key={typeInfo.type}
                  onClick={() => setSelectedType(typeInfo.type)}
                  className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
                    isSelected
                      ? `border-${typeInfo.color}-500 bg-${typeInfo.color}-50`
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 bg-${typeInfo.color}-100 rounded-lg`}>
                      <Icon className={`w-5 h-5 text-${typeInfo.color}-600`} />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-1">{typeInfo.label}</h4>
                      <p className="text-sm text-gray-600 mb-2">{typeInfo.description}</p>
                      <div className="text-xs text-gray-500">
                        {typeInfo.features.slice(0, 2).map((feature, idx) => (
                          <div key={idx}>• {feature}</div>
                        ))}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Account Selection */}
        {selectedType && (
          <div className="mb-6 pt-6 border-t">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Account
            </label>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Choose an account...</option>
              {trialBalance.map((account: any) => (
                <option key={account.id} value={account.account_name}>
                  {account.account_number} - {account.account_name} (${account.balance?.toLocaleString() || '0'})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Generate Button */}
        {selectedType && selectedAccount && (
          <div className="pt-6 border-t flex items-center justify-between">
            <div className="text-sm text-gray-600">
              <p>Type: <span className="font-semibold">{getTypeInfo(selectedType).label}</span></p>
              <p>Account: <span className="font-semibold">{selectedAccount}</span></p>
            </div>
            <Button
              onClick={handleGenerate}
              disabled={generateMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {generateMutation.isPending ? 'Generating...' : 'Generate with AI'}
            </Button>
          </div>
        )}
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-3xl font-bold text-gray-900">{workpapers.length}</p>
            </div>
            <FileSpreadsheet className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-3xl font-bold text-gray-900">
                {workpapers.filter((w: Workpaper) => w.status === 'in_progress').length}
              </p>
            </div>
            <RefreshCw className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Under Review</p>
              <p className="text-3xl font-bold text-gray-900">
                {workpapers.filter((w: Workpaper) => w.status === 'review').length}
              </p>
            </div>
            <Eye className="w-8 h-8 text-yellow-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-3xl font-bold text-gray-900">
                {workpapers.filter((w: Workpaper) => w.status === 'completed').length}
              </p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
        </Card>
      </div>

      {/* Workpapers List */}
      <Card>
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-blue-600" />
            Generated Workpapers
            <Badge variant="outline" className="ml-2">{workpapers.length}</Badge>
          </h3>
        </div>

        {workpapers.length === 0 ? (
          <div className="p-12 text-center">
            <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No workpapers generated yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Select a type and account above to generate your first workpaper
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {workpapers.map((workpaper: Workpaper) => {
              const typeInfo = getTypeInfo(workpaper.workpaper_type);
              const Icon = typeInfo.icon;
              return (
                <div key={workpaper.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`p-3 bg-${typeInfo.color}-100 rounded-lg`}>
                        <Icon className={`w-6 h-6 text-${typeInfo.color}-600`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold text-gray-900">{workpaper.title}</h4>
                          {getStatusBadge(workpaper.status)}
                        </div>
                        <p className="text-sm text-gray-600 mb-1">
                          Account: <span className="font-medium">{workpaper.account}</span>
                        </p>
                        <p className="text-sm text-gray-600 mb-3">{typeInfo.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Generated: {new Date(workpaper.generated_at).toLocaleDateString()}</span>
                          {workpaper.completed_by && (
                            <span>Completed by: {workpaper.completed_by}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPreviewWorkpaper(workpaper)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        View
                      </Button>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => downloadMutation.mutate(workpaper.id)}
                        disabled={downloadMutation.isPending}
                        className="flex items-center gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteMutation.mutate(workpaper.id)}
                        disabled={deleteMutation.isPending}
                        className="flex items-center gap-2 text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Preview Modal */}
      {previewWorkpaper && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{previewWorkpaper.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{previewWorkpaper.account}</p>
              </div>
              <button
                onClick={() => setPreviewWorkpaper(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                ×
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              {previewWorkpaper.data ? (
                <div className="space-y-4">
                  <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    {JSON.stringify(previewWorkpaper.data, null, 2)}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-12">No preview data available</p>
              )}
            </div>
            <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setPreviewWorkpaper(null)}
              >
                Close
              </Button>
              <Button
                onClick={() => downloadMutation.mutate(previewWorkpaper.id)}
                disabled={downloadMutation.isPending}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Excel
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
