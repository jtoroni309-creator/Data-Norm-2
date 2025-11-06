'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  BarChart3,
  TrendingUp,
  Download,
  Activity,
  Database,
  Zap,
  Users,
  FileText,
} from 'lucide-react';
import { api } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

export default function AdminAnalyticsPage() {
  const { data: usage, isLoading } = useQuery({
    queryKey: ['admin-usage'],
    queryFn: () => api.admin.usage.getAll(),
  });

  const mockStats = [
    {
      title: 'Total Engagements',
      value: '4,329',
      change: '+12%',
      trend: 'up',
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      title: 'Total Users',
      value: '1,067',
      change: '+8%',
      trend: 'up',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      title: 'Analytics Runs',
      value: '23,456',
      change: '+18%',
      trend: 'up',
      icon: BarChart3,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    },
    {
      title: 'QC Checks',
      value: '15,892',
      change: '+15%',
      trend: 'up',
      icon: Activity,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
    },
    {
      title: 'Normalize Operations',
      value: '34,221',
      change: '+22%',
      trend: 'up',
      icon: Zap,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/20',
    },
    {
      title: 'Storage Used',
      value: '2.3 TB',
      change: '+5%',
      trend: 'up',
      icon: Database,
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-100 dark:bg-cyan-900/20',
    },
    {
      title: 'API Calls',
      value: '342K',
      change: '+28%',
      trend: 'up',
      icon: TrendingUp,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100 dark:bg-pink-900/20',
    },
    {
      title: 'Avg Response Time',
      value: '124ms',
      change: '-8%',
      trend: 'down',
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
  ];

  const topCustomers = [
    { name: 'Acme Corp', engagements: 342, analytics: 1247, usage: 42.3 },
    { name: 'Global Audit', engagements: 298, analytics: 1089, usage: 38.7 },
    { name: 'Finance Pro', engagements: 256, analytics: 934, usage: 35.2 },
    { name: 'CPA Partners', engagements: 223, analytics: 812, usage: 31.8 },
    { name: 'TechStart Inc', engagements: 189, analytics: 687, usage: 28.4 },
  ];

  const featureUsage = [
    { name: 'Analytics (JE Testing)', usage: 23456, percentage: 92 },
    { name: 'Normalize (Mapping)', usage: 34221, percentage: 88 },
    { name: 'Quality Control', usage: 15892, percentage: 75 },
    { name: 'API Access', usage: 8934, percentage: 65 },
    { name: 'Anomaly Detection', usage: 12456, percentage: 82 },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Usage & Analytics</h1>
          <p className="text-muted-foreground">
            Platform usage metrics and customer analytics
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        {mockStats.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                  <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                  <p className="mt-1 text-sm">
                    <span
                      className={
                        stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      }
                    >
                      {stat.change}
                    </span>
                    <span className="text-muted-foreground ml-1">vs last month</span>
                  </p>
                </div>
                <div className={`rounded-full p-3 ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Top Customers by Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Top Customers by Usage</CardTitle>
            <CardDescription>Highest resource consumption this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topCustomers.map((customer, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{customer.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {customer.engagements} engagements
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{customer.analytics.toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">analytics runs</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Feature Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Feature Adoption</CardTitle>
            <CardDescription>Usage rates across platform features</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {featureUsage.map((feature, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium">{feature.name}</p>
                    <div className="text-right">
                      <p className="text-sm font-medium">{feature.percentage}%</p>
                      <p className="text-xs text-muted-foreground">
                        {feature.usage.toLocaleString()} uses
                      </p>
                    </div>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${feature.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Trends */}
      <Card>
        <CardHeader>
          <CardTitle>Usage Trends</CardTitle>
          <CardDescription>Monthly platform usage over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-end justify-around space-x-2">
            {[65, 72, 68, 78, 85, 92, 88, 95, 100, 98, 105, 112].map((height, index) => (
              <div key={index} className="flex flex-1 flex-col items-center">
                <div
                  className="w-full rounded-t bg-primary transition-all hover:bg-primary/80"
                  style={{ height: `${height}%` }}
                />
                <p className="mt-2 text-xs text-muted-foreground">
                  {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][index]}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Usage by Region/Industry */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Usage by Industry</CardTitle>
            <CardDescription>Platform adoption across industries</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { industry: 'Accounting & Audit', percentage: 45 },
                { industry: 'Financial Services', percentage: 28 },
                { industry: 'Technology', percentage: 15 },
                { industry: 'Healthcare', percentage: 8 },
                { industry: 'Other', percentage: 4 },
              ].map((item, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium">{item.industry}</p>
                    <p className="text-sm text-muted-foreground">{item.percentage}%</p>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
            <CardDescription>System health and performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">API Uptime</p>
                  <p className="text-sm font-medium text-green-600">99.97%</p>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-green-600" style={{ width: '99.97%' }} />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Average Response Time</p>
                  <p className="text-sm font-medium">124ms</p>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-blue-600" style={{ width: '85%' }} />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Error Rate</p>
                  <p className="text-sm font-medium text-green-600">0.03%</p>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-red-600" style={{ width: '3%' }} />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Customer Satisfaction</p>
                  <p className="text-sm font-medium text-green-600">4.8/5.0</p>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-green-600" style={{ width: '96%' }} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
