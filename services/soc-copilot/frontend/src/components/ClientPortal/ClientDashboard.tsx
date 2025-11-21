/**
 * Client Collaboration Portal - Dashboard
 * COMPETITIVE DIFFERENTIATOR #2: Two-sided marketplace
 *
 * Client-facing dashboard showing:
 * - Pending evidence requests
 * - Recent uploads
 * - Upcoming deadlines
 * - Activity timeline
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface EvidenceRequest {
  id: string;
  request_title: string;
  request_description: string;
  due_date: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: string;
}

interface Upload {
  id: string;
  filename: string;
  uploaded_at: string;
  verification_status: string;
  auditor_feedback?: string;
}

interface DashboardData {
  pending_requests: number;
  overdue_requests: number;
  recent_uploads: number;
  pending_auditor_review: number;
  upcoming_deadlines: EvidenceRequest[];
  recent_activity: Activity[];
}

interface Activity {
  timestamp: string;
  action: string;
  request: string;
}

const ClientDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [requests, setRequests] = useState<EvidenceRequest[]>([]);
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    fetchEvidenceRequests();
    fetchRecentUploads();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/v1/client-portal/client-view/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const fetchEvidenceRequests = async () => {
    try {
      const response = await axios.get('/api/v1/client-portal/client-view/evidence-requests');
      setRequests(response.data);
    } catch (error) {
      console.error('Failed to fetch evidence requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentUploads = async () => {
    try {
      const response = await axios.get('/api/v1/client-portal/client-view/uploads');
      setUploads(response.data);
    } catch (error) {
      console.error('Failed to fetch uploads:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      URGENT: 'bg-red-100 text-red-800 border-red-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      LOW: 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[priority as keyof typeof colors] || colors.MEDIUM;
  };

  const getVerificationStatusColor = (status: string) => {
    const colors = {
      PENDING: 'text-yellow-600',
      ACCEPTED: 'text-green-600',
      REJECTED: 'text-red-600'
    };
    return colors[status as keyof typeof colors] || 'text-gray-600';
  };

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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Client Portal Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's your SOC audit status.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="text-sm font-medium text-gray-600">Pending Requests</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {dashboardData?.pending_requests || 0}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="text-sm font-medium text-gray-600">Overdue</div>
          <div className="text-3xl font-bold text-red-600 mt-2">
            {dashboardData?.overdue_requests || 0}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="text-sm font-medium text-gray-600">Recent Uploads</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {dashboardData?.recent_uploads || 0}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
          <div className="text-sm font-medium text-gray-600">Awaiting Review</div>
          <div className="text-3xl font-bold text-gray-900 mt-2">
            {dashboardData?.pending_auditor_review || 0}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Evidence Requests */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Pending Evidence Requests</h2>
          </div>
          <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
            {requests.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No pending requests</p>
            ) : (
              requests.map(request => (
                <div key={request.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{request.request_title}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(request.priority)}`}>
                      {request.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{request.request_description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">
                      Due: {new Date(request.due_date).toLocaleDateString()}
                    </span>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                      Upload Evidence
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Uploads */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Uploads</h2>
          </div>
          <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
            {uploads.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No uploads yet</p>
            ) : (
              uploads.map(upload => (
                <div key={upload.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{upload.filename}</h3>
                    <span className={`text-sm font-medium ${getVerificationStatusColor(upload.verification_status)}`}>
                      {upload.verification_status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    Uploaded {new Date(upload.uploaded_at).toLocaleString()}
                  </p>
                  {upload.auditor_feedback && (
                    <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                      <p className="font-medium text-gray-700">Auditor Feedback:</p>
                      <p className="text-gray-600">{upload.auditor_feedback}</p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Upcoming Deadlines */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Upcoming Deadlines</h2>
          </div>
          <div className="p-6 space-y-3">
            {dashboardData?.upcoming_deadlines?.map((deadline, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{deadline.request_title}</p>
                  <p className="text-sm text-gray-600">Due: {new Date(deadline.due_date).toLocaleDateString()}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(deadline.priority)}`}>
                  {deadline.priority}
                </span>
              </div>
            )) || <p className="text-gray-500 text-center py-4">No upcoming deadlines</p>}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
          </div>
          <div className="p-6 space-y-3">
            {dashboardData?.recent_activity?.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-2 h-2 mt-2 bg-blue-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-sm text-gray-600">{activity.request}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            )) || <p className="text-gray-500 text-center py-4">No recent activity</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientDashboard;
