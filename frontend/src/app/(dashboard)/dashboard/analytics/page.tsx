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

  const jeResultsArray = (jeResults as any[]) || [];
  const anomaliesArray = (anomalies as any[]) || [];
  const engagementsArray = (engagements as any[]) || [];
  const ratiosArray = (ratios as any[]) || [];

  const filteredJEResults = jeResultsArray.filter(
    (result: any) =>
      result.entry_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      result.reason?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const flaggedJECount = jeResultsArray.filter((r: any) => r.flagged).length;
  const criticalAnomaliesCount = anomaliesArray.filter((a: any) => a.severity === 'critical').length;

  return (
    <div className="space-y-8 pb-8">
      {/* Premium Page Header with Gradient */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 p-8 text-white shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"></div>
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-purple-500/20 blur-3xl"></div>

        <div className="relative z-10 flex items-center justify-between">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8" />
              <h1 className="text-4xl font-bold tracking-tight">Analytics</h1>
            </div>
            <p className="text-blue-100 text-lg">AI-powered analysis and testing for your engagements</p>
          </div>
          <div className="flex items-center space-x-3">
            <select
              value={selectedEngagement}
              onChange={(e) => setSelectedEngagement(e.target.value)}
              className="flex h-12 min-w-[250px] rounded-xl border-2 border-white/30 bg-white/10 backdrop-blur-md px-4 py-2 text-sm text-white placeholder:text-white/60 focus:border-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
            >
              <option value="" className="text-gray-900">Select engagement...</option>
              {engagementsArray.map((eng: any) => (
                <option key={eng.id} value={eng.id} className="text-gray-900">
                  {eng.client_name}
                </option>
              ))}
            </select>
          </div>
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
          {/* Premium Stats Grid */}
          <div className="grid gap-6 md:grid-cols-4">
            <Card className="group relative overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-500 hover-lift bg-gradient-to-br from-white via-blue-50/30 to-cyan-50/40 dark:from-gray-900 dark:via-blue-950/30 dark:to-cyan-950/40">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-500/10 to-transparent rounded-bl-full"></div>
              <CardContent className="pt-6 pb-6 relative z-10">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">JEs Tested</p>
                    <p className="text-4xl font-bold text-blue-600 dark:text-blue-400">{jeResultsArray.length}</p>
                    <div className="h-1 w-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"></div>
                  </div>
                  <div className="rounded-2xl p-3 bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <BarChart3 className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="group relative overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-500 hover-lift bg-gradient-to-br from-white via-orange-50/30 to-amber-50/40 dark:from-gray-900 dark:via-orange-950/30 dark:to-amber-950/40">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-orange-500/10 to-transparent rounded-bl-full"></div>
              <CardContent className="pt-6 pb-6 relative z-10">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Flagged Entries</p>
                    <p className="text-4xl font-bold text-orange-600 dark:text-orange-400">{flaggedJECount}</p>
                    <div className="h-1 w-16 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"></div>
                  </div>
                  <div className="rounded-2xl p-3 bg-gradient-to-br from-orange-500 to-amber-500 shadow-lg group-hover:scale-110 transition-transform duration-300 pulse-glow">
                    <AlertTriangle className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="group relative overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-500 hover-lift bg-gradient-to-br from-white via-red-50/30 to-pink-50/40 dark:from-gray-900 dark:via-red-950/30 dark:to-pink-950/40">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-red-500/10 to-transparent rounded-bl-full"></div>
              <CardContent className="pt-6 pb-6 relative z-10">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Critical Anomalies</p>
                    <p className="text-4xl font-bold text-red-600 dark:text-red-400">{criticalAnomaliesCount}</p>
                    <div className="h-1 w-16 bg-gradient-to-r from-red-500 to-pink-500 rounded-full"></div>
                  </div>
                  <div className="rounded-2xl p-3 bg-gradient-to-br from-red-500 to-pink-500 shadow-lg group-hover:scale-110 transition-transform duration-300 pulse-glow">
                    <AlertTriangle className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="group relative overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-500 hover-lift bg-gradient-to-br from-white via-green-50/30 to-emerald-50/40 dark:from-gray-900 dark:via-green-950/30 dark:to-emerald-950/40">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-green-500/10 to-transparent rounded-bl-full"></div>
              <CardContent className="pt-6 pb-6 relative z-10">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Ratios Calculated</p>
                    <p className="text-4xl font-bold text-green-600 dark:text-green-400">{ratiosArray.length}</p>
                    <div className="h-1 w-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"></div>
                  </div>
                  <div className="rounded-2xl p-3 bg-gradient-to-br from-green-500 to-emerald-500 shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <TrendingUp className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Premium Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 p-1.5 rounded-2xl border shadow-sm">
              <TabsTrigger
                value="je-testing"
                className="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
              >
                JE Testing
              </TabsTrigger>
              <TabsTrigger
                value="anomalies"
                className="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
              >
                Anomaly Detection
              </TabsTrigger>
              <TabsTrigger
                value="ratios"
                className="rounded-xl data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
              >
                Ratio Analysis
              </TabsTrigger>
            </TabsList>

            {/* JE Testing Tab */}
            <TabsContent value="je-testing" className="space-y-4">
              <Card className="border-none shadow-lg bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950">
                <CardHeader className="border-b bg-gradient-to-r from-purple-500/5 to-blue-500/5">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-xl flex items-center">
                        <BarChart3 className="mr-2 h-5 w-5 text-purple-600" />
                        Journal Entry Testing
                      </CardTitle>
                      <CardDescription>
                        AI-powered testing of journal entries for unusual patterns
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        onClick={() => runJETestingMutation.mutate()}
                        loading={runJETestingMutation.isPending}
                        className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 shadow-lg hover-lift"
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Run Testing
                      </Button>
                      <Button variant="outline" className="hover:bg-purple-50 hover:text-purple-600 hover:border-purple-300">
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
                        Click &quot;Run Testing&quot; to analyze journal entries
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
                  ) : anomaliesArray.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <AlertTriangle className="h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">No anomalies detected yet</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Click &quot;Run Detection&quot; to analyze for anomalies
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {anomaliesArray.map((anomaly: any, index: number) => (
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
                  ) : ratiosArray.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <TrendingUp className="h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">No ratios calculated yet</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Ratio analysis will appear here once data is processed
                      </p>
                    </div>
                  ) : (
                    <div className="grid gap-4 md:grid-cols-2">
                      {ratiosArray.map((ratio: any, index: number) => (
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
