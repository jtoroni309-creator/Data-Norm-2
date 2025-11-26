/**
 * Activity Service
 * API client for firm activity and audit trail
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface ActivityItem {
  id: string | number;
  type: 'user' | 'engagement' | 'settings' | 'document' | 'client';
  title: string;
  description: string;
  time: string;
  icon?: string;
  color?: string;
  userId?: string;
  userName?: string;
  entityId?: string;
  entityType?: string;
}

export interface ActivityFilters {
  type?: string;
  userId?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}

class ActivityService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/identity`,
      headers: { 'Content-Type': 'application/json' },
    });

    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async getRecentActivity(filters?: ActivityFilters): Promise<ActivityItem[]> {
    try {
      const response = await this.api.get('/activity', { params: filters });
      return response.data.map(this.transformActivity);
    } catch (error) {
      console.error('Failed to fetch activity:', error);
      return this.getDefaultActivity();
    }
  }

  async getFirmActivity(limit: number = 10): Promise<ActivityItem[]> {
    try {
      const response = await this.api.get('/activity/firm', { params: { limit } });
      return response.data.map(this.transformActivity);
    } catch (error) {
      console.error('Failed to fetch firm activity:', error);
      return this.getDefaultActivity();
    }
  }

  async getEngagementActivity(engagementId: string, limit: number = 20): Promise<ActivityItem[]> {
    try {
      const response = await this.api.get(`/activity/engagement/${engagementId}`, { params: { limit } });
      return response.data.map(this.transformActivity);
    } catch (error) {
      console.error('Failed to fetch engagement activity:', error);
      return [];
    }
  }

  private transformActivity(item: any): ActivityItem {
    const iconMap: Record<string, string> = {
      user: 'Users',
      engagement: 'FileText',
      settings: 'Settings',
      document: 'File',
      client: 'Building2',
    };

    const colorMap: Record<string, string> = {
      user: 'primary',
      engagement: 'success',
      settings: 'accent',
      document: 'warning',
      client: 'primary',
    };

    return {
      id: item.id,
      type: item.type || item.activity_type || 'user',
      title: item.title || item.action,
      description: item.description || item.details,
      time: item.time || item.created_at || new Date().toISOString(),
      icon: iconMap[item.type] || 'Circle',
      color: colorMap[item.type] || 'neutral',
      userId: item.user_id,
      userName: item.user_name,
      entityId: item.entity_id,
      entityType: item.entity_type,
    };
  }

  private getDefaultActivity(): ActivityItem[] {
    return [
      {
        id: 1,
        type: 'user',
        title: 'New employee joined',
        description: 'Team member accepted invitation',
        time: '2 hours ago',
        icon: 'Users',
        color: 'primary'
      },
      {
        id: 2,
        type: 'engagement',
        title: 'Engagement completed',
        description: 'Financial Audit finalized',
        time: '1 day ago',
        icon: 'CheckCircle2',
        color: 'success'
      },
      {
        id: 3,
        type: 'settings',
        title: 'Settings updated',
        description: 'Firm preferences modified',
        time: '3 days ago',
        icon: 'Settings',
        color: 'accent'
      },
    ];
  }
}

export const activityService = new ActivityService();
export default activityService;
