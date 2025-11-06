'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  FolderOpen,
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Clock,
  Users,
  FileText,
} from 'lucide-react';

export default function DashboardPage() {
  const stats = [
    {
      title: 'Active Engagements',
      value: '12',
      change: '+2 from last month',
      trend: 'up',
      icon: FolderOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      title: 'Pending Reviews',
      value: '8',
      change: '3 urgent',
      trend: 'neutral',
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
    },
    {
      title: 'Completed This Month',
      value: '24',
      change: '+12% from last month',
      trend: 'up',
      icon: CheckCircle2,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      title: 'Issues Detected',
      value: '5',
      change: '2 critical',
      trend: 'down',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/20',
    },
  ];

  const recentActivity = [
    {
      id: 1,
      title: 'ABC Corp - Q4 2024 Audit',
      status: 'In Progress',
      assignee: 'John Smith',
      dueDate: '2024-12-15',
      type: 'audit',
    },
    {
      id: 2,
      title: 'XYZ Inc - Financial Review',
      status: 'Pending Review',
      assignee: 'Sarah Johnson',
      dueDate: '2024-12-10',
      type: 'review',
    },
    {
      id: 3,
      title: 'Tech Solutions - Compliance Check',
      status: 'Completed',
      assignee: 'Mike Davis',
      dueDate: '2024-11-28',
      type: 'compliance',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your audit activities</p>
        </div>
        <Button size="lg">
          <FolderOpen className="mr-2 h-4 w-4" />
          New Engagement
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className="hover:shadow-elevation-2 transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <div className={`rounded-full p-2 ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.change}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest engagement updates</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between rounded-lg border p-4">
                <div className="space-y-1">
                  <p className="font-medium">{activity.title}</p>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <Users className="h-3 w-3" />
                    <span>{activity.assignee}</span>
                    <span>•</span>
                    <span>Due: {activity.dueDate}</span>
                  </div>
                </div>
                <Badge
                  variant={
                    activity.status === 'Completed'
                      ? 'success'
                      : activity.status === 'In Progress'
                      ? 'default'
                      : 'warning'
                  }
                >
                  {activity.status}
                </Badge>
              </div>
            ))}
            <Button variant="outline" className="w-full">
              View All Engagements
            </Button>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start" size="lg">
              <BarChart3 className="mr-2 h-4 w-4" />
              Run Analytics
            </Button>
            <Button variant="outline" className="w-full justify-start" size="lg">
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Quality Control Check
            </Button>
            <Button variant="outline" className="w-full justify-start" size="lg">
              <FileText className="mr-2 h-4 w-4" />
              Generate Report
            </Button>
            <Button variant="outline" className="w-full justify-start" size="lg">
              <TrendingUp className="mr-2 h-4 w-4" />
              View Insights
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Team Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Completion Rate</span>
                <span className="font-semibold">94%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Avg. Review Time</span>
                <span className="font-semibold">2.3 days</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Quality Score</span>
                <span className="font-semibold">98/100</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Compliance Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">PCAOB Standards</span>
                <Badge variant="success">Compliant</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">AICPA Guidelines</span>
                <Badge variant="success">Compliant</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Internal Policies</span>
                <Badge variant="success">Compliant</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">API Status</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Database</span>
                <Badge variant="success">Healthy</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">ML Models</span>
                <Badge variant="success">Active</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
