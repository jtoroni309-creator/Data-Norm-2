import React from 'react';
import {
  FileText,
  CheckCircle,
  Clock,
  TrendingUp,
  AlertCircle,
  Calendar,
  Upload,
  Link as LinkIcon,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const stats = [
    {
      label: 'Documents Uploaded',
      value: '12 / 15',
      icon: FileText,
      color: 'blue',
      progress: 80,
    },
    {
      label: 'Integrations Connected',
      value: '3 / 5',
      icon: LinkIcon,
      color: 'green',
      progress: 60,
    },
    {
      label: 'Overall Progress',
      value: '70%',
      icon: TrendingUp,
      color: 'purple',
      progress: 70,
    },
    {
      label: 'Days Until Deadline',
      value: '14',
      icon: Calendar,
      color: 'orange',
      progress: 50,
    },
  ];

  const recentActivity = [
    {
      id: '1',
      action: 'Uploaded financial statements',
      time: '2 hours ago',
      icon: Upload,
      color: 'blue',
    },
    {
      id: '2',
      action: 'Connected QuickBooks integration',
      time: '5 hours ago',
      icon: CheckCircle,
      color: 'green',
    },
    {
      id: '3',
      action: 'Completed client questionnaire',
      time: '1 day ago',
      icon: CheckCircle,
      color: 'green',
    },
  ];

  const nextSteps = [
    {
      id: '1',
      title: 'Upload remaining tax documents',
      description: '3 documents pending',
      priority: 'high',
    },
    {
      id: '2',
      title: 'Connect ADP payroll integration',
      description: 'Automate payroll data sync',
      priority: 'medium',
    },
    {
      id: '3',
      title: 'Review and approve bank confirmations',
      description: '2 confirmations awaiting approval',
      priority: 'high',
    },
  ];

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    return 'bg-orange-500';
  };

  const getPriorityBadge = (priority: string) => {
    if (priority === 'high')
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertCircle className="w-3 h-3" />
          High Priority
        </span>
      );
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        <Clock className="w-3 h-3" />
        Medium Priority
        </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Engagement Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Track your audit engagement progress and complete required tasks
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <stat.icon className={`w-8 h-8 text-${stat.color}-600`} />
                <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-2">{stat.label}</h3>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getProgressColor(stat.progress)}`}
                  style={{ width: `${stat.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-4">
                  <div className={`p-2 rounded-lg bg-${activity.color}-100`}>
                    <activity.icon className={`w-5 h-5 text-${activity.color}-600`} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{activity.action}</p>
                    <p className="text-sm text-gray-600">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Next Steps</h2>
            <div className="space-y-4">
              {nextSteps.map((step) => (
                <div key={step.id} className="border-l-4 border-blue-500 pl-4 py-2">
                  <h3 className="font-medium text-gray-900 mb-1">{step.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                  {getPriorityBadge(step.priority)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Engagement Info */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Engagement Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Engagement Type</h3>
              <p className="text-lg font-semibold text-gray-900">Financial Statement Audit</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Fiscal Year End</h3>
              <p className="text-lg font-semibold text-gray-900">December 31, 2024</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">CPA Firm</h3>
              <p className="text-lg font-semibold text-gray-900">Anderson & Partners CPA</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
