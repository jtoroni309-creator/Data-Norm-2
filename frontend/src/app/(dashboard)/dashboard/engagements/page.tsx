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

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <CardTitle>All Engagements</CardTitle>
              <CardDescription>
                {filteredEngagements.length} of {engagementsArray.length} engagements
              </CardDescription>
            </div>
            <div className="flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search engagements..."
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
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Client Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Fiscal Year End</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEngagements.map((engagement: Engagement) => (
                    <TableRow key={engagement.id}>
                      <TableCell className="font-medium">{engagement.client_name}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getTypeColor(
                            engagement.engagement_type
                          )}`}
                        >
                          {engagement.engagement_type}
                        </span>
                      </TableCell>
                      <TableCell>{formatDate(engagement.fiscal_year_end, 'short')}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(engagement.status)}>
                          {engagement.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(engagement.created_at, 'short')}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => window.location.href = `/dashboard/engagements/${engagement.id}`}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
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
