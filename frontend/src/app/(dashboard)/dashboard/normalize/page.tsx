'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  GitCompare,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Search,
  Play,
  Download,
  Filter,
} from 'lucide-react';
import { api } from '@/lib/api';
import { MappingSuggestion } from '@/types';
import { formatDate, formatNumber } from '@/lib/utils';
import { toast } from 'sonner';

export default function NormalizePage() {
  const [selectedEngagement, setSelectedEngagement] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [confidenceFilter, setConfidenceFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Fetch engagements
  const { data: engagements = [] } = useQuery({
    queryKey: ['engagements'],
    queryFn: api.engagements.list,
  });

  // Fetch mapping suggestions
  const {
    data: suggestions = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['mapping-suggestions', selectedEngagement],
    queryFn: () => api.normalize.mappings.list(selectedEngagement),
    enabled: !!selectedEngagement,
  });

  // Generate suggestions mutation
  const generateSuggestionsMutation = useMutation({
    mutationFn: () => api.normalize.mappings.generate(selectedEngagement),
    onSuccess: () => {
      toast.success('Mapping suggestions generated successfully!');
      refetch();
    },
    onError: () => {
      toast.error('Failed to generate mapping suggestions');
    },
  });

  // Confirm mapping mutation
  const confirmMappingMutation = useMutation({
    mutationFn: (suggestionId: string) =>
      api.normalize.mappings.update(suggestionId, { status: 'confirmed' }),
    onSuccess: () => {
      toast.success('Mapping confirmed!');
      refetch();
    },
    onError: () => {
      toast.error('Failed to confirm mapping');
    },
  });

  // Reject mapping mutation
  const rejectMappingMutation = useMutation({
    mutationFn: (suggestionId: string) =>
      api.normalize.mappings.update(suggestionId, { status: 'rejected' }),
    onSuccess: () => {
      toast.success('Mapping rejected');
      refetch();
    },
    onError: () => {
      toast.error('Failed to reject mapping');
    },
  });

  // Filter suggestions
  const filteredSuggestions = suggestions.filter((suggestion: MappingSuggestion) => {
    const matchesSearch =
      suggestion.source_account_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      suggestion.source_account_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      suggestion.suggested_account_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      suggestion.suggested_account_code.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesConfidence =
      confidenceFilter === 'all' || suggestion.confidence_level === confidenceFilter;

    const matchesStatus = statusFilter === 'all' || suggestion.status === statusFilter;

    return matchesSearch && matchesConfidence && matchesStatus;
  });

  // Calculate stats
  const confirmedCount = suggestions.filter((s: MappingSuggestion) => s.status === 'confirmed')
    .length;
  const pendingCount = suggestions.filter((s: MappingSuggestion) => s.status === 'suggested')
    .length;
  const rejectedCount = suggestions.filter((s: MappingSuggestion) => s.status === 'rejected')
    .length;
  const avgConfidence =
    suggestions.length > 0
      ? suggestions.reduce((acc: number, s: MappingSuggestion) => acc + s.confidence_score, 0) /
        suggestions.length
      : 0;

  const getConfidenceBadgeVariant = (level: string) => {
    switch (level) {
      case 'very_high':
        return 'success';
      case 'high':
        return 'info';
      case 'medium':
        return 'warning';
      case 'low':
        return 'destructive';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'rejected':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'suggested':
        return <AlertCircle className="h-4 w-4 text-orange-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Normalize</h1>
          <p className="text-muted-foreground">
            AI-powered account mapping and data normalization
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={selectedEngagement}
            onChange={(e) => setSelectedEngagement(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="">Select engagement...</option>
            {engagements.map((eng: any) => (
              <option key={eng.id} value={eng.id}>
                {eng.client_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!selectedEngagement ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GitCompare className="h-16 w-16 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">Select an engagement to begin</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Choose an engagement from the dropdown above to start mapping
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">{suggestions.length}</p>
                    <p className="text-sm text-muted-foreground">Total Mappings</p>
                  </div>
                  <GitCompare className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-green-600">{confirmedCount}</p>
                    <p className="text-sm text-muted-foreground">Confirmed</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-orange-600">{pendingCount}</p>
                    <p className="text-sm text-muted-foreground">Pending Review</p>
                  </div>
                  <AlertCircle className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">{formatNumber(avgConfidence * 100, 0)}%</p>
                    <p className="text-sm text-muted-foreground">Avg Confidence</p>
                  </div>
                  <div className="text-muted-foreground">🎯</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <Card>
            <CardHeader>
              <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
                <div>
                  <CardTitle>Account Mapping Suggestions</CardTitle>
                  <CardDescription>
                    {filteredSuggestions.length} of {suggestions.length} suggestions
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={() => generateSuggestionsMutation.mutate()}
                    loading={generateSuggestionsMutation.isPending}
                  >
                    <Play className="mr-2 h-4 w-4" />
                    Generate Suggestions
                  </Button>
                  <Button variant="outline">
                    <Download className="mr-2 h-4 w-4" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="mb-4 flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search accounts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <select
                  value={confidenceFilter}
                  onChange={(e) => setConfidenceFilter(e.target.value)}
                  className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="all">All Confidence</option>
                  <option value="very_high">Very High</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="all">All Status</option>
                  <option value="suggested">Suggested</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="rejected">Rejected</option>
                  <option value="manual">Manual</option>
                </select>
              </div>

              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : filteredSuggestions.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <GitCompare className="h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-semibold">No mapping suggestions yet</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {searchQuery || confidenceFilter !== 'all' || statusFilter !== 'all'
                      ? 'Try adjusting your filters'
                      : 'Click "Generate Suggestions" to create AI-powered mappings'}
                  </p>
                </div>
              ) : (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Source Account</TableHead>
                        <TableHead>Suggested Account</TableHead>
                        <TableHead>Confidence</TableHead>
                        <TableHead>Score</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredSuggestions.map((suggestion: MappingSuggestion) => (
                        <TableRow key={suggestion.id}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{suggestion.source_account_code}</p>
                              <p className="text-sm text-muted-foreground">
                                {suggestion.source_account_name}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-medium">{suggestion.suggested_account_code}</p>
                              <p className="text-sm text-muted-foreground">
                                {suggestion.suggested_account_name}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getConfidenceBadgeVariant(suggestion.confidence_level)}>
                              {suggestion.confidence_level.replace('_', ' ')}
                            </Badge>
                          </TableCell>
                          <TableCell>{formatNumber(suggestion.confidence_score * 100, 0)}%</TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(suggestion.status)}
                              <span className="text-sm capitalize">{suggestion.status}</span>
                            </div>
                          </TableCell>
                          <TableCell>{formatDate(suggestion.created_at, 'short')}</TableCell>
                          <TableCell className="text-right">
                            {suggestion.status === 'suggested' && (
                              <div className="flex items-center justify-end space-x-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => confirmMappingMutation.mutate(suggestion.id)}
                                  loading={confirmMappingMutation.isPending}
                                >
                                  <CheckCircle2 className="mr-1 h-3 w-3" />
                                  Confirm
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => rejectMappingMutation.mutate(suggestion.id)}
                                  loading={rejectMappingMutation.isPending}
                                >
                                  <XCircle className="mr-1 h-3 w-3" />
                                  Reject
                                </Button>
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
