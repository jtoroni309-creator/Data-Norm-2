/**
 * Continuous Control Monitoring Dashboard
 * COMPETITIVE DIFFERENTIATOR #3: Real-time control monitoring
 *
 * Auditor dashboard showing:
 * - Real-time control health status
 * - Monitoring agent status
 * - Anomaly detections
 * - Control health trends
 * - Predictive alerts
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface MonitoringAgent {
  id: string;
  agent_name: string;
  agent_type: string;
  status: 'ACTIVE' | 'PAUSED' | 'FAILED' | 'DISCONNECTED';
  last_check_at: string;
  next_check_at: string;
}

interface ControlHealth {
  control_id: string;
  control_name: string;
  health_status: 'HEALTHY' | 'DEGRADED' | 'AT_RISK' | 'FAILING';
  health_score: number;
  success_rate: number;
  trend_direction: 'IMPROVING' | 'STABLE' | 'DEGRADING';
}

interface Anomaly {
  control_id: string;
  control_name: string;
  anomaly_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  detected_at: string;
  recommended_action: string;
}

const CCMMonitoringDashboard: React.FC = () => {
  const [agents, setAgents] = useState<MonitoringAgent[]>([]);
  const [controlHealth, setControlHealth] = useState<ControlHealth[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [healthTrends, setHealthTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Mock data - in production, fetch from API
      const mockAgents: MonitoringAgent[] = [
        {
          id: '1',
          agent_name: 'MFA Enforcement Monitor',
          agent_type: 'ACCESS_CONTROL',
          status: 'ACTIVE',
          last_check_at: new Date(Date.now() - 15 * 60000).toISOString(),
          next_check_at: new Date(Date.now() + 45 * 60000).toISOString()
        },
        {
          id: '2',
          agent_name: 'Backup Success Monitor',
          agent_type: 'BACKUP_RECOVERY',
          status: 'ACTIVE',
          last_check_at: new Date(Date.now() - 5 * 60000).toISOString(),
          next_check_at: new Date(Date.now() + 55 * 60000).toISOString()
        },
        {
          id: '3',
          agent_name: 'Vulnerability Scan Monitor',
          agent_type: 'VULNERABILITY_SCANNING',
          status: 'ACTIVE',
          last_check_at: new Date(Date.now() - 120 * 60000).toISOString(),
          next_check_at: new Date(Date.now() + 120 * 60000).toISOString()
        }
      ];

      const mockHealth: ControlHealth[] = [
        {
          control_id: '1',
          control_name: 'Multi-Factor Authentication',
          health_status: 'HEALTHY',
          health_score: 95,
          success_rate: 98.5,
          trend_direction: 'STABLE'
        },
        {
          control_id: '2',
          control_name: 'Daily Backup Execution',
          health_status: 'DEGRADED',
          health_score: 82,
          success_rate: 87.0,
          trend_direction: 'DEGRADING'
        },
        {
          control_id: '3',
          control_name: 'Vulnerability Patching',
          health_status: 'AT_RISK',
          health_score: 65,
          success_rate: 72.0,
          trend_direction: 'DEGRADING'
        }
      ];

      const mockAnomalies: Anomaly[] = [
        {
          control_id: '2',
          control_name: 'Daily Backup Execution',
          anomaly_type: 'SUDDEN_DEGRADATION',
          severity: 'HIGH',
          description: 'Backup success rate dropped from 98% to 87% in past 7 days',
          detected_at: new Date().toISOString(),
          recommended_action: 'Investigate storage capacity and backup job configurations'
        }
      ];

      const mockTrends = [
        { date: '01/15', score: 92 },
        { date: '01/16', score: 93 },
        { date: '01/17', score: 91 },
        { date: '01/18', score: 89 },
        { date: '01/19', score: 87 },
        { date: '01/20', score: 85 },
        { date: '01/21', score: 82 }
      ];

      setAgents(mockAgents);
      setControlHealth(mockHealth);
      setAnomalies(mockAnomalies);
      setHealthTrends(mockTrends);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const getHealthStatusColor = (status: string) => {
    const colors = {
      HEALTHY: 'bg-green-100 text-green-800 border-green-300',
      DEGRADED: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      AT_RISK: 'bg-orange-100 text-orange-800 border-orange-300',
      FAILING: 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[status as keyof typeof colors] || colors.HEALTHY;
  };

  const getAgentStatusColor = (status: string) => {
    const colors = {
      ACTIVE: 'text-green-600',
      PAUSED: 'text-yellow-600',
      FAILED: 'text-red-600',
      DISCONNECTED: 'text-gray-600'
    };
    return colors[status as keyof typeof colors] || 'text-gray-600';
  };

  const getSeverityColor = (severity: string) => {
    const colors = {
      CRITICAL: 'bg-red-600 text-white',
      HIGH: 'bg-orange-600 text-white',
      MEDIUM: 'bg-yellow-600 text-white',
      LOW: 'bg-blue-600 text-white'
    };
    return colors[severity as keyof typeof colors] || colors.MEDIUM;
  };

  const getTrendIcon = (direction: string) => {
    if (direction === 'IMPROVING') return '↗';
    if (direction === 'DEGRADING') return '↘';
    return '→';
  };

  // Pie chart data
  const healthDistribution = [
    { name: 'Healthy', value: controlHealth.filter(c => c.health_status === 'HEALTHY').length, color: '#10B981' },
    { name: 'Degraded', value: controlHealth.filter(c => c.health_status === 'DEGRADED').length, color: '#F59E0B' },
    { name: 'At Risk', value: controlHealth.filter(c => c.health_status === 'AT_RISK').length, color: '#F97316' },
    { name: 'Failing', value: controlHealth.filter(c => c.health_status === 'FAILING').length, color: '#EF4444' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Continuous Control Monitoring</h1>
          <p className="text-gray-600 mt-2">Real-time monitoring and anomaly detection</p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="text-sm font-medium text-gray-600">Active Agents</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {agents.filter(a => a.status === 'ACTIVE').length}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="text-sm font-medium text-gray-600">Healthy Controls</div>
          <div className="text-3xl font-bold text-green-600 mt-2">
            {controlHealth.filter(c => c.health_status === 'HEALTHY').length}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
          <div className="text-sm font-medium text-gray-600">At Risk</div>
          <div className="text-3xl font-bold text-orange-600 mt-2">
            {controlHealth.filter(c => c.health_status === 'AT_RISK').length}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="text-sm font-medium text-gray-600">Anomalies (24h)</div>
          <div className="text-3xl font-bold text-red-600 mt-2">
            {anomalies.length}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Health Trend Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Control Health Trend (7 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={healthTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#3B82F6"
                strokeWidth={2}
                name="Health Score"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Health Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Control Health Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={healthDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {healthDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Control Health Status */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Control Health Status</h2>
          </div>
          <div className="p-6 space-y-4">
            {controlHealth.map(control => (
              <div key={control.control_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{control.control_name}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getHealthStatusColor(control.health_status)}`}>
                    {control.health_status}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3">
                  <div>
                    <p className="text-xs text-gray-500">Health Score</p>
                    <p className="text-lg font-semibold text-gray-900">{control.health_score}/100</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Success Rate</p>
                    <p className="text-lg font-semibold text-gray-900">{control.success_rate}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Trend</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {getTrendIcon(control.trend_direction)} {control.trend_direction}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monitoring Agents */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Monitoring Agents</h2>
          </div>
          <div className="p-6 space-y-4">
            {agents.map(agent => (
              <div key={agent.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{agent.agent_name}</h3>
                  <span className={`text-sm font-medium ${getAgentStatusColor(agent.status)}`}>
                    ● {agent.status}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mb-2">{agent.agent_type}</p>
                <div className="space-y-1">
                  <p className="text-xs text-gray-600">
                    Last check: {new Date(agent.last_check_at).toLocaleTimeString()}
                  </p>
                  <p className="text-xs text-gray-600">
                    Next check: {new Date(agent.next_check_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Anomalies */}
        <div className="lg:col-span-3 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Detected Anomalies</h2>
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
              {anomalies.length} Active
            </span>
          </div>
          <div className="p-6 space-y-4">
            {anomalies.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No anomalies detected</p>
            ) : (
              anomalies.map((anomaly, index) => (
                <div key={index} className="border-l-4 border-red-500 bg-red-50 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">{anomaly.control_name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{anomaly.anomaly_type}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-md text-xs font-medium ${getSeverityColor(anomaly.severity)}`}>
                      {anomaly.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-800 mb-3">{anomaly.description}</p>
                  <div className="bg-white rounded p-3">
                    <p className="text-xs font-medium text-gray-700">Recommended Action:</p>
                    <p className="text-sm text-gray-600 mt-1">{anomaly.recommended_action}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Detected: {new Date(anomaly.detected_at).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CCMMonitoringDashboard;
