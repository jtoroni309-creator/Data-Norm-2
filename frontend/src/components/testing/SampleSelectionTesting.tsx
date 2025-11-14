'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Target,
  Sparkles,
  Download,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Eye,
  FileSpreadsheet,
  TrendingUp,
  Percent,
  DollarSign,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface SampleSelectionTestingProps {
  engagementId: string;
}

interface Sample {
  id: string;
  account: string;
  population_size: number;
  sample_size: number;
  sampling_method: string;
  risk_level: 'low' | 'moderate' | 'high';
  status: 'planning' | 'in_progress' | 'completed';
  tested_count: number;
  exceptions_count: number;
  generated_at: string;
}

interface TestResult {
  id: string;
  sample_id: string;
  item_id: string;
  item_description: string;
  amount: number;
  test_performed: string;
  result: 'pass' | 'fail' | 'pending';
  exception_notes?: string;
  tested_by?: string;
  tested_date?: string;
}

export function SampleSelectionTesting({ engagementId }: SampleSelectionTestingProps) {
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  const [samplingMethod, setSamplingMethod] = useState<string>('statistical');
  const [riskLevel, setRiskLevel] = useState<string>('moderate');
  const [sampleSize, setSampleSize] = useState<number>(25);
  const [viewingSample, setViewingSample] = useState<Sample | null>(null);

  const queryClient = useQueryClient();

  // Fetch trial balance for account selection
  const { data: trialBalance = [] } = useQuery({
    queryKey: ['trial-balance', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/trial-balance`);
      return response.data;
    },
  });

  // Fetch samples
  const { data: samples = [], isLoading, refetch } = useQuery({
    queryKey: ['samples', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/samples`);
      return response.data;
    },
  });

  // Fetch test results for selected sample
  const { data: testResults = [] } = useQuery({
    queryKey: ['test-results', viewingSample?.id],
    queryFn: async () => {
      if (!viewingSample) return [];
      const response = await api.get(`/engagements/${engagementId}/samples/${viewingSample.id}/results`);
      return response.data;
    },
    enabled: !!viewingSample,
  });

  // Generate sample mutation
  const generateSampleMutation = useMutation({
    mutationFn: async (data: any) => {
      return api.post(`/engagements/${engagementId}/samples/generate`, data);
    },
    onSuccess: () => {
      toast.success('Sample generated successfully');
      refetch();
      setSelectedAccount('');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate sample');
    },
  });

  // Record test result mutation
  const recordTestMutation = useMutation({
    mutationFn: async (data: any) => {
      return api.post(
        `/engagements/${engagementId}/samples/${viewingSample?.id}/results`,
        data
      );
    },
    onSuccess: () => {
      toast.success('Test result recorded');
      queryClient.invalidateQueries({ queryKey: ['test-results', viewingSample?.id] });
      queryClient.invalidateQueries({ queryKey: ['samples', engagementId] });
    },
    onError: () => {
      toast.error('Failed to record test result');
    },
  });

  const handleGenerateSample = () => {
    if (!selectedAccount) {
      toast.error('Please select an account');
      return;
    }

    generateSampleMutation.mutate({
      account: selectedAccount,
      sampling_method: samplingMethod,
      risk_level: riskLevel,
      sample_size: sampleSize,
    });
  };

  const getRiskBadge = (risk: string) => {
    const riskConfig = {
      low: { label: 'Low Risk', className: 'bg-green-100 text-green-700' },
      moderate: { label: 'Moderate Risk', className: 'bg-yellow-100 text-yellow-700' },
      high: { label: 'High Risk', className: 'bg-red-100 text-red-700' },
    };
    const config = riskConfig[risk as keyof typeof riskConfig] || riskConfig.moderate;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      planning: { label: 'Planning', className: 'bg-gray-100 text-gray-700' },
      in_progress: { label: 'In Progress', className: 'bg-blue-100 text-blue-700' },
      completed: { label: 'Completed', className: 'bg-green-100 text-green-700' },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.planning;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getResultBadge = (result: string) => {
    const resultConfig = {
      pass: { label: 'Pass', className: 'bg-green-100 text-green-700', icon: CheckCircle2 },
      fail: { label: 'Fail', className: 'bg-red-100 text-red-700', icon: AlertCircle },
      pending: { label: 'Pending', className: 'bg-gray-100 text-gray-700', icon: RefreshCw },
    };
    const config = resultConfig[result as keyof typeof resultConfig] || resultConfig.pending;
    const Icon = config.icon;
    return (
      <Badge className={`${config.className} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
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
          <h2 className="text-2xl font-bold text-gray-900">Sample Selection & Testing</h2>
          <p className="text-gray-600 mt-1">
            AI-powered statistical and judgmental sampling
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

      {/* Sample Generator */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          Generate New Sample
        </h3>

        <div className="space-y-4">
          {/* Account Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                  {account.account_number} - {account.account_name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Sampling Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sampling Method
              </label>
              <select
                value={samplingMethod}
                onChange={(e) => setSamplingMethod(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="statistical">Statistical (Random)</option>
                <option value="systematic">Systematic</option>
                <option value="judgmental">Judgmental</option>
                <option value="stratified">Stratified</option>
                <option value="monetary_unit">Monetary Unit Sampling</option>
              </select>
            </div>

            {/* Risk Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Risk Assessment
              </label>
              <select
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="low">Low Risk</option>
                <option value="moderate">Moderate Risk</option>
                <option value="high">High Risk</option>
              </select>
            </div>

            {/* Sample Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sample Size
              </label>
              <input
                type="number"
                value={sampleSize}
                onChange={(e) => setSampleSize(parseInt(e.target.value) || 25)}
                min="1"
                max="500"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="pt-4 border-t flex items-center justify-end">
            <Button
              onClick={handleGenerateSample}
              disabled={!selectedAccount || generateSampleMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {generateSampleMutation.isPending ? 'Generating...' : 'Generate Sample'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Samples</p>
              <p className="text-3xl font-bold text-gray-900">{samples.length}</p>
            </div>
            <Target className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-3xl font-bold text-gray-900">
                {samples.filter((s: Sample) => s.status === 'in_progress').length}
              </p>
            </div>
            <RefreshCw className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-3xl font-bold text-gray-900">
                {samples.filter((s: Sample) => s.status === 'completed').length}
              </p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Exceptions</p>
              <p className="text-3xl font-bold text-gray-900">
                {samples.reduce((sum: number, s: Sample) => sum + s.exceptions_count, 0)}
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Samples List */}
      <Card>
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-blue-600" />
            Generated Samples
            <Badge variant="outline" className="ml-2">{samples.length}</Badge>
          </h3>
        </div>

        {samples.length === 0 ? (
          <div className="p-12 text-center">
            <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No samples generated yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Generate your first sample using the form above
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {samples.map((sample: Sample) => {
              const completionRate = (sample.tested_count / sample.sample_size) * 100;
              const exceptionRate = sample.tested_count > 0
                ? (sample.exceptions_count / sample.tested_count) * 100
                : 0;

              return (
                <div key={sample.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-semibold text-gray-900">{sample.account}</h4>
                        {getStatusBadge(sample.status)}
                        {getRiskBadge(sample.risk_level)}
                        <Badge variant="outline" className="text-xs">{sample.sampling_method}</Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                        <div>
                          <p className="text-xs text-gray-500">Population</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {sample.population_size.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Sample Size</p>
                          <p className="text-sm font-semibold text-gray-900">{sample.sample_size}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Tested</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {sample.tested_count} / {sample.sample_size}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Exceptions</p>
                          <p className="text-sm font-semibold text-red-600">{sample.exceptions_count}</p>
                        </div>
                      </div>

                      {/* Progress Bars */}
                      <div className="space-y-2">
                        <div>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-600">Testing Progress</span>
                            <span className="font-semibold">{completionRate.toFixed(0)}%</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-600 to-purple-600"
                              style={{ width: `${completionRate}%` }}
                            />
                          </div>
                        </div>
                        {exceptionRate > 0 && (
                          <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="text-gray-600">Exception Rate</span>
                              <span className="font-semibold text-red-600">{exceptionRate.toFixed(1)}%</span>
                            </div>
                            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-red-500"
                                style={{ width: `${exceptionRate}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setViewingSample(sample)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Sample Detail Modal */}
      {viewingSample && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{viewingSample.account}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Sample Size: {viewingSample.sample_size} | {viewingSample.sampling_method}
                </p>
              </div>
              <button
                onClick={() => setViewingSample(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                ×
              </button>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Test</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tested By</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {testResults.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                          No test results recorded yet
                        </td>
                      </tr>
                    ) : (
                      testResults.map((result: TestResult) => (
                        <tr key={result.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">{result.item_id}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{result.item_description}</td>
                          <td className="px-4 py-3 text-sm text-gray-900 text-right">
                            ${result.amount.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">{result.test_performed}</td>
                          <td className="px-4 py-3">{getResultBadge(result.result)}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{result.tested_by || '-'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
              <Button variant="outline" onClick={() => setViewingSample(null)}>
                Close
              </Button>
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export Results
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
