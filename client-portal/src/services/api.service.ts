/**
 * API Service
 * Central service for all API calls to the backend
 */

import axios from 'axios';
import type {
  Engagement,
  EngagementProgress,
  DashboardStats,
  ChatMessage,
  AISuggestion,
  Notification,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export class ApiService {
  /**
   * Get dashboard stats
   */
  public async getDashboardStats(engagementId?: string): Promise<DashboardStats> {
    const params = engagementId ? { engagementId } : {};
    const response = await axios.get<DashboardStats>(`${API_BASE_URL}/dashboard/stats`, { params });
    return response.data;
  }

  /**
   * Get engagements
   */
  public async getEngagements(): Promise<Engagement[]> {
    const response = await axios.get<Engagement[]>(`${API_BASE_URL}/engagements`);
    return response.data;
  }

  /**
   * Get engagement details
   */
  public async getEngagement(engagementId: string): Promise<Engagement> {
    const response = await axios.get<Engagement>(`${API_BASE_URL}/engagements/${engagementId}`);
    return response.data;
  }

  /**
   * Get engagement progress
   */
  public async getEngagementProgress(engagementId: string): Promise<EngagementProgress> {
    const response = await axios.get<EngagementProgress>(
      `${API_BASE_URL}/engagements/${engagementId}/progress`
    );
    return response.data;
  }

  /**
   * Get AI chat messages
   */
  public async getChatMessages(engagementId?: string): Promise<ChatMessage[]> {
    const params = engagementId ? { engagementId } : {};
    const response = await axios.get<ChatMessage[]>(`${API_BASE_URL}/ai/chat/messages`, { params });
    return response.data;
  }

  /**
   * Send chat message to AI assistant
   */
  public async sendChatMessage(message: string, engagementId?: string): Promise<ChatMessage> {
    const response = await axios.post<ChatMessage>(`${API_BASE_URL}/ai/chat/send`, {
      message,
      engagementId,
    });
    return response.data;
  }

  /**
   * Get AI suggestions
   */
  public async getAISuggestions(engagementId?: string): Promise<AISuggestion[]> {
    const params = engagementId ? { engagementId } : {};
    const response = await axios.get<AISuggestion[]>(`${API_BASE_URL}/ai/suggestions`, { params });
    return response.data;
  }

  /**
   * Get notifications
   */
  public async getNotifications(): Promise<Notification[]> {
    const response = await axios.get<Notification[]>(`${API_BASE_URL}/notifications`);
    return response.data;
  }

  /**
   * Mark notification as read
   */
  public async markNotificationRead(notificationId: string): Promise<void> {
    await axios.post(`${API_BASE_URL}/notifications/${notificationId}/read`);
  }

  /**
   * Mark all notifications as read
   */
  public async markAllNotificationsRead(): Promise<void> {
    await axios.post(`${API_BASE_URL}/notifications/read-all`);
  }

  /**
   * Get activity feed
   */
  public async getActivityFeed(engagementId?: string): Promise<{
    activities: {
      id: string;
      type: string;
      title: string;
      description: string;
      timestamp: string;
      icon: string;
      color: string;
    }[];
  }> {
    const params = engagementId ? { engagementId } : {};
    const response = await axios.get(`${API_BASE_URL}/activity`, { params });
    return response.data;
  }
}

export const apiService = new ApiService();
