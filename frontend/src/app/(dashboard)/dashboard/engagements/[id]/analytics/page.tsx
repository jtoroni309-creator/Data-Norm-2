'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
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
  Brain,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Lightbulb,
  FileText,
  DollarSign,
  Calendar,
  Activity,
  Target,
  Zap,
} from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '@/lib/api';
import { aiService, AIAnomalyInsight } from '@/lib/ai-service';
import { AIAssistant } from '@/components/ai/ai-assistant';
import { cn } from '@/lib/utils';

interface JETestResult {
  test_type: string;
  entry_number: string;
  entry_date: string;
  amount: number;
  reason: string;
  score: number;
}

interface Anomaly {
  id: string;
  account_name: string;
  anomaly_type: string;
  severity: string;
  score: number;
  evidence: any;
  status: string;
}

export default function AnalyticsDashboardPage({ params }: { params: { id: string } }) {
  const [aiInsights, setAiInsights] = useState<AIAnomalyInsight[]>([]);
  const [isLoadingAI, setIsLoadingAI] = useState(false);

  // Fetch JE test results
  const { data: jeResults = [], isLoading: isLoadingJE } = useQuery({
    queryKey: ['je-tests', params.id],
    queryFn: () => api.analytics.jeTests(params.id),
  });

  // Fetch anomalies
  const { data: anomaliesData, isLoading: isLoadingAnomalies } = useQuery({
    queryKey: ['anomalies', params.id],
    queryFn: () => api.analytics.anomalies.list(params.id),
  });

  const anomalies = anomaliesData?.anomalies || [];

  // Get AI insights for anomalies
  useEffect(() => {
    if (anomalies.length > 0 && aiInsights.length === 0) {
      loadAIInsights();
    }
  }, [anomalies]);

  const loadAIInsights = async () => {
    setIsLoadingAI(true);
    try {
      const insights = await aiService.analyzeAnomalies(
        anomalies.map((a: Anomaly) => ({
          account_name: a.account_name,
          anomaly_type: a.anomaly_type,
          score: a.score,
          evidence: a.evidence,
        }))
      );
      setAiInsights(insights);
    } catch (error) {
      console.error('Failed to load AI insights:', error);
    } finally {
      setIsLoadingAI(false);
    }
  };

  // Calculate statistics
  const jeStats = {
    total: jeResults.length,
    round_dollar: jeResults.filter((r: JETestResult) => r.test_type === 'round_dollar').length,
    weekend: jeResults.filter((r: JETestResult) => r.test_type === 'weekend').length,
    period_end: jeResults.filter((r: JETestResult) => r.test_type === 'period_end').length,
  };

  const anomalyStats = {
    total: anomalies.length,
    critical: anomalies.filter((a: Anomaly) => a.severity === 'critical').length,
    high: anomalies.filter((a: Anomaly) => a.severity === 'high').length,
    medium: anomalies.filter((a: Anomaly) => a.severity === 'medium').length,
    resolved: anomalies.filter((a: Anomaly) => a.status === 'resolved').length,
  };

  const jeChartData = [
    { name: 'Round Dollar', value: jeStats.round_dollar, color: '#3b82f6' },
    { name: 'Weekend', value: jeStats.weekend, color: '#f59e0b' },
    { name: 'Period End', value: jeStats.period_end, color: '#ef4444' },
  ];

  const anomalyChartData = [
    { name: 'Critical', value: anomalyStats.critical, color: '#dc2626' },
    { name: 'High', value: anomalyStats.high, color: '#f97316' },
    { name: 'Medium', value: anomalyStats.medium, color: '#eab308' },
  ];

  const stats = [
    {
      label: 'JE Tests Flagged',
      value: jeStats.total,
      icon: FileText,
      color: 'text-blue-600 bg-blue-100',
      trend: '+12%',
    },
    {
      label: 'ML Anomalies',
      value: anomalyStats.total,
      icon: Brain,
      color: 'text-purple-600 bg-purple-100',
      trend: '+8%',
    },
    {
      label: 'Critical Issues',
      value: anomalyStats.critical,
      icon: AlertTriangle,
      color: 'text-red-600 bg-red-100',
      trend: '-5%',
    },
    {
      label: 'AI Insights',
      value: aiInsights.length,
      icon: Lightbulb,
      color: 'text-yellow-600 bg-yellow-100',
      trend: 'New',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'high':
        return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      default:
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
    }
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold tracking-tight">AI Analytics Dashboard</h1>
            <Badge
              variant="outline"
              className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 text-blue-600"
            >
              <Sparkles className="mr-1 h-3 w-3" />
              ML-Powered
            </Badge>
          </div>
          <p className="mt-2 text-muted-foreground">
            Advanced analytics with machine learning anomaly detection
          </p>
        </div>
        <Button
          onClick={loadAIInsights}
          disabled={isLoadingAI}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          {isLoadingAI ? (
            <>
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Generating Insights...
            </>
          ) : (
            <>
              <Brain className="mr-2 h-4 w-4" />
              Refresh AI Insights
            </>
          )}
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                    <div className="mt-2 flex items-baseline space-x-2">
                      <p className="text-3xl font-bold">{stat.value}</p>
                      <Badge variant="outline" className="text-xs">
                        {stat.trend}
                      </Badge>
                    </div>
                  </div>
                  <div className={`rounded-lg p-2 ${stat.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Journal Entry Tests</CardTitle>
            <CardDescription>Distribution by test type</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={jeChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {jeChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Anomaly Severity</CardTitle>
            <CardDescription>ML-detected anomalies by severity</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={anomalyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8">
                  {anomalyChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      {aiInsights.length > 0 && (
        <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50/50 to-blue-50/50 dark:from-purple-950/20 dark:to-blue-950/20">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-6 w-6 text-purple-600" />
              <CardTitle>AI-Generated Insights</CardTitle>
            </div>
            <CardDescription>
              Machine learning analysis of detected anomalies
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {aiInsights.map((insight, index) => (
              <div
                key={index}
                className="rounded-lg border bg-white p-4 dark:bg-gray-900"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center space-x-2">
                      <Badge className={getSeverityColor(insight.priority)}>
                        {insight.priority.toUpperCase()}
                      </Badge>
                      <h4 className="font-semibold">{insight.summary}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      <span className="font-medium">Likely Cause:</span> {insight.likely_cause}
                    </p>
                    <div className="space-y-1">
                      <p className="text-sm font-medium">Suggested Procedures:</p>
                      <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                        {insight.suggested_procedures.map((procedure, i) => (
                          <li key={i}>{procedure}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <Sparkles className="ml-4 h-5 w-5 flex-shrink-0 text-purple-600" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Detailed Tabs */}
      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="je-tests">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="je-tests">
                <FileText className="mr-2 h-4 w-4" />
                JE Tests ({jeStats.total})
              </TabsTrigger>
              <TabsTrigger value="anomalies">
                <Brain className="mr-2 h-4 w-4" />
                ML Anomalies ({anomalyStats.total})
              </TabsTrigger>
            </TabsList>

            {/* JE Tests Table */}
            <TabsContent value="je-tests" className="space-y-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Entry Number</TableHead>
                      <TableHead>Test Type</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Risk Score</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {jeResults.map((result: JETestResult, index: number) => (
                      <TableRow key={index}>
                        <TableCell className="font-mono">{result.entry_number}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{result.test_type}</Badge>
                        </TableCell>
                        <TableCell>{new Date(result.entry_date).toLocaleDateString()}</TableCell>
                        <TableCell className="text-right font-mono">
                          ${result.amount.toLocaleString()}
                        </TableCell>
                        <TableCell className="max-w-md text-sm text-muted-foreground">
                          {result.reason}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <div className="h-2 w-24 overflow-hidden rounded-full bg-gray-200">
                              <div
                                className={cn(
                                  'h-full',
                                  result.score > 0.7
                                    ? 'bg-red-500'
                                    : result.score > 0.5
                                      ? 'bg-yellow-500'
                                      : 'bg-green-500'
                                )}
                                style={{ width: `${result.score * 100}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium">
                              {(result.score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>

            {/* Anomalies Table */}
            <TabsContent value="anomalies" className="space-y-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Account</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Severity</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {anomalies.map((anomaly: Anomaly) => (
                      <TableRow key={anomaly.id}>
                        <TableCell className="font-medium">
                          {anomaly.account_name}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{anomaly.anomaly_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={getSeverityColor(anomaly.severity)}>
                            {anomaly.severity}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono">
                          {anomaly.score.toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              anomaly.status === 'resolved' ? 'outline' : 'default'
                            }
                          >
                            {anomaly.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            Investigate
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* AI Assistant */}
      <AIAssistant
        context={{
          engagement_id: params.id,
          current_page: 'analytics',
          user_role: 'auditor',
        }}
      />
    </div>
  );
}
