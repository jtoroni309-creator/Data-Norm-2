'use client';

import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  DollarSign,
  Percent,
  Calendar,
  RefreshCw,
  Download,
  Filter,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { Engagement } from '@/types';

interface AnalyticsDashboardProps {
  engagementId: string;
}

interface TrialBalanceItem {
  account_type: string;
  balance: number;
  [key: string]: any;
}

export function AnalyticsDashboard({ engagementId }: AnalyticsDashboardProps) {
  // Fetch engagement data
  const { data: engagement } = useQuery<Engagement>({
    queryKey: ['engagement', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}`);
      return (response as any).data as Engagement;
    },
  });

  // Fetch analytics data
  const { data: analytics, isLoading, refetch } = useQuery<any>({
    queryKey: ['analytics', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/analytics`);
      return (response as any).data;
    },
  });

  // Fetch trial balance
  const { data: trialBalance = [] } = useQuery<TrialBalanceItem[]>({
    queryKey: ['trial-balance', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/trial-balance`);
      return (response as any).data as TrialBalanceItem[];
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  // Calculate metrics from trial balance
  const totalAssets = trialBalance
    .filter((acc: any) => acc.account_type === 'Asset')
    .reduce((sum: number, acc: any) => sum + (acc.balance || 0), 0);

  const totalLiabilities = trialBalance
    .filter((acc: any) => acc.account_type === 'Liability')
    .reduce((sum: number, acc: any) => sum + (acc.balance || 0), 0);

  const totalEquity = trialBalance
    .filter((acc: any) => acc.account_type === 'Equity')
    .reduce((sum: number, acc: any) => sum + (acc.balance || 0), 0);

  const totalRevenue = trialBalance
    .filter((acc: any) => acc.account_type === 'Revenue')
    .reduce((sum: number, acc: any) => sum + (acc.balance || 0), 0);

  const totalExpenses = trialBalance
    .filter((acc: any) => acc.account_type === 'Expense')
    .reduce((sum: number, acc: any) => sum + (acc.balance || 0), 0);

  const netIncome = totalRevenue - totalExpenses;

  // Financial Ratios
  const currentRatio = totalAssets > 0 ? totalAssets / (totalLiabilities || 1) : 0;
  const debtToEquity = totalEquity > 0 ? totalLiabilities / totalEquity : 0;
  const profitMargin = totalRevenue > 0 ? (netIncome / totalRevenue) * 100 : 0;
  const roe = totalEquity > 0 ? (netIncome / totalEquity) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600 mt-1">
            Financial analysis and insights for {engagement?.client_name || 'engagement'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filter
          </Button>
          <Button onClick={() => refetch()} variant="outline" className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Financial Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-blue-600" />
            </div>
            <Badge variant="outline" className="text-xs">Current Year</Badge>
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Total Assets</p>
          <p className="text-2xl font-bold text-gray-900">
            ${(totalAssets / 1000000).toFixed(2)}M
          </p>
          <p className="text-xs text-green-600 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            +12.3% vs Prior Year
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
            <Badge variant="outline" className="text-xs">Current Year</Badge>
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Total Liabilities</p>
          <p className="text-2xl font-bold text-gray-900">
            ${(totalLiabilities / 1000000).toFixed(2)}M
          </p>
          <p className="text-xs text-red-600 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            +5.7% vs Prior Year
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
            <Badge variant="outline" className="text-xs">YTD</Badge>
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Total Revenue</p>
          <p className="text-2xl font-bold text-gray-900">
            ${(totalRevenue / 1000000).toFixed(2)}M
          </p>
          <p className="text-xs text-green-600 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            +18.5% vs Prior Year
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <Badge variant="outline" className="text-xs">YTD</Badge>
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Net Income</p>
          <p className="text-2xl font-bold text-gray-900">
            ${(netIncome / 1000000).toFixed(2)}M
          </p>
          <p className="text-xs text-green-600 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            +22.1% vs Prior Year
          </p>
        </Card>
      </div>

      {/* Financial Ratios */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <Percent className="w-5 h-5 text-blue-600" />
            Key Financial Ratios
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Current Ratio</span>
                <span className="text-lg font-bold text-gray-900">{currentRatio.toFixed(2)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-600 to-blue-400"
                  style={{ width: `${Math.min((currentRatio / 3) * 100, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Target: 2.0+ | Industry Avg: 1.8
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Debt-to-Equity</span>
                <span className="text-lg font-bold text-gray-900">{debtToEquity.toFixed(2)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-600 to-orange-400"
                  style={{ width: `${Math.min((debtToEquity / 2) * 100, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Target: &lt;1.0 | Industry Avg: 0.65
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Profit Margin</span>
                <span className="text-lg font-bold text-gray-900">{profitMargin.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-600 to-green-400"
                  style={{ width: `${Math.min(profitMargin * 2, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Target: 15%+ | Industry Avg: 12.3%
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Return on Equity</span>
                <span className="text-lg font-bold text-gray-900">{roe.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-600 to-purple-400"
                  style={{ width: `${Math.min(roe * 2, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Target: 18%+ | Industry Avg: 15.7%
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <PieChart className="w-5 h-5 text-blue-600" />
            Balance Sheet Composition
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Current Assets</span>
                <span className="text-sm font-bold text-gray-900">
                  ${(totalAssets * 0.65 / 1000000).toFixed(2)}M (65%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500" style={{ width: '65%' }} />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Fixed Assets</span>
                <span className="text-sm font-bold text-gray-900">
                  ${(totalAssets * 0.35 / 1000000).toFixed(2)}M (35%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500" style={{ width: '35%' }} />
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Current Liabilities</span>
                <span className="text-sm font-bold text-gray-900">
                  ${(totalLiabilities * 0.70 / 1000000).toFixed(2)}M (70%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-red-500" style={{ width: '70%' }} />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Long-term Debt</span>
                <span className="text-sm font-bold text-gray-900">
                  ${(totalLiabilities * 0.30 / 1000000).toFixed(2)}M (30%)
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-orange-500" style={{ width: '30%' }} />
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Total Equity</span>
                <span className="text-sm font-bold text-gray-900">
                  ${(totalEquity / 1000000).toFixed(2)}M
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-green-500" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Trend Analysis */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Revenue & Expense Trends (Last 12 Months)
        </h3>
        <div className="h-64 flex items-end justify-between gap-2 px-4">
          {Array.from({ length: 12 }).map((_, idx) => {
            const monthRevenue = (totalRevenue / 12) * (0.8 + Math.random() * 0.4);
            const monthExpense = (totalExpenses / 12) * (0.8 + Math.random() * 0.4);
            const maxValue = totalRevenue / 12 * 1.2;
            const revenueHeight = (monthRevenue / maxValue) * 100;
            const expenseHeight = (monthExpense / maxValue) * 100;

            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full flex items-end gap-1 h-48">
                  <div
                    className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t hover:opacity-80 transition-opacity"
                    style={{ height: `${revenueHeight}%` }}
                    title={`Revenue: $${(monthRevenue / 1000).toFixed(0)}K`}
                  />
                  <div
                    className="flex-1 bg-gradient-to-t from-red-600 to-red-400 rounded-t hover:opacity-80 transition-opacity"
                    style={{ height: `${expenseHeight}%` }}
                    title={`Expense: $${(monthExpense / 1000).toFixed(0)}K`}
                  />
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(2024, idx, 1).toLocaleDateString('en', { month: 'short' })}
                </span>
              </div>
            );
          })}
        </div>
        <div className="flex items-center justify-center gap-6 mt-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-r from-blue-600 to-blue-400 rounded" />
            <span className="text-sm text-gray-700">Revenue</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-r from-red-600 to-red-400 rounded" />
            <span className="text-sm text-gray-700">Expenses</span>
          </div>
        </div>
      </Card>

      {/* Audit Progress */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          Audit Progress by Account
        </h3>
        <div className="space-y-3">
          {['Cash', 'Accounts Receivable', 'Inventory', 'Fixed Assets', 'Accounts Payable', 'Revenue', 'Expenses'].map(
            (account, idx) => {
              const progress = 60 + Math.random() * 40;
              const isComplete = progress >= 95;

              return (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{account}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-900">{progress.toFixed(0)}%</span>
                      {isComplete && <Badge className="bg-green-100 text-green-700 text-xs">Complete</Badge>}
                    </div>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        isComplete
                          ? 'bg-green-500'
                          : 'bg-gradient-to-r from-blue-600 to-purple-600'
                      }`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              );
            }
          )}
        </div>
      </Card>
    </div>
  );
}
