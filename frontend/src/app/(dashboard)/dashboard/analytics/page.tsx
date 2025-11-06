'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Play,
  Download,
  Search,
} from 'lucide-react';
import { api } from '@/lib/api';
import { formatCurrency, formatDate, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';

export default function AnalyticsPage() {
  const [selectedEngagement, setSelectedEngagement] = useState<string>('');
  const [activeTab, setActiveTab] = useState('je-testing');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch engagements for selection
  const { data: engagements = [] } = useQuery({
    queryKey: ['engagements'],
    queryFn: api.engagements.list,
  });

  // JE Testing Query
  const {
    data: jeResults = [],
    isLoading: isLoadingJE,
    refetch: refetchJE,
  } = useQuery({
    queryKey: ['je-testing', selectedEngagement],
    queryFn: () => api.analytics.jeTests(selectedEngagement),
    enabled: !!selectedEngagement,
  });

  // Anomalies Query
  const {
    data: anomalies = [],
    isLoading: isLoadingAnomalies,
    refetch: refetchAnomalies,
  } = useQuery({
    queryKey: ['anomalies', selectedEngagement],
    queryFn: () => api.analytics.anomalies.list(selectedEngagement),
    enabled: !!selectedEngagement,
  });

  // Ratios Query
  const {
    data: ratios = [],
    isLoading: isLoadingRatios,
    refetch: refetchRatios,
  } = useQuery({
    queryKey: ['ratios', selectedEngagement],
    queryFn: () => api.analytics.ratios(selectedEngagement),
    enabled: !!selectedEngagement,
  });

  // Run JE Testing Mutation
  const runJETestingMutation = useMutation({
    mutationFn: () => api.analytics.jeTests(selectedEngagement),
    onSuccess: () => {
      toast.success('JE Testing completed successfully!');
      refetchJE();
    },
    onError: () => {
      toast.error('Failed to run JE Testing');
    },
  });

  // Run Anomaly Detection Mutation
  const runAnomalyDetectionMutation = useMutation({
    mutationFn: () => api.analytics.anomalies.detect(selectedEngagement, 'zscore'),
    onSuccess: () => {
      toast.success('Anomaly detection completed successfully!');
      refetchAnomalies();
    },
    onError: () => {
      toast.error('Failed to run anomaly detection');
    },
  });

  const filteredJEResults = jeResults.filter(
    (result: any) =>
      result.entry_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      result.reason.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const flaggedJECount = jeResults.filter((r: any) => r.flagged).length;
  const criticalAnomaliesCount = anomalies.filter((a: any) => a.severity === 'critical').length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            AI-powered analysis and testing for your engagements
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
            <BarChart3 className="h-16 w-16 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">Select an engagement to begin</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Choose an engagement from the dropdown above to run analytics
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
                    <p className="text-2xl font-bold">{jeResults.length}</p>
                    <p className="text-sm text-muted-foreground">JEs Tested</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-orange-600">{flaggedJECount}</p>
                    <p className="text-sm text-muted-foreground">Flagged Entries</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-red-600">{criticalAnomaliesCount}</p>
                    <p className="text-sm text-muted-foreground">Critical Anomalies</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-green-600">{ratios.length}</p>
                    <p className="text-sm text-muted-foreground">Ratios Calculated</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="je-testing">JE Testing</TabsTrigger>
              <TabsTrigger value="anomalies">Anomaly Detection</TabsTrigger>
              <TabsTrigger value="ratios">Ratio Analysis</TabsTrigger>
            </TabsList>

            {/* JE Testing Tab */}
            <TabsContent value="je-testing" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Journal Entry Testing</CardTitle>
                      <CardDescription>
                        AI-powered testing of journal entries for unusual patterns
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        onClick={() => runJETestingMutation.mutate()}
                        loading={runJETestingMutation.isPending}
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Run Testing
                      </Button>
                      <Button variant="outline">
                        <Download className="mr-2 h-4 w-4" />
                        Export
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Search */}
                  <div className="mb-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        placeholder="Search by entry number or reason..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                  </div>

                  {isLoadingJE ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    </div>
                  ) : filteredJEResults.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <BarChart3 className="h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">No test results yet</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Click "Run Testing" to analyze journal entries
                      </p>
                    </div>
                  ) : (
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Entry #</TableHead>
                            <TableHead>Date</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Test Type</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Reason</TableHead>
                            <TableHead>Score</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {filteredJEResults.map((result: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell className="font-medium">{result.entry_number}</TableCell>
                              <TableCell>{formatDate(result.entry_date, 'short')}</TableCell>
                              <TableCell>{formatCurrency(result.amount)}</TableCell>
                              <TableCell>
                                <Badge variant="outline">{result.test_type}</Badge>
                              </TableCell>
                              <TableCell>
                                {result.flagged ? (
                                  <Badge variant="warning">
                                    <AlertTriangle className="mr-1 h-3 w-3" />
                                    Flagged
                                  </Badge>
                                ) : (
                                  <Badge variant="success">
                                    <CheckCircle2 className="mr-1 h-3 w-3" />
                                    Passed
                                  </Badge>
                                )}
                              </TableCell>
                              <TableCell className="max-w-xs truncate">{result.reason}</TableCell>
                              <TableCell>
                                {result.score ? formatNumber(result.score, 2) : '-'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Anomaly Detection Tab */}
            <TabsContent value="anomalies" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Anomaly Detection</CardTitle>
                      <CardDescription>
                        Machine learning-based detection of unusual transactions
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        onClick={() => runAnomalyDetectionMutation.mutate()}
                        loading={runAnomalyDetectionMutation.isPending}
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Run Detection
                      </Button>
                      <Button variant="outline">
                        <Download className="mr-2 h-4 w-4" />
                        Export
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {isLoadingAnomalies ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    </div>
                  ) : anomalies.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <AlertTriangle className="h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">No anomalies detected yet</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Click "Run Detection" to analyze for anomalies
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {anomalies.map((anomaly: any, index: number) => (
                        <div
                          key={index}
                          className="flex items-start justify-between rounded-lg border p-4"
                        >
                          <div className="flex-1 space-y-1">
                            <div className="flex items-center space-x-2">
                              <p className="font-medium">{anomaly.transaction_id}</p>
                              <Badge
                                variant={
                                  anomaly.severity === 'critical'
                                    ? 'destructive'
                                    : anomaly.severity === 'high'
                                    ? 'warning'
                                    : 'default'
                                }
                              >
                                {anomaly.severity}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">{anomaly.description}</p>
                            <div className="flex items-center space-x-4 text-sm">
                              <span>Amount: {formatCurrency(anomaly.amount)}</span>
                              <span>•</span>
                              <span>Score: {formatNumber(anomaly.anomaly_score, 2)}</span>
                              <span>•</span>
                              <span>Method: {anomaly.detection_method}</span>
                            </div>
                          </div>
                          <Button variant="outline" size="sm">
                            Review
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Ratio Analysis Tab */}
            <TabsContent value="ratios" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Ratio Analysis</CardTitle>
                      <CardDescription>
                        Financial ratios and trend analysis
                      </CardDescription>
                    </div>
                    <Button variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Export
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {isLoadingRatios ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    </div>
                  ) : ratios.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <TrendingUp className="h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">No ratios calculated yet</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Ratio analysis will appear here once data is processed
                      </p>
                    </div>
                  ) : (
                    <div className="grid gap-4 md:grid-cols-2">
                      {ratios.map((ratio: any, index: number) => (
                        <div key={index} className="rounded-lg border p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{ratio.ratio_name}</p>
                              <p className="text-2xl font-bold">{formatNumber(ratio.value, 2)}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm text-muted-foreground">Industry Avg</p>
                              <p className="font-semibold">
                                {formatNumber(ratio.industry_average, 2)}
                              </p>
                            </div>
                          </div>
                          {ratio.variance && (
                            <div className="mt-2">
                              <Badge
                                variant={
                                  Math.abs(ratio.variance) > 20 ? 'destructive' : 'success'
                                }
                              >
                                {ratio.variance > 0 ? '+' : ''}
                                {formatNumber(ratio.variance, 1)}%
                              </Badge>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}
