'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Brain,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertCircle,
  TrendingUp,
  Search,
  Filter,
  Save,
  Wand2,
  ThumbsUp,
  ThumbsDown,
  Info,
  ArrowRight,
} from 'lucide-react';
import { api } from '@/lib/api';
import { aiService, AIAccountSuggestion } from '@/lib/ai-service';
import { AIAssistant } from '@/components/ai/ai-assistant';
import { cn } from '@/lib/utils';

interface TrialBalanceLine {
  id: string;
  account_code: string;
  account_name: string;
  balance_amount: number;
  mapped_account_id?: string;
  mapping_status: 'unmapped' | 'ai_suggested' | 'user_confirmed' | 'user_rejected';
}

export default function AccountMapperPage({ params }: { params: { id: string } }) {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<Map<string, AIAccountSuggestion>>(new Map());

  // Fetch trial balance
  const { data: trialBalance = [], isLoading } = useQuery({
    queryKey: ['trial-balance', params.id],
    queryFn: () => api.trialBalance.getByEngagement(params.id),
  });

  // Get AI suggestions when trial balance loads
  useEffect(() => {
    if (trialBalance.length > 0 && aiSuggestions.size === 0) {
      loadAISuggestions();
    }
  }, [trialBalance]);

  const loadAISuggestions = async () => {
    setIsLoadingAI(true);
    try {
      const suggestions = await aiService.suggestAccountMappings(
        trialBalance.map((line: TrialBalanceLine) => ({
          account_code: line.account_code,
          account_name: line.account_name,
          balance: line.balance_amount,
        }))
      );

      const suggestionsMap = new Map<string, AIAccountSuggestion>();
      suggestions.forEach((suggestion) => {
        suggestionsMap.set(suggestion.account_code, suggestion);
      });
      setAiSuggestions(suggestionsMap);
    } catch (error) {
      console.error('Failed to load AI suggestions:', error);
    } finally {
      setIsLoadingAI(false);
    }
  };

  // Accept AI suggestion
  const acceptSuggestion = useMutation({
    mutationFn: async ({ lineId, mapping }: { lineId: string; mapping: string }) => {
      return await api.trialBalance.updateMapping(lineId, {
        mapped_account: mapping,
        mapping_status: 'user_confirmed',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trial-balance', params.id] });
    },
  });

  // Reject AI suggestion
  const rejectSuggestion = useMutation({
    mutationFn: async ({ lineId }: { lineId: string }) => {
      return await api.trialBalance.updateMapping(lineId, {
        mapping_status: 'user_rejected',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trial-balance', params.id] });
    },
  });

  const filteredLines = trialBalance.filter((line: TrialBalanceLine) => {
    const matchesSearch =
      line.account_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      line.account_code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'unmapped' && !line.mapped_account_id) ||
      (statusFilter === 'mapped' && line.mapped_account_id);
    return matchesSearch && matchesStatus;
  });

  const stats = [
    {
      label: 'Total Accounts',
      value: trialBalance.length,
      icon: Brain,
      color: 'text-blue-600 bg-blue-100',
    },
    {
      label: 'AI Suggested',
      value: aiSuggestions.size,
      icon: Sparkles,
      color: 'text-purple-600 bg-purple-100',
    },
    {
      label: 'Confirmed',
      value: trialBalance.filter((l: TrialBalanceLine) => l.mapping_status === 'user_confirmed').length,
      icon: CheckCircle2,
      color: 'text-green-600 bg-green-100',
    },
    {
      label: 'Unmapped',
      value: trialBalance.filter((l: TrialBalanceLine) => !l.mapped_account_id).length,
      icon: AlertCircle,
      color: 'text-orange-600 bg-orange-100',
    },
  ];

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100 dark:bg-green-900/20';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
    return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20';
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold tracking-tight">AI Account Mapper</h1>
            <Badge
              variant="outline"
              className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 text-blue-600"
            >
              <Sparkles className="mr-1 h-3 w-3" />
              ML-Powered
            </Badge>
          </div>
          <p className="mt-2 text-muted-foreground">
            Intelligent account mapping with machine learning confidence scores
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={loadAISuggestions}
            disabled={isLoadingAI}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            {isLoadingAI ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Analyzing...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-4 w-4" />
                Re-run AI Analysis
              </>
            )}
          </Button>
          <Button variant="outline">
            <Save className="mr-2 h-4 w-4" />
            Save All
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                    <p className="mt-2 text-3xl font-bold">{stat.value}</p>
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

      {/* Mapping Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <CardTitle>Account Mappings</CardTitle>
              <CardDescription>
                {filteredLines.length} of {trialBalance.length} accounts
              </CardDescription>
            </div>
            <div className="flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search accounts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 md:w-[250px]"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="all">All Status</option>
                <option value="unmapped">Unmapped</option>
                <option value="mapped">Mapped</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Account Code</TableHead>
                    <TableHead>Account Name</TableHead>
                    <TableHead className="text-right">Balance</TableHead>
                    <TableHead>AI Suggestion</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLines.map((line: TrialBalanceLine) => {
                    const suggestion = aiSuggestions.get(line.account_code);
                    return (
                      <TableRow key={line.id}>
                        <TableCell className="font-mono text-sm">
                          {line.account_code}
                        </TableCell>
                        <TableCell className="font-medium">{line.account_name}</TableCell>
                        <TableCell className="text-right font-mono">
                          ${line.balance_amount.toLocaleString()}
                        </TableCell>
                        <TableCell>
                          {suggestion ? (
                            <div className="flex items-center space-x-2">
                              <Sparkles className="h-4 w-4 text-purple-600" />
                              <span className="text-sm font-medium">
                                {suggestion.suggested_mapping}
                              </span>
                            </div>
                          ) : isLoadingAI ? (
                            <div className="flex items-center space-x-2">
                              <div className="h-4 w-4 animate-spin rounded-full border-2 border-purple-600 border-t-transparent" />
                              <span className="text-xs text-muted-foreground">
                                Analyzing...
                              </span>
                            </div>
                          ) : (
                            <span className="text-sm text-muted-foreground">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {suggestion && (
                            <Badge className={getConfidenceColor(suggestion.confidence)}>
                              {(suggestion.confidence * 100).toFixed(0)}%
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-1">
                            {suggestion && line.mapping_status !== 'user_confirmed' && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-green-600 hover:bg-green-100 hover:text-green-700"
                                  onClick={() =>
                                    acceptSuggestion.mutate({
                                      lineId: line.id,
                                      mapping: suggestion.suggested_mapping,
                                    })
                                  }
                                  title="Accept AI suggestion"
                                >
                                  <ThumbsUp className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-red-600 hover:bg-red-100 hover:text-red-700"
                                  onClick={() =>
                                    rejectSuggestion.mutate({ lineId: line.id })
                                  }
                                  title="Reject AI suggestion"
                                >
                                  <ThumbsDown className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                            {line.mapping_status === 'user_confirmed' && (
                              <Badge variant="outline" className="text-green-600">
                                <CheckCircle2 className="mr-1 h-3 w-3" />
                                Confirmed
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Assistant */}
      <AIAssistant
        context={{
          engagement_id: params.id,
          current_page: 'account_mapper',
          user_role: 'auditor',
        }}
      />
    </div>
  );
}
