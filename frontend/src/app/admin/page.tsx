'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Users,
  CreditCard,
  TrendingUp,
  TrendingDown,
  DollarSign,
  UserCheck,
  UserX,
  Activity,
} from 'lucide-react';
import { api } from '@/lib/api';
import { formatCurrency, formatNumber, formatPercentage } from '@/lib/utils';

export default function AdminDashboardPage() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['admin-metrics'],
    queryFn: api.admin.metrics.overview,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const mockMetrics = metrics || {
    total_customers: 127,
    active_customers: 118,
    trial_customers: 9,
    churned_this_month: 3,
    revenue_mrr: 47500,
    revenue_arr: 570000,
    average_seats_per_customer: 8.4,
    total_seats: 1067,
    seats_utilized: 892,
  };

  const stats = [
    {
      title: 'Total Customers',
      value: mockMetrics.total_customers,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
      change: '+12%',
      trend: 'up',
    },
    {
      title: 'Active Customers',
      value: mockMetrics.active_customers,
      icon: UserCheck,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      change: '+5%',
      trend: 'up',
    },
    {
      title: 'Trial Customers',
      value: mockMetrics.trial_customers,
      icon: Activity,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
      change: '+3',
      trend: 'up',
    },
    {
      title: 'Churned (This Month)',
      value: mockMetrics.churned_this_month,
      icon: UserX,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/20',
      change: '-2',
      trend: 'down',
    },
  ];

  const revenueStats = [
    {
      title: 'Monthly Recurring Revenue',
      value: formatCurrency(mockMetrics.revenue_mrr),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      change: '+18%',
      trend: 'up',
    },
    {
      title: 'Annual Recurring Revenue',
      value: formatCurrency(mockMetrics.revenue_arr),
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
      change: '+22%',
      trend: 'up',
    },
    {
      title: 'Total Seats',
      value: mockMetrics.total_seats,
      icon: CreditCard,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
      change: formatPercentage(mockMetrics.seats_utilized / mockMetrics.total_seats),
      subtitle: `${mockMetrics.seats_utilized} utilized`,
    },
    {
      title: 'Avg Seats per Customer',
      value: mockMetrics.average_seats_per_customer.toFixed(1),
      icon: Users,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/20',
      change: '+0.8',
      trend: 'up',
    },
  ];

  const recentCustomers = [
    { name: 'Acme Corp', plan: 'Enterprise', mrr: '$2,400', status: 'active', date: '2024-11-05' },
    { name: 'TechStart Inc', plan: 'Professional', mrr: '$800', status: 'trial', date: '2024-11-04' },
    { name: 'Global Audit', plan: 'Enterprise', mrr: '$3,200', status: 'active', date: '2024-11-03' },
    { name: 'CPA Partners', plan: 'Starter', mrr: '$200', status: 'active', date: '2024-11-02' },
    { name: 'Finance Pro', plan: 'Professional', mrr: '$1,200', status: 'active', date: '2024-11-01' },
  ];

  const recentActivity = [
    { action: 'New customer signup', customer: 'Acme Corp', time: '5 minutes ago', type: 'success' },
    { action: 'License renewed', customer: 'Global Audit', time: '2 hours ago', type: 'success' },
    { action: 'Support ticket created', customer: 'TechStart Inc', time: '3 hours ago', type: 'warning' },
    { action: 'Customer suspended', customer: 'Old Client LLC', time: '1 day ago', type: 'error' },
    { action: 'Invoice paid', customer: 'CPA Partners', time: '1 day ago', type: 'success' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of customer metrics, revenue, and platform health
        </p>
      </div>

      {/* Customer Stats */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">Customer Metrics</h2>
        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                    <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                    <div className="mt-1 flex items-center text-sm">
                      {stat.trend === 'up' ? (
                        <TrendingUp className="mr-1 h-3 w-3 text-green-600" />
                      ) : (
                        <TrendingDown className="mr-1 h-3 w-3 text-red-600" />
                      )}
                      <span
                        className={stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}
                      >
                        {stat.change}
                      </span>
                      <span className="ml-1 text-muted-foreground">vs last month</span>
                    </div>
                  </div>
                  <div className={`rounded-full p-3 ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Revenue Stats */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">Revenue Metrics</h2>
        <div className="grid gap-4 md:grid-cols-4">
          {revenueStats.map((stat) => (
            <Card key={stat.title}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                    <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {stat.subtitle || (
                        <span className={stat.trend === 'up' ? 'text-green-600' : ''}>
                          {stat.change} {stat.trend === 'up' ? '↑' : ''}
                        </span>
                      )}
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
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Customers */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Customers</CardTitle>
            <CardDescription>Latest customer signups and conversions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentCustomers.map((customer, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{customer.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {customer.plan} • {customer.date}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{customer.mrr}</p>
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        customer.status === 'active'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/20'
                          : 'bg-orange-100 text-orange-700 dark:bg-orange-900/20'
                      }`}
                    >
                      {customer.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest platform events and actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div
                    className={`mt-1 h-2 w-2 rounded-full ${
                      activity.type === 'success'
                        ? 'bg-green-500'
                        : activity.type === 'warning'
                        ? 'bg-orange-500'
                        : 'bg-red-500'
                    }`}
                  />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-sm text-muted-foreground">
                      {activity.customer} • {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
