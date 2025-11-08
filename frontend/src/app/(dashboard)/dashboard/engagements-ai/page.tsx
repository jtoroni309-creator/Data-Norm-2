'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import {
  Plus,
  Search,
  Sparkles,
  TrendingUp,
  AlertCircle,
  Brain,
  Filter
} from 'lucide-react';
import { api } from '@/lib/api';
import { Engagement, EngagementStatus } from '@/types';
import { AIAssistant } from '@/components/ai/ai-assistant';
import { EngagementCardWithAI } from '@/components/engagements/engagement-card-with-ai';
import CreateEngagementForm from '@/components/engagements/create-engagement-form';
import { useRouter } from 'next/navigation';

export default function EngagementsAIPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<EngagementStatus | 'all'>('all');
  const [riskFilter, setRiskFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const { data: engagements = [], isLoading, refetch } = useQuery({
    queryKey: ['engagements'],
    queryFn: api.engagements.list,
  });

  const filteredEngagements = engagements.filter((engagement: Engagement) => {
    const matchesSearch =
      engagement.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      engagement.engagement_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || engagement.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = [
    {
      label: 'Total Engagements',
      value: engagements.length,
      icon: Brain,
      color: 'text-blue-600 bg-blue-100',
      description: 'All active engagements',
    },
    {
      label: 'High Risk',
      value: engagements.filter((e: Engagement) => e.risk_level === 'high').length,
      icon: AlertCircle,
      color: 'text-red-600 bg-red-100',
      description: 'Require immediate attention',
    },
    {
      label: 'In Progress',
      value: engagements.filter((e: Engagement) =>
        [EngagementStatus.PLANNING, EngagementStatus.FIELDWORK].includes(e.status)
      ).length,
      icon: TrendingUp,
      color: 'text-orange-600 bg-orange-100',
      description: 'Active fieldwork',
    },
    {
      label: 'AI Insights',
      value: engagements.filter((e: Engagement) => e.ai_insights_available).length,
      icon: Sparkles,
      color: 'text-purple-600 bg-purple-100',
      description: 'Ready for review',
    },
  ];

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header with AI Badge */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold tracking-tight">Engagements</h1>
            <Badge
              variant="outline"
              className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 text-blue-600"
            >
              <Sparkles className="mr-1 h-3 w-3" />
              AI-Powered
            </Badge>
          </div>
          <p className="mt-2 text-muted-foreground">
            Intelligent engagement management with AI risk scoring and insights
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Plus className="mr-2 h-4 w-4" />
              New Engagement
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Engagement</DialogTitle>
            </DialogHeader>
            <CreateEngagementForm
              onSuccess={() => {
                setIsCreateDialogOpen(false);
                refetch();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* AI-Powered Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="group transition-all duration-300 hover:shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                    <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{stat.description}</p>
                  </div>
                  <div className={`rounded-lg p-2 ${stat.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <CardTitle>AI-Enhanced Engagement List</CardTitle>
              <CardDescription>
                {filteredEngagements.length} of {engagements.length} engagements
              </CardDescription>
            </div>
            <div className="flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search by client or type..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 md:w-[300px]"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as EngagementStatus | 'all')}
                className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="all">All Status</option>
                <option value={EngagementStatus.PLANNING}>Planning</option>
                <option value={EngagementStatus.FIELDWORK}>Fieldwork</option>
                <option value={EngagementStatus.REVIEW}>Review</option>
                <option value={EngagementStatus.COMPLETED}>Completed</option>
              </select>
              <Button variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                More Filters
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="flex flex-col items-center space-y-4">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="text-sm text-muted-foreground">Loading AI-enhanced engagements...</p>
              </div>
            </div>
          ) : filteredEngagements.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Brain className="h-16 w-16 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No engagements found</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {searchQuery || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Get started by creating your first AI-powered engagement'}
              </p>
              {!searchQuery && statusFilter === 'all' && (
                <Button className="mt-4" onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Engagement
                </Button>
              )}
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredEngagements.map((engagement: Engagement) => (
                <EngagementCardWithAI
                  key={engagement.id}
                  engagement={engagement}
                  onClick={() => router.push(`/dashboard/engagements/${engagement.id}`)}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Assistant */}
      <AIAssistant context={{ current_page: 'engagements', user_role: 'auditor' }} />
    </div>
  );
}
