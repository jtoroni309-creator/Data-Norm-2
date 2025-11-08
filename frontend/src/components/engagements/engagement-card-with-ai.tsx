'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Eye,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sparkles,
  Brain,
} from 'lucide-react';
import { Engagement, EngagementStatus } from '@/types';
import { aiService, AIRiskScore } from '@/lib/ai-service';
import { formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface EngagementCardWithAIProps {
  engagement: Engagement;
  onClick?: () => void;
}

export function EngagementCardWithAI({ engagement, onClick }: EngagementCardWithAIProps) {
  const [riskScore, setRiskScore] = useState<AIRiskScore | null>(null);
  const [isLoadingAI, setIsLoadingAI] = useState(true);

  useEffect(() => {
    const loadAIRiskScore = async () => {
      try {
        const score = await aiService.calculateRiskScore({
          client_name: engagement.client_name,
          engagement_type: engagement.engagement_type,
          total_assets: engagement.total_assets,
          total_revenue: engagement.total_revenue,
          industry: engagement.industry,
          prior_year_issues: engagement.prior_year_issues || [],
        });
        setRiskScore(score);
      } catch (error) {
        console.error('Failed to load AI risk score:', error);
      } finally {
        setIsLoadingAI(false);
      }
    };

    loadAIRiskScore();
  }, [engagement]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'high':
        return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'low':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getStatusIcon = (status: EngagementStatus) => {
    switch (status) {
      case EngagementStatus.FINALIZED:
        return <CheckCircle2 className="h-4 w-4" />;
      case EngagementStatus.REVIEW:
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <Card
      className={cn(
        'group relative overflow-hidden transition-all duration-300 hover:shadow-lg',
        'cursor-pointer border-l-4',
        riskScore?.risk_level === 'critical'
          ? 'border-l-red-500'
          : riskScore?.risk_level === 'high'
            ? 'border-l-orange-500'
            : riskScore?.risk_level === 'medium'
              ? 'border-l-yellow-500'
              : 'border-l-green-500'
      )}
      onClick={onClick}
    >
      {/* AI Badge */}
      <div className="absolute right-2 top-2">
        <Badge
          variant="outline"
          className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 text-blue-600"
        >
          <Sparkles className="mr-1 h-3 w-3" />
          AI Enhanced
        </Badge>
      </div>

      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{engagement.client_name}</CardTitle>
            <div className="flex items-center space-x-2">
              <Badge variant="outline">{engagement.engagement_type}</Badge>
              <Badge
                variant="outline"
                className={cn(
                  'flex items-center space-x-1',
                  engagement.status === EngagementStatus.FINALIZED
                    ? 'border-green-500 text-green-600'
                    : engagement.status === EngagementStatus.REVIEW
                      ? 'border-yellow-500 text-yellow-600'
                      : 'border-blue-500 text-blue-600'
                )}
              >
                {getStatusIcon(engagement.status)}
                <span>{engagement.status}</span>
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* AI Risk Score */}
        {isLoadingAI ? (
          <div className="flex items-center space-x-2 rounded-lg bg-muted p-3">
            <Brain className="h-5 w-5 animate-pulse text-blue-600" />
            <span className="text-sm text-muted-foreground">
              AI analyzing risk factors...
            </span>
          </div>
        ) : riskScore ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">AI Risk Assessment</span>
              <Badge className={getRiskColor(riskScore.risk_level)}>
                {riskScore.risk_level.toUpperCase()} RISK
              </Badge>
            </div>

            {/* Risk Score Bar */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span>Risk Score</span>
                <span className="font-semibold">{riskScore.overall_score}/100</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800">
                <div
                  className={cn(
                    'h-full transition-all duration-500',
                    riskScore.risk_level === 'critical'
                      ? 'bg-red-500'
                      : riskScore.risk_level === 'high'
                        ? 'bg-orange-500'
                        : riskScore.risk_level === 'medium'
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                  )}
                  style={{ width: `${riskScore.overall_score}%` }}
                />
              </div>
            </div>

            {/* Top Risk Factors */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-muted-foreground">
                Top Risk Factors:
              </span>
              {riskScore.risk_factors.slice(0, 2).map((factor, index) => (
                <div key={index} className="flex items-start space-x-2 text-xs">
                  <AlertTriangle className="mt-0.5 h-3 w-3 flex-shrink-0 text-orange-500" />
                  <span className="text-muted-foreground">{factor.factor}</span>
                </div>
              ))}
            </div>

            {/* Estimated Hours */}
            <div className="flex items-center justify-between rounded-lg bg-blue-50 p-2 dark:bg-blue-900/10">
              <span className="text-xs font-semibold text-blue-600">
                AI Estimated Hours:
              </span>
              <span className="text-sm font-bold text-blue-600">
                {riskScore.estimated_hours}h
              </span>
            </div>
          </div>
        ) : null}

        {/* Engagement Details */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Fiscal Year End:</span>
            <p className="font-semibold">{formatDate(engagement.fiscal_year_end, 'short')}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Created:</span>
            <p className="font-semibold">{formatDate(engagement.created_at, 'short')}</p>
          </div>
        </div>

        {/* Action Button */}
        <Button className="w-full" variant="outline">
          <Eye className="mr-2 h-4 w-4" />
          View Engagement
        </Button>
      </CardContent>
    </Card>
  );
}
