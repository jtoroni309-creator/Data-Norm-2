import React from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Ticket,
  Activity,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
} from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface StatCardProps {
  title: string;
  value: string | number;
  change: string;
  icon: React.ReactNode;
  trend: 'up' | 'down';
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, icon, trend, color }) => {
  return (
    <Card variant="elevated">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-600">{title}</p>
          <h3 className="text-3xl font-bold text-neutral-900 mt-2">{value}</h3>
          <div className="flex items-center gap-2 mt-3">
            <Badge variant={trend === 'up' ? 'success' : 'error'} size="small">
              {trend === 'up' ? '↑' : '↓'} {change}
            </Badge>
            <span className="text-xs text-neutral-600">vs last month</span>
          </div>
        </div>
        <div className={`w-14 h-14 rounded-2xl ${color} flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </Card>
  );
};

export const Dashboard: React.FC = () => {
  const userGrowthData = [
    { month: 'Jan', users: 450 },
    { month: 'Feb', users: 680 },
    { month: 'Mar', users: 820 },
    { month: 'Apr', users: 1240 },
    { month: 'May', users: 1680 },
    { month: 'Jun', users: 2140 },
  ];

  const ticketData = [
    { status: 'Open', count: 234, color: '#1a91eb' },
    { status: 'In Progress', count: 156, color: '#8764ff' },
    { status: 'Resolved', count: 421, color: '#4caf50' },
    { status: 'Closed', count: 89, color: '#9e9e9e' },
  ];

  const revenueData = [
    { month: 'Jan', revenue: 45000, expenses: 32000 },
    { month: 'Feb', revenue: 52000, expenses: 34000 },
    { month: 'Mar', revenue: 61000, expenses: 38000 },
    { month: 'Apr', revenue: 73000, expenses: 41000 },
    { month: 'May', revenue: 82000, expenses: 45000 },
    { month: 'Jun', revenue: 94000, expenses: 48000 },
  ];

  const recentActivity = [
    {
      id: 1,
      user: 'John Doe',
      action: 'Created new ticket',
      time: '5 minutes ago',
      type: 'ticket',
    },
    {
      id: 2,
      user: 'Jane Smith',
      action: 'Resolved ticket #1234',
      time: '15 minutes ago',
      type: 'resolve',
    },
    {
      id: 3,
      user: 'Bob Johnson',
      action: 'Registered as new user',
      time: '1 hour ago',
      type: 'user',
    },
    {
      id: 4,
      user: 'Alice Williams',
      action: 'Updated system settings',
      time: '2 hours ago',
      type: 'settings',
    },
    {
      id: 5,
      user: 'Charlie Brown',
      action: 'Generated analytics report',
      time: '3 hours ago',
      type: 'report',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Dashboard</h1>
          <p className="text-neutral-600 mt-1">Welcome back! Here's what's happening today.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outlined" icon={<Activity size={18} />}>
            View Reports
          </Button>
          <Button variant="filled" icon={<TrendingUp size={18} />}>
            Analytics
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <StatCard
            title="Total Users"
            value="2,847"
            change="12.5%"
            trend="up"
            icon={<Users size={24} className="text-primary-600" />}
            color="bg-primary-100"
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <StatCard
            title="Active Tickets"
            value="234"
            change="8.3%"
            trend="down"
            icon={<Ticket size={24} className="text-warning-600" />}
            color="bg-warning-100"
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <StatCard
            title="Resolution Rate"
            value="94.2%"
            change="5.1%"
            trend="up"
            icon={<CheckCircle size={24} className="text-success-600" />}
            color="bg-success-100"
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <StatCard
            title="Revenue"
            value="$94.2K"
            change="18.7%"
            trend="up"
            icon={<DollarSign size={24} className="text-tertiary-600" />}
            color="bg-tertiary-100"
          />
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* User Growth Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card variant="elevated">
            <CardHeader title="User Growth" subtitle="Last 6 months" />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={userGrowthData}>
                  <defs>
                    <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#1a91eb" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#1a91eb" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis dataKey="month" stroke="#757575" />
                  <YAxis stroke="#757575" />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="users"
                    stroke="#1a91eb"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorUsers)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Revenue Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card variant="elevated">
            <CardHeader title="Revenue vs Expenses" subtitle="Monthly comparison" />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis dataKey="month" stroke="#757575" />
                  <YAxis stroke="#757575" />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="revenue" fill="#1a91eb" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="expenses" fill="#8764ff" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Ticket Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card variant="elevated">
            <CardHeader title="Ticket Distribution" subtitle="By status" />
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={ticketData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {ticketData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="xl:col-span-2"
        >
          <Card variant="elevated">
            <CardHeader
              title="Recent Activity"
              subtitle="Latest system events"
              action={
                <Button variant="text" size="small">
                  View All
                </Button>
              }
            />
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + index * 0.1 }}
                    className="flex items-start gap-4 p-4 rounded-xl hover:bg-surface-container-low transition-colors"
                  >
                    <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                      {activity.type === 'ticket' && <Ticket size={18} className="text-primary-600" />}
                      {activity.type === 'resolve' && <CheckCircle size={18} className="text-success-600" />}
                      {activity.type === 'user' && <Users size={18} className="text-secondary-600" />}
                      {activity.type === 'settings' && <Activity size={18} className="text-warning-600" />}
                      {activity.type === 'report' && <TrendingUp size={18} className="text-tertiary-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-neutral-900">{activity.user}</p>
                      <p className="text-sm text-neutral-600 mt-1">{activity.action}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Clock size={14} className="text-neutral-400" />
                        <span className="text-xs text-neutral-500">{activity.time}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};
