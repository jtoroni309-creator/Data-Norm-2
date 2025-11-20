'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  BookOpen,
  Sparkles,
  Download,
  Eye,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  FileText,
  Edit,
  Copy,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface DisclosuresGeneratorProps {
  engagementId: string;
}

interface Disclosure {
  id: string;
  disclosure_type: string;
  standard: string;
  title: string;
  content: string;
  status: 'draft' | 'review' | 'approved';
  generated_at: string;
  last_modified: string;
  metadata?: any;
}

export function DisclosuresGenerator({ engagementId }: DisclosuresGeneratorProps) {
  const [selectedStandard, setSelectedStandard] = useState<string>('');
  const [editingDisclosure, setEditingDisclosure] = useState<Disclosure | null>(null);
  const [previewDisclosure, setPreviewDisclosure] = useState<Disclosure | null>(null);

  // Fetch engagement data
  const { data: engagement } = useQuery<any>({
    queryKey: ['engagement', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}`);
      return (response as any).data;
    },
  });

  // Fetch existing disclosures
  const { data: disclosures = [], isLoading, refetch } = useQuery<any[]>({
    queryKey: ['disclosures', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/disclosures`);
      return (response as any).data as any[];
    },
  });

  // Generate disclosure mutation
  const generateMutation = useMutation<{ data: Disclosure }, unknown, string>({
    mutationFn: async (standard: string) => {
      return api.post(`/engagements/${engagementId}/disclosures/generate`, {
        standard,
      });
    },
    onSuccess: (response) => {
      toast.success('Disclosure generated successfully');
      refetch();
      setPreviewDisclosure(response.data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate disclosure');
    },
  });

  // Update disclosure mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, content }: { id: string; content: string }) => {
      return api.put(`/engagements/${engagementId}/disclosures/${id}`, { content });
    },
    onSuccess: () => {
      toast.success('Disclosure updated successfully');
      refetch();
      setEditingDisclosure(null);
    },
    onError: () => {
      toast.error('Failed to update disclosure');
    },
  });

  const disclosureStandards = [
    {
      standard: 'ASC 606',
      label: 'Revenue Recognition (ASC 606)',
      description: 'Revenue from contracts with customers',
      icon: BookOpen,
      color: 'blue',
      items: [
        'Disaggregation of revenue',
        'Performance obligations',
        'Transaction price allocation',
        'Contract balances',
        'Significant judgments',
      ],
    },
    {
      standard: 'ASC 842',
      label: 'Leases (ASC 842)',
      description: 'Lease accounting and disclosures',
      icon: FileText,
      color: 'green',
      items: [
        'Lease cost components',
        'Maturity analysis',
        'Weighted-average rates and terms',
        'ROU assets and liabilities',
        'Lease commitments',
      ],
    },
    {
      standard: 'ASC 326',
      label: 'Credit Losses (ASC 326)',
      description: 'Current expected credit losses (CECL)',
      icon: AlertCircle,
      color: 'orange',
      items: [
        'Allowance methodology',
        'Credit quality indicators',
        'Vintage analysis',
        'Roll-forward of allowance',
        'Write-offs and recoveries',
      ],
    },
    {
      standard: 'ASC 820',
      label: 'Fair Value (ASC 820)',
      description: 'Fair value measurements',
      icon: CheckCircle2,
      color: 'purple',
      items: [
        'Fair value hierarchy',
        'Valuation techniques',
        'Level 3 reconciliation',
        'Transfers between levels',
        'Unobservable inputs',
      ],
    },
    {
      standard: 'ASC 740',
      label: 'Income Taxes (ASC 740)',
      description: 'Income tax disclosures',
      icon: FileText,
      color: 'indigo',
      items: [
        'Effective tax rate reconciliation',
        'Deferred tax assets and liabilities',
        'Uncertain tax positions',
        'NOL carryforwards',
        'Valuation allowance',
      ],
    },
    {
      standard: 'ASC 718',
      label: 'Stock Compensation (ASC 718)',
      description: 'Stock-based compensation',
      icon: Sparkles,
      color: 'pink',
      items: [
        'Stock option activity',
        'Restricted stock units',
        'Valuation assumptions',
        'Expense recognition',
        'Outstanding awards',
      ],
    },
    {
      standard: 'ASC 450',
      label: 'Contingencies (ASC 450)',
      description: 'Commitments and contingencies',
      icon: AlertCircle,
      color: 'red',
      items: [
        'Legal proceedings',
        'Loss contingencies',
        'Warranties',
        'Guarantees',
        'Environmental liabilities',
      ],
    },
    {
      standard: 'ASC 470',
      label: 'Debt (ASC 470)',
      description: 'Debt and loan covenants',
      icon: FileText,
      color: 'teal',
      items: [
        'Debt instruments',
        'Maturity schedule',
        'Covenant requirements',
        'Interest rates',
        'Debt issuance costs',
      ],
    },
    {
      standard: 'ASC 850',
      label: 'Related Parties (ASC 850)',
      description: 'Related party transactions',
      icon: BookOpen,
      color: 'amber',
      items: [
        'Nature of relationships',
        'Transaction descriptions',
        'Amounts and terms',
        'Settlement basis',
        'Balances outstanding',
      ],
    },
  ];

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-700' },
      review: { label: 'Under Review', className: 'bg-yellow-100 text-yellow-700' },
      approved: { label: 'Approved', className: 'bg-green-100 text-green-700' },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getStandardInfo = (standard: string) => {
    return disclosureStandards.find((ds) => ds.standard === standard) || disclosureStandards[0];
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
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
          <h2 className="text-2xl font-bold text-gray-900">Disclosures Generator</h2>
          <p className="text-gray-600 mt-1">
            AI-powered disclosure notes for {engagement?.client_name || 'engagement'}
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

      {/* Standards Selection */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          Generate Disclosure Note
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {disclosureStandards.map((stdInfo) => {
            const Icon = stdInfo.icon;
            const isSelected = selectedStandard === stdInfo.standard;
            const existingDisclosure = disclosures.find(
              (d: Disclosure) => d.standard === stdInfo.standard
            );

            return (
              <button
                key={stdInfo.standard}
                onClick={() => setSelectedStandard(stdInfo.standard)}
                className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
                  isSelected
                    ? `border-${stdInfo.color}-500 bg-${stdInfo.color}-50`
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className={`p-2 bg-${stdInfo.color}-100 rounded-lg`}>
                    <Icon className={`w-5 h-5 text-${stdInfo.color}-600`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{stdInfo.label}</h4>
                      {existingDisclosure && (
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{stdInfo.description}</p>
                  </div>
                </div>
                <div className="pl-11">
                  <p className="text-xs font-medium text-gray-500 mb-1">Includes:</p>
                  <ul className="text-xs text-gray-600 space-y-0.5">
                    {stdInfo.items.slice(0, 3).map((item, idx) => (
                      <li key={idx}>• {item}</li>
                    ))}
                    {stdInfo.items.length > 3 && (
                      <li className="text-gray-400">+ {stdInfo.items.length - 3} more...</li>
                    )}
                  </ul>
                </div>
              </button>
            );
          })}
        </div>
        {selectedStandard && (
          <div className="mt-6 pt-6 border-t flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Selected: <span className="font-semibold">{getStandardInfo(selectedStandard).label}</span>
            </p>
            <Button
              onClick={() => generateMutation.mutate(selectedStandard)}
              disabled={generateMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {generateMutation.isPending ? 'Generating...' : 'Generate with AI'}
            </Button>
          </div>
        )}
      </Card>

      {/* Existing Disclosures */}
      <Card>
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-600" />
            Generated Disclosures
            <Badge variant="outline" className="ml-2">{disclosures.length}</Badge>
          </h3>
        </div>

        {disclosures.length === 0 ? (
          <div className="p-12 text-center">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No disclosures generated yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Select a standard above to generate your first disclosure note
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {disclosures.map((disclosure: Disclosure) => {
              const stdInfo = getStandardInfo(disclosure.standard);
              const Icon = stdInfo.icon;
              return (
                <div key={disclosure.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`p-3 bg-${stdInfo.color}-100 rounded-lg`}>
                        <Icon className={`w-6 h-6 text-${stdInfo.color}-600`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold text-gray-900">{disclosure.title}</h4>
                          {getStatusBadge(disclosure.status)}
                          <Badge variant="outline" className="text-xs">{disclosure.standard}</Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {disclosure.content.substring(0, 150)}...
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Generated: {new Date(disclosure.generated_at).toLocaleDateString()}</span>
                          <span>Modified: {new Date(disclosure.last_modified).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(disclosure.content)}
                        className="flex items-center gap-2"
                      >
                        <Copy className="w-4 h-4" />
                        Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingDisclosure(disclosure)}
                        className="flex items-center gap-2"
                      >
                        <Edit className="w-4 h-4" />
                        Edit
                      </Button>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => setPreviewDisclosure(disclosure)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        View
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Edit Modal */}
      {editingDisclosure && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-xl font-bold">Edit Disclosure</h3>
              <button
                onClick={() => setEditingDisclosure(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <AlertCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              <textarea
                value={editingDisclosure.content}
                onChange={(e) =>
                  setEditingDisclosure({ ...editingDisclosure, content: e.target.value })
                }
                className="w-full h-96 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
            <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setEditingDisclosure(null)}
              >
                Cancel
              </Button>
              <Button
                onClick={() =>
                  updateMutation.mutate({
                    id: editingDisclosure.id,
                    content: editingDisclosure.content,
                  })
                }
                disabled={updateMutation.isPending}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Preview Modal */}
      {previewDisclosure && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{previewDisclosure.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{previewDisclosure.standard}</p>
              </div>
              <button
                onClick={() => setPreviewDisclosure(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <AlertCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed">
                  {previewDisclosure.content}
                </pre>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => copyToClipboard(previewDisclosure.content)}
                className="flex items-center gap-2"
              >
                <Copy className="w-4 h-4" />
                Copy to Clipboard
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setPreviewDisclosure(null);
                  setEditingDisclosure(previewDisclosure);
                }}
                className="flex items-center gap-2"
              >
                <Edit className="w-4 h-4" />
                Edit
              </Button>
              <Button
                onClick={() => setPreviewDisclosure(null)}
              >
                Close
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
