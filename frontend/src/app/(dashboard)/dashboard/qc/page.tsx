'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tantml:react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  Download,
  Search,
  Shield,
  FileText,
} from 'lucide-react';
import { api } from '@/lib/api';
import { formatDate, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';

interface QCPolicy {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  active: boolean;
}

interface QCResult {
  id: string;
  policy_id: string;
  policy_name: string;
  status: 'passed' | 'failed' | 'warning';
  message: string;
  details?: any;
  timestamp: string;
}

export default function QualityControlPage() {
  const [selectedEngagement, setSelectedEngagement] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Fetch engagements
  const { data: engagements = [] } = useQuery({
    queryKey: ['engagements'],
    queryFn: api.engagements.list,
  });

  // Fetch QC policies
  const { data: policies = [] } = useQuery({
    queryKey: ['qc-policies'],
    queryFn: api.qc.policies.list,
  });

  // Fetch QC results
  const {
    data: results = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['qc-results', selectedEngagement],
    queryFn: () => api.qc.results.list(selectedEngagement),
    enabled: !!selectedEngagement,
  });

  // Execute QC policies mutation
  const executePoliciesMutation = useMutation({
    mutationFn: (policyIds: string[]) =>
      api.qc.execute(selectedEngagement, { policy_ids: policyIds }),
    onSuccess: () => {
      toast.success('Quality control policies executed successfully!');
      refetch();
    },
    onError: () => {
      toast.error('Failed to execute quality control policies');
    },
  });

  // Filter results
  const filteredResults = results.filter((result: QCResult) => {
    const matchesSearch =
      result.policy_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      result.message.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || result.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // Calculate stats
  const passedCount = results.filter((r: QCResult) => r.status === 'passed').length;
  const failedCount = results.filter((r: QCResult) => r.status === 'failed').length;
  const warningCount = results.filter((r: QCResult) => r.status === 'warning').length;
  const complianceRate =
    results.length > 0 ? (passedCount / results.length) * 100 : 0;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      default:
        return null;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'failed':
        return 'destructive';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getSeverityBadgeVariant = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'error':
        return 'destructive';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quality Control</h1>
          <p className="text-muted-foreground">
            Automated policy execution and compliance monitoring
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={selectedEngagement}
            onChange={(e) => setSelectedEngagement(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="">Select engagement...</option>
            {engagements.map((eng: any) => (
              <option key={eng.id} value={eng.id}>
                {eng.client_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!selectedEngagement ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Shield className="h-16 w-16 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">Select an engagement to begin</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Choose an engagement from the dropdown above to run quality control
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">{formatNumber(complianceRate, 0)}%</p>
                    <p className="text-sm text-muted-foreground">Compliance Rate</p>
                  </div>
                  <Shield className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-green-600">{passedCount}</p>
                    <p className="text-sm text-muted-foreground">Passed</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-orange-600">{warningCount}</p>
                    <p className="text-sm text-muted-foreground">Warnings</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-red-600">{failedCount}</p>
                    <p className="text-sm text-muted-foreground">Failed</p>
                  </div>
                  <XCircle className="h-8 w-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* QC Policies */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Quality Control Policies</CardTitle>
                  <CardDescription>
                    {policies.filter((p: QCPolicy) => p.active).length} active policies
                  </CardDescription>
                </div>
                <Button
                  onClick={() =>
                    executePoliciesMutation.mutate(
                      policies.filter((p: QCPolicy) => p.active).map((p: QCPolicy) => p.id)
                    )
                  }
                  loading={executePoliciesMutation.isPending}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Execute All Policies
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {policies.map((policy: QCPolicy) => (
                  <div
                    key={policy.id}
                    className="flex items-start justify-between rounded-lg border p-4"
                  >
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium">{policy.name}</p>
                        <Badge variant={getSeverityBadgeVariant(policy.severity)}>
                          {policy.severity}
                        </Badge>
                        {policy.active && <Badge variant="success">Active</Badge>}
                      </div>
                      <p className="text-sm text-muted-foreground">{policy.description}</p>
                      <p className="text-xs text-muted-foreground">Category: {policy.category}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* QC Results */}
          <Card>
            <CardHeader>
              <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
                <div>
                  <CardTitle>Policy Execution Results</CardTitle>
                  <CardDescription>
                    {filteredResults.length} of {results.length} results
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline">
                    <Download className="mr-2 h-4 w-4" />
                    Export Report
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="mb-4 flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search results..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="all">All Status</option>
                  <option value="passed">Passed</option>
                  <option value="warning">Warning</option>
                  <option value="failed">Failed</option>
                </select>
              </div>

              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : filteredResults.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <FileText className="h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-semibold">No QC results yet</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {searchQuery || statusFilter !== 'all'
                      ? 'Try adjusting your filters'
                      : 'Click "Execute All Policies" to run quality control checks'}
                  </p>
                </div>
              ) : (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Policy</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Message</TableHead>
                        <TableHead>Timestamp</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredResults.map((result: QCResult) => (
                        <TableRow key={result.id}>
                          <TableCell className="font-medium">{result.policy_name}</TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(result.status)}
                              <Badge variant={getStatusBadgeVariant(result.status)}>
                                {result.status}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell className="max-w-md">
                            <p className="truncate">{result.message}</p>
                          </TableCell>
                          <TableCell>{formatDate(result.timestamp, 'short')}</TableCell>
                          <TableCell className="text-right">
                            <Button variant="outline" size="sm">
                              View Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
