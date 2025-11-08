/**
 * AI Service - Powered by Claude/GPT for Audit Intelligence
 *
 * Features:
 * - Account mapping suggestions with ML confidence scores
 * - Risk assessment and scoring
 * - Anomaly insights and explanations
 * - Natural language audit assistance
 * - Document analysis and extraction
 */

import { api } from './api';

export interface AIAccountSuggestion {
  account_code: string;
  account_name: string;
  suggested_mapping: string;
  confidence: number;
  reasoning: string;
  similar_accounts: Array<{
    name: string;
    code: string;
    mapping: string;
  }>;
}

export interface AIRiskScore {
  overall_score: number; // 0-100
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_factors: Array<{
    factor: string;
    score: number;
    description: string;
    recommendations: string[];
  }>;
  estimated_hours: number;
  complexity_factors: string[];
}

export interface AIAnomalyInsight {
  anomaly_id: string;
  summary: string;
  likely_cause: string;
  suggested_procedures: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  similar_cases: Array<{
    description: string;
    resolution: string;
  }>;
}

export interface AIChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  context?: any;
}

export interface AIChatResponse {
  message: string;
  suggested_actions?: Array<{
    action: string;
    description: string;
    url?: string;
  }>;
  references?: Array<{
    standard: string;
    section: string;
    url: string;
  }>;
}

class AIService {
  private baseUrl = process.env.NEXT_PUBLIC_AI_SERVICE_URL || 'http://localhost:8010';

  /**
   * Get AI-powered account mapping suggestions
   */
  async suggestAccountMappings(
    trialBalanceLines: Array<{ account_code: string; account_name: string; balance: number }>
  ): Promise<AIAccountSuggestion[]> {
    try {
      const response = await fetch(`${this.baseUrl}/ai/account-mapping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trial_balance_lines: trialBalanceLines }),
      });

      if (!response.ok) {
        // Fallback to rule-based suggestions
        return this.fallbackAccountSuggestions(trialBalanceLines);
      }

      return await response.json();
    } catch (error) {
      console.error('AI account mapping failed, using fallback:', error);
      return this.fallbackAccountSuggestions(trialBalanceLines);
    }
  }

  /**
   * Calculate AI-powered risk score for engagement
   */
  async calculateRiskScore(engagementData: {
    client_name: string;
    engagement_type: string;
    total_assets?: number;
    total_revenue?: number;
    industry?: string;
    prior_year_issues?: string[];
  }): Promise<AIRiskScore> {
    try {
      const response = await fetch(`${this.baseUrl}/ai/risk-assessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(engagementData),
      });

      if (!response.ok) {
        return this.fallbackRiskScore(engagementData);
      }

      return await response.json();
    } catch (error) {
      console.error('AI risk scoring failed, using fallback:', error);
      return this.fallbackRiskScore(engagementData);
    }
  }

  /**
   * Get AI insights for anomalies
   */
  async analyzeAnomalies(anomalies: Array<{
    account_name: string;
    anomaly_type: string;
    score: number;
    evidence: any;
  }>): Promise<AIAnomalyInsight[]> {
    try {
      const response = await fetch(`${this.baseUrl}/ai/anomaly-insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ anomalies }),
      });

      if (!response.ok) {
        return this.fallbackAnomalyInsights(anomalies);
      }

      return await response.json();
    } catch (error) {
      console.error('AI anomaly analysis failed, using fallback:', error);
      return this.fallbackAnomalyInsights(anomalies);
    }
  }

  /**
   * AI Chat Assistant for audit guidance
   */
  async chat(
    messages: AIChatMessage[],
    context?: {
      engagement_id?: string;
      current_page?: string;
      user_role?: string;
    }
  ): Promise<AIChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, context }),
      });

      if (!response.ok) {
        return {
          message: "I'm currently unavailable. Please try again later or consult the audit manual.",
        };
      }

      return await response.json();
    } catch (error) {
      console.error('AI chat failed:', error);
      return {
        message: "I'm having trouble connecting. Please check your internet connection and try again.",
      };
    }
  }

  /**
   * Generate AI summary of engagement status
   */
  async generateEngagementSummary(engagementId: string): Promise<{
    summary: string;
    key_findings: string[];
    recommended_actions: string[];
    completion_percentage: number;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/ai/engagement-summary/${engagementId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        return {
          summary: 'Unable to generate AI summary at this time.',
          key_findings: [],
          recommended_actions: [],
          completion_percentage: 0,
        };
      }

      return await response.json();
    } catch (error) {
      console.error('AI summary generation failed:', error);
      return {
        summary: 'Summary generation unavailable.',
        key_findings: [],
        recommended_actions: [],
        completion_percentage: 0,
      };
    }
  }

  /**
   * Predict workload hours using ML
   */
  async predictWorkload(engagementData: {
    engagement_type: string;
    total_assets?: number;
    complexity_factors?: string[];
  }): Promise<{
    estimated_hours: number;
    confidence: number;
    breakdown: Array<{
      phase: string;
      hours: number;
    }>;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/ai/workload-prediction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(engagementData),
      });

      if (!response.ok) {
        return this.fallbackWorkloadPrediction(engagementData);
      }

      return await response.json();
    } catch (error) {
      console.error('AI workload prediction failed:', error);
      return this.fallbackWorkloadPrediction(engagementData);
    }
  }

  // Fallback methods when AI service is unavailable

  private fallbackAccountSuggestions(
    lines: Array<{ account_code: string; account_name: string; balance: number }>
  ): AIAccountSuggestion[] {
    return lines.map((line) => {
      // Simple rule-based mapping
      const name = line.account_name.toLowerCase();
      let suggested_mapping = 'Other Assets';
      let confidence = 0.5;

      if (name.includes('cash') || name.includes('bank')) {
        suggested_mapping = 'Cash and Cash Equivalents';
        confidence = 0.9;
      } else if (name.includes('receivable') || name.includes('a/r')) {
        suggested_mapping = 'Accounts Receivable';
        confidence = 0.85;
      } else if (name.includes('inventory')) {
        suggested_mapping = 'Inventory';
        confidence = 0.9;
      } else if (name.includes('payable') || name.includes('a/p')) {
        suggested_mapping = 'Accounts Payable';
        confidence = 0.85;
      } else if (name.includes('revenue') || name.includes('sales')) {
        suggested_mapping = 'Revenue';
        confidence = 0.9;
      } else if (name.includes('expense') || name.includes('cost')) {
        suggested_mapping = 'Operating Expenses';
        confidence = 0.75;
      }

      return {
        account_code: line.account_code,
        account_name: line.account_name,
        suggested_mapping,
        confidence,
        reasoning: `Based on account name pattern matching: "${line.account_name}"`,
        similar_accounts: [],
      };
    });
  }

  private fallbackRiskScore(engagementData: any): AIRiskScore {
    const baseScore = 30;
    const factors: AIRiskScore['risk_factors'] = [
      {
        factor: 'Engagement Type',
        score: engagementData.engagement_type === 'AUDIT' ? 70 : 40,
        description: `${engagementData.engagement_type} engagements require comprehensive procedures`,
        recommendations: ['Allocate sufficient resources', 'Plan for extended fieldwork'],
      },
    ];

    if (engagementData.total_assets && engagementData.total_assets > 10000000) {
      factors.push({
        factor: 'Materiality',
        score: 80,
        description: 'High asset value increases complexity and risk',
        recommendations: ['Increase sample sizes', 'Consider using specialists'],
      });
    }

    const overall_score = Math.min(
      100,
      factors.reduce((sum, f) => sum + f.score, baseScore) / (factors.length + 1)
    );

    return {
      overall_score: Math.round(overall_score),
      risk_level: overall_score > 70 ? 'high' : overall_score > 50 ? 'medium' : 'low',
      risk_factors: factors,
      estimated_hours: engagementData.engagement_type === 'AUDIT' ? 120 : 60,
      complexity_factors: ['Standard complexity assessment'],
    };
  }

  private fallbackAnomalyInsights(anomalies: any[]): AIAnomalyInsight[] {
    return anomalies.map((anomaly) => ({
      anomaly_id: anomaly.id || 'unknown',
      summary: `Unusual activity detected in ${anomaly.account_name}`,
      likely_cause: 'Requires investigation to determine root cause',
      suggested_procedures: [
        'Review supporting documentation',
        'Perform analytical procedures',
        'Inquire with management',
      ],
      priority: anomaly.score > 5 ? 'high' : 'medium',
      similar_cases: [],
    }));
  }

  private fallbackWorkloadPrediction(engagementData: any): {
    estimated_hours: number;
    confidence: number;
    breakdown: Array<{ phase: string; hours: number }>;
  } {
    const baseHours = engagementData.engagement_type === 'AUDIT' ? 120 : 60;

    return {
      estimated_hours: baseHours,
      confidence: 0.6,
      breakdown: [
        { phase: 'Planning', hours: baseHours * 0.15 },
        { phase: 'Fieldwork', hours: baseHours * 0.50 },
        { phase: 'Review', hours: baseHours * 0.25 },
        { phase: 'Reporting', hours: baseHours * 0.10 },
      ],
    };
  }
}

export const aiService = new AIService();
