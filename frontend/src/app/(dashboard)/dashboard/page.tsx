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
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Zap,
  Shield,
  Activity,
} from 'lucide-react';

export default function DashboardPage() {
  const stats = [
    {
      title: 'Active Engagements',
      value: '12',
      change: '+2 from last month',
      changePercent: '+18%',
      trend: 'up',
      icon: FolderOpen,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-gradient-to-br from-blue-500 to-blue-600',
      lightBg: 'bg-blue-50 dark:bg-blue-950/50',
    },
    {
      title: 'Pending Reviews',
      value: '8',
      change: '3 urgent',
      changePercent: '-5%',
      trend: 'neutral',
      icon: Clock,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-gradient-to-br from-orange-500 to-orange-600',
      lightBg: 'bg-orange-50 dark:bg-orange-950/50',
    },
    {
      title: 'Completed This Month',
      value: '24',
      change: '+12% from last month',
      changePercent: '+12%',
      trend: 'up',
      icon: CheckCircle2,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-gradient-to-br from-green-500 to-green-600',
      lightBg: 'bg-green-50 dark:bg-green-950/50',
    },
    {
      title: 'Issues Detected',
      value: '5',
      change: '2 critical',
      changePercent: '-60%',
      trend: 'down',
      icon: AlertTriangle,
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-gradient-to-br from-red-500 to-red-600',
      lightBg: 'bg-red-50 dark:bg-red-950/50',
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
    <div className="space-y-8 pb-8">
      {/* Page Header with Gradient */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-blue-600 to-blue-700 p-8 text-white shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"></div>
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-blue-500/20 blur-3xl"></div>

        <div className="relative z-10 flex items-center justify-between">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6" />
              <h1 className="text-4xl font-bold tracking-tight">Welcome Back</h1>
            </div>
            <p className="text-blue-100 text-lg">Here's what's happening with your audits today</p>
          </div>
          <Button size="lg" className="bg-white text-purple-600 hover:bg-blue-50 shadow-xl hover-lift">
            <FolderOpen className="mr-2 h-5 w-5" />
            New Engagement
          </Button>
        </div>
      </div>

      {/* Premium Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          const TrendIcon = stat.trend === 'up' ? ArrowUpRight : stat.trend === 'down' ? ArrowDownRight : Activity;

          return (
            <Card
              key={stat.title}
              className="group relative overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-500 hover-lift spotlight bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Animated background gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

              <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-4 relative z-10">
                <div className="space-y-1">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <div className="flex items-baseline space-x-2">
                    <div className="text-3xl font-bold tracking-tight">{stat.value}</div>
                    <div className={`flex items-center text-xs font-semibold ${
                      stat.trend === 'up' ? 'text-green-600' : stat.trend === 'down' ? 'text-red-600' : 'text-orange-600'
                    }`}>
                      <TrendIcon className="h-3 w-3 mr-0.5" />
                      {stat.changePercent}
                    </div>
                  </div>
                </div>
                <div className={`rounded-2xl p-3 ${stat.bgColor} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </CardHeader>

              <CardContent className="relative z-10">
                <p className="text-xs text-muted-foreground flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  {stat.change}
                </p>
              </CardContent>

              {/* Decorative corner element */}
              <div className="absolute bottom-0 right-0 w-20 h-20 bg-gradient-to-tl from-purple-500/10 to-transparent rounded-tl-full"></div>
            </Card>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-white to-purple-50/30 dark:from-gray-900 dark:to-purple-950/20">
          <CardHeader className="border-b bg-gradient-to-r from-purple-500/5 to-blue-500/5">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-xl flex items-center">
                  <Activity className="mr-2 h-5 w-5 text-purple-600" />
                  Recent Activity
                </CardTitle>
                <CardDescription>Your latest engagement updates</CardDescription>
              </div>
              <Badge className="bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                {recentActivity.length} Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 p-6">
            {recentActivity.map((activity, index) => (
              <div
                key={activity.id}
                className="group relative overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 p-4 hover:border-purple-300 dark:hover:border-purple-700 transition-all duration-300 hover-lift bg-white dark:bg-gray-950"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-blue-500/0 group-hover:from-purple-500/5 group-hover:to-blue-500/5 transition-all duration-300"></div>

                <div className="relative z-10 flex items-center justify-between">
                  <div className="space-y-2 flex-1">
                    <p className="font-semibold text-foreground group-hover:text-purple-600 transition-colors">
                      {activity.title}
                    </p>
                    <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <Users className="h-3.5 w-3.5 mr-1.5" />
                        <span>{activity.assignee}</span>
                      </div>
                      <span className="text-gray-300">•</span>
                      <div className="flex items-center">
                        <Clock className="h-3.5 w-3.5 mr-1.5" />
                        <span>{activity.dueDate}</span>
                      </div>
                    </div>
                  </div>
                  <Badge
                    className={`ml-4 shadow-sm ${
                      activity.status === 'Completed'
                        ? 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300'
                        : activity.status === 'In Progress'
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                        : 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300'
                    }`}
                  >
                    {activity.status}
                  </Badge>
                </div>
              </div>
            ))}
            <Button variant="outline" className="w-full mt-4 hover:bg-purple-50 hover:text-purple-600 hover:border-purple-300 transition-all">
              View All Engagements
              <ArrowUpRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-white to-blue-50/30 dark:from-gray-900 dark:to-blue-950/20">
          <CardHeader className="border-b bg-gradient-to-r from-blue-500/5 to-purple-500/5">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-xl flex items-center">
                  <Zap className="mr-2 h-5 w-5 text-blue-600" />
                  Quick Actions
                </CardTitle>
                <CardDescription>Common tasks and shortcuts</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 p-6">
            <Button
              variant="outline"
              className="w-full justify-start h-14 group hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-950/50 dark:hover:to-purple-950/50 hover:border-blue-300 transition-all hover-lift"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center">
                  <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 mr-3 group-hover:scale-110 transition-transform">
                    <BarChart3 className="h-5 w-5" />
                  </div>
                  <span className="font-medium">Run Analytics</span>
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-blue-600 transition-colors" />
              </div>
            </Button>

            <Button
              variant="outline"
              className="w-full justify-start h-14 group hover:bg-gradient-to-r hover:from-green-50 hover:to-blue-50 dark:hover:from-green-950/50 dark:hover:to-blue-950/50 hover:border-green-300 transition-all hover-lift"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center">
                  <div className="p-2 rounded-lg bg-green-100 dark:bg-green-950 text-green-600 dark:text-green-400 mr-3 group-hover:scale-110 transition-transform">
                    <CheckCircle2 className="h-5 w-5" />
                  </div>
                  <span className="font-medium">Quality Control Check</span>
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-green-600 transition-colors" />
              </div>
            </Button>

            <Button
              variant="outline"
              className="w-full justify-start h-14 group hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 dark:hover:from-purple-950/50 dark:hover:to-pink-950/50 hover:border-purple-300 transition-all hover-lift"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center">
                  <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-950 text-purple-600 dark:text-purple-400 mr-3 group-hover:scale-110 transition-transform">
                    <FileText className="h-5 w-5" />
                  </div>
                  <span className="font-medium">Generate Report</span>
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-purple-600 transition-colors" />
              </div>
            </Button>

            <Button
              variant="outline"
              className="w-full justify-start h-14 group hover:bg-gradient-to-r hover:from-orange-50 hover:to-red-50 dark:hover:from-orange-950/50 dark:hover:to-red-950/50 hover:border-orange-300 transition-all hover-lift"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center">
                  <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-950 text-orange-600 dark:text-orange-400 mr-3 group-hover:scale-110 transition-transform">
                    <TrendingUp className="h-5 w-5" />
                  </div>
                  <span className="font-medium">View Insights</span>
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-orange-600 transition-colors" />
              </div>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section - Premium Info Cards */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group bg-gradient-to-br from-white via-green-50/20 to-emerald-50/30 dark:from-gray-900 dark:via-green-950/20 dark:to-emerald-950/20">
          <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 rounded-full blur-3xl group-hover:bg-green-500/20 transition-all duration-500"></div>

          <CardHeader className="border-b bg-gradient-to-r from-green-500/5 to-emerald-500/5">
            <CardTitle className="text-lg flex items-center">
              <div className="p-2 rounded-lg bg-green-100 dark:bg-green-950 text-green-600 dark:text-green-400 mr-2">
                <TrendingUp className="h-5 w-5" />
              </div>
              Team Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 relative z-10">
            <div className="space-y-4">
              <div className="flex items-center justify-between group/item">
                <span className="text-sm text-muted-foreground">Completion Rate</span>
                <div className="flex items-center space-x-2">
                  <div className="h-1.5 w-24 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full w-[94%] bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"></div>
                  </div>
                  <span className="font-bold text-green-600 dark:text-green-400">94%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Avg. Review Time</span>
                <span className="font-bold text-foreground">2.3 days</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Quality Score</span>
                <div className="flex items-center space-x-2">
                  <div className="h-1.5 w-24 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full w-[98%] bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"></div>
                  </div>
                  <span className="font-bold text-green-600 dark:text-green-400">98/100</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group bg-gradient-to-br from-white via-blue-50/20 to-cyan-50/30 dark:from-gray-900 dark:via-blue-950/20 dark:to-cyan-950/20">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl group-hover:bg-blue-500/20 transition-all duration-500"></div>

          <CardHeader className="border-b bg-gradient-to-r from-blue-500/5 to-cyan-500/5">
            <CardTitle className="text-lg flex items-center">
              <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 mr-2">
                <Shield className="h-5 w-5" />
              </div>
              Compliance Status
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 relative z-10">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <span className="text-sm font-medium">PCAOB Standards</span>
                <div className="flex items-center space-x-1">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 border-none">
                    Compliant
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <span className="text-sm font-medium">AICPA Guidelines</span>
                <div className="flex items-center space-x-1">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 border-none">
                    Compliant
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <span className="text-sm font-medium">Internal Policies</span>
                <div className="flex items-center space-x-1">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 border-none">
                    Compliant
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group bg-gradient-to-br from-white via-purple-50/20 to-pink-50/30 dark:from-gray-900 dark:via-purple-950/20 dark:to-pink-950/20">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl group-hover:bg-purple-500/20 transition-all duration-500"></div>

          <CardHeader className="border-b bg-gradient-to-r from-purple-500/5 to-pink-500/5">
            <CardTitle className="text-lg flex items-center">
              <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-950 text-purple-600 dark:text-purple-400 mr-2">
                <Activity className="h-5 w-5" />
              </div>
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 relative z-10">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span className="text-sm font-medium">API Status</span>
                </div>
                <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 border-none">
                  Online
                </Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span className="text-sm font-medium">Database</span>
                </div>
                <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 border-none">
                  Healthy
                </Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span className="text-sm font-medium">ML Models</span>
                </div>
                <Badge className="bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 border-none">
                  Active
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
