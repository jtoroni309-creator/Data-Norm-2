'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  FileText,
  Download,
  Eye,
  Send,
  RefreshCw,
  Calendar,
  Building,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface ReportGeneratorProps {
  engagementId: string;
}

interface Report {
  id: string;
  report_type: string;
  title: string;
  status: 'draft' | 'review' | 'final' | 'issued';
  generated_at: string;
  issued_date?: string;
  content?: string;
  metadata?: any;
}

export function ReportGenerator({ engagementId }: ReportGeneratorProps) {
  const [selectedReportType, setSelectedReportType] = useState<string>('');
  const [previewReport, setPreviewReport] = useState<Report | null>(null);

  // Fetch engagement details
  const { data: engagement } = useQuery({
    queryKey: ['engagement', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}`);
      return response.data;
    },
  });

  // Fetch existing reports
  const { data: reports = [], isLoading, refetch } = useQuery({
    queryKey: ['reports', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/reports`);
      return response.data;
    },
  });

  // Generate report mutation
  const generateMutation = useMutation({
    mutationFn: async (reportType: string) => {
      return api.post(`/engagements/${engagementId}/reports/generate`, {
        report_type: reportType,
      });
    },
    onSuccess: (response) => {
      toast.success('Report generated successfully');
      refetch();
      setPreviewReport(response.data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate report');
    },
  });

  // Download report mutation
  const downloadMutation = useMutation({
    mutationFn: async (reportId: string) => {
      return api.get(`/engagements/${engagementId}/reports/${reportId}/download`, {
        responseType: 'blob',
      });
    },
    onSuccess: (response, reportId) => {
      const report = reports.find((r: Report) => r.id === reportId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${report?.title || 'report'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Report downloaded successfully');
    },
    onError: () => {
      toast.error('Failed to download report');
    },
  });

  const reportTypes = [
    {
      type: 'audit_opinion',
      label: 'Audit Opinion',
      description: 'Independent auditor\'s report with opinion on financial statements',
      icon: CheckCircle2,
      color: 'blue',
    },
    {
      type: 'financial_statements',
      label: 'Financial Statements',
      description: 'Complete set of financial statements with notes',
      icon: FileText,
      color: 'green',
    },
    {
      type: 'management_letter',
      label: 'Management Letter',
      description: 'Internal control deficiencies and recommendations',
      icon: AlertCircle,
      color: 'orange',
    },
    {
      type: 'audit_adjustments',
      label: 'Summary of Adjustments',
      description: 'Summary of audit adjustments and unadjusted differences',
      icon: FileText,
      color: 'purple',
    },
    {
      type: 'representation_letter',
      label: 'Management Representation Letter',
      description: 'Management representations required for audit completion',
      icon: Building,
      color: 'indigo',
    },
    {
      type: 'audit_committee',
      label: 'Audit Committee Communication',
      description: 'Required communications under AS 1301',
      icon: FileText,
      color: 'pink',
    },
  ];

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-700' },
      review: { label: 'Under Review', className: 'bg-yellow-100 text-yellow-700' },
      final: { label: 'Final', className: 'bg-blue-100 text-blue-700' },
      issued: { label: 'Issued', className: 'bg-green-100 text-green-700' },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getReportTypeInfo = (type: string) => {
    return reportTypes.find((rt) => rt.type === type) || reportTypes[0];
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
          <h2 className="text-2xl font-bold text-gray-900">Report Generator</h2>
          <p className="text-gray-600 mt-1">
            AI-powered report generation for {engagement?.client_name || 'engagement'}
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

      {/* Report Type Selection */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          Generate New Report
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTypes.map((reportType) => {
            const Icon = reportType.icon;
            return (
              <button
                key={reportType.type}
                onClick={() => setSelectedReportType(reportType.type)}
                className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
                  selectedReportType === reportType.type
                    ? `border-${reportType.color}-500 bg-${reportType.color}-50`
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 bg-${reportType.color}-100 rounded-lg`}>
                    <Icon className={`w-5 h-5 text-${reportType.color}-600`} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">{reportType.label}</h4>
                    <p className="text-sm text-gray-600">{reportType.description}</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
        {selectedReportType && (
          <div className="mt-6 pt-6 border-t flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Selected: <span className="font-semibold">{getReportTypeInfo(selectedReportType).label}</span>
            </p>
            <Button
              onClick={() => generateMutation.mutate(selectedReportType)}
              disabled={generateMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {generateMutation.isPending ? 'Generating...' : 'Generate with AI'}
            </Button>
          </div>
        )}
      </Card>

      {/* Existing Reports */}
      <Card>
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Generated Reports
            <Badge variant="outline" className="ml-2">{reports.length}</Badge>
          </h3>
        </div>

        {reports.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No reports generated yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Select a report type above to generate your first report
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {reports.map((report: Report) => {
              const reportInfo = getReportTypeInfo(report.report_type);
              const Icon = reportInfo.icon;
              return (
                <div key={report.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`p-3 bg-${reportInfo.color}-100 rounded-lg`}>
                        <Icon className={`w-6 h-6 text-${reportInfo.color}-600`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold text-gray-900">{report.title}</h4>
                          {getStatusBadge(report.status)}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{reportInfo.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            Generated: {new Date(report.generated_at).toLocaleDateString()}
                          </span>
                          {report.issued_date && (
                            <span className="flex items-center gap-1">
                              <Send className="w-3 h-3" />
                              Issued: {new Date(report.issued_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPreviewReport(report)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        Preview
                      </Button>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => downloadMutation.mutate(report.id)}
                        disabled={downloadMutation.isPending}
                        className="flex items-center gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Download
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
      {previewReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-xl font-bold">{previewReport.title}</h3>
              <button
                onClick={() => setPreviewReport(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <AlertCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              {previewReport.content ? (
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-sm">{previewReport.content}</pre>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-12">No preview available</p>
              )}
            </div>
            <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setPreviewReport(null)}
              >
                Close
              </Button>
              <Button
                onClick={() => downloadMutation.mutate(previewReport.id)}
                disabled={downloadMutation.isPending}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
