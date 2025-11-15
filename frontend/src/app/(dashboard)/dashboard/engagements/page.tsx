'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { FolderOpen, Search, Filter, Plus, MoreVertical, Eye, Edit, Trash2 } from 'lucide-react';
import { api } from '@/lib/api';
import { Engagement, EngagementStatus, EngagementType } from '@/types';
import { formatDate } from '@/lib/utils';
import CreateEngagementForm from '@/components/engagements/create-engagement-form';

export default function EngagementsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<EngagementStatus | 'all'>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const { data: engagements, isLoading, refetch } = useQuery({
    queryKey: ['engagements'],
    queryFn: api.engagements.list,
  });

  const engagementsArray = (engagements as any[]) || [];

  const filteredEngagements = engagementsArray.filter((engagement: Engagement) => {
    const matchesSearch =
      engagement.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      engagement.engagement_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || engagement.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusVariant = (status: EngagementStatus) => {
    switch (status) {
      case EngagementStatus.DRAFT:
        return 'secondary';
      case EngagementStatus.PLANNING:
        return 'default';
      case EngagementStatus.FIELDWORK:
        return 'info';
      case EngagementStatus.REVIEW:
        return 'warning';
      case EngagementStatus.FINALIZED:
        return 'success';
      default:
        return 'default';
    }
  };

  const getTypeColor = (type: EngagementType) => {
    switch (type) {
      case EngagementType.AUDIT:
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      case EngagementType.REVIEW:
        return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20';
      case EngagementType.COMPILATION:
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const stats = [
    {
      label: 'Total Engagements',
      value: engagementsArray.length,
      color: 'text-blue-600',
    },
    {
      label: 'In Progress',
      value: engagementsArray.filter((e: Engagement) =>
        [EngagementStatus.PLANNING, EngagementStatus.FIELDWORK].includes(e.status)
      ).length,
      color: 'text-orange-600',
    },
    {
      label: 'In Review',
      value: engagementsArray.filter((e: Engagement) => e.status === EngagementStatus.REVIEW).length,
      color: 'text-yellow-600',
    },
    {
      label: 'Completed',
      value: engagementsArray.filter((e: Engagement) => e.status === EngagementStatus.FINALIZED).length,
      color: 'text-green-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Engagements</h1>
          <p className="text-muted-foreground">Manage your audit engagements and client work</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg">
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

      {/* Premium Stats Grid */}
      <div className="grid gap-6 md:grid-cols-4">
        {stats.map((stat, index) => (
          <Card
            key={stat.label}
            className="group relative overflow-hidden border-none shadow-lg hover:shadow-xl transition-all duration-300 hover-lift bg-gradient-to-br from-white to-purple-50/20 dark:from-gray-900 dark:to-purple-950/20"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-purple-500/10 to-transparent rounded-bl-full"></div>
            <CardContent className="pt-6 relative z-10">
              <div className="space-y-2">
                <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
                <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
                <div className="h-1 w-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters and Search */}
      <Card className="border-none shadow-lg bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-950">
        <CardHeader className="border-b bg-gradient-to-r from-purple-500/5 to-blue-500/5">
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <CardTitle className="text-xl flex items-center">
                <FolderOpen className="mr-2 h-5 w-5 text-purple-600" />
                All Engagements
              </CardTitle>
              <CardDescription className="mt-1">
                <span className="font-semibold text-purple-600">{filteredEngagements.length}</span> of {engagementsArray.length} engagements
              </CardDescription>
            </div>
            <div className="flex flex-col space-y-2 md:flex-row md:items-center md:space-x-3 md:space-y-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search engagements..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 md:w-[300px] border-gray-300 dark:border-gray-700 focus:border-purple-500 focus:ring-purple-500"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as EngagementStatus | 'all')}
                className="flex h-10 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 px-3 py-2 text-sm focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none transition-all"
              >
                <option value="all">All Status</option>
                <option value={EngagementStatus.DRAFT}>Draft</option>
                <option value={EngagementStatus.PLANNING}>Planning</option>
                <option value={EngagementStatus.FIELDWORK}>Fieldwork</option>
                <option value={EngagementStatus.REVIEW}>Review</option>
                <option value={EngagementStatus.FINALIZED}>Finalized</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          ) : filteredEngagements.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FolderOpen className="h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No engagements found</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {searchQuery || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Get started by creating your first engagement'}
              </p>
              {!searchQuery && statusFilter === 'all' && (
                <Button className="mt-4" onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Engagement
                </Button>
              )}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 hover:bg-gradient-to-r">
                    <TableHead className="font-semibold">Client Name</TableHead>
                    <TableHead className="font-semibold">Type</TableHead>
                    <TableHead className="font-semibold">Fiscal Year End</TableHead>
                    <TableHead className="font-semibold">Status</TableHead>
                    <TableHead className="font-semibold">Created</TableHead>
                    <TableHead className="text-right font-semibold">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEngagements.map((engagement: Engagement) => (
                    <TableRow
                      key={engagement.id}
                      className="group hover:bg-gradient-to-r hover:from-purple-50/50 hover:to-blue-50/50 dark:hover:from-purple-950/20 dark:hover:to-blue-950/20 transition-all duration-200"
                    >
                      <TableCell className="font-semibold text-foreground group-hover:text-purple-700 dark:group-hover:text-purple-400 transition-colors">
                        {engagement.client_name}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold shadow-sm ${getTypeColor(
                            engagement.engagement_type
                          )}`}
                        >
                          {engagement.engagement_type}
                        </span>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{formatDate(engagement.fiscal_year_end, 'short')}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(engagement.status)} className="shadow-sm">
                          {engagement.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{formatDate(engagement.created_at, 'short')}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="hover:bg-purple-100 hover:text-purple-700 dark:hover:bg-purple-950 dark:hover:text-purple-300 transition-colors"
                            onClick={() => window.location.href = `/dashboard/engagements/${engagement.id}`}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="hover:bg-blue-100 hover:text-blue-700 dark:hover:bg-blue-950 dark:hover:text-blue-300 transition-colors"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-800 dark:hover:text-gray-300 transition-colors"
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
