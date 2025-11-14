'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText,
  Send,
  CheckCircle2,
  AlertCircle,
  Clock,
  Filter,
  Download,
  Plus,
  Mail,
  Eye,
  Edit,
  Trash2,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { CreateConfirmationDialog } from './CreateConfirmationDialog';
import { ConfirmationDetailDialog } from './ConfirmationDetailDialog';

interface Confirmation {
  id: string;
  confirmation_type: string;
  entity_name: string;
  amount: number;
  as_of_date: string;
  status: 'not_sent' | 'sent' | 'received' | 'exception' | 'resolved' | 'alternative_procedures';
  sent_date?: string;
  received_date?: string;
  has_exception: boolean;
  confirmed_amount?: number;
  difference_amount?: number;
  entity_email?: string;
  account_number?: string;
}

interface ConfirmationsListProps {
  engagementId: string;
}

export function ConfirmationsList({ engagementId }: ConfirmationsListProps) {
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedConfirmation, setSelectedConfirmation] = useState<Confirmation | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  const queryClient = useQueryClient();

  // Fetch confirmations
  const { data: confirmations = [], isLoading } = useQuery({
    queryKey: ['confirmations', engagementId],
    queryFn: async () => {
      const response = await api.get(`/engagements/${engagementId}/confirmations`);
      return response.data;
    },
  });

  // Delete confirmation
  const deleteMutation = useMutation({
    mutationFn: (confirmationId: string) =>
      api.delete(`/engagements/${engagementId}/confirmations/${confirmationId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confirmations', engagementId] });
      toast.success('Confirmation deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete confirmation');
    },
  });

  // Mark as sent
  const markSentMutation = useMutation({
    mutationFn: (confirmationId: string) =>
      api.post(`/engagements/${engagementId}/confirmations/${confirmationId}/mark-sent`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confirmations', engagementId] });
      toast.success('Marked as sent');
    },
    onError: () => {
      toast.error('Failed to update confirmation');
    },
  });

  // Filter confirmations
  const filteredConfirmations = confirmations.filter((conf: Confirmation) => {
    if (filterType !== 'all' && conf.confirmation_type !== filterType) return false;
    if (filterStatus !== 'all' && conf.status !== filterStatus) return false;
    return true;
  });

  // Calculate statistics
  const stats = {
    total: confirmations.length,
    sent: confirmations.filter((c: Confirmation) => c.status === 'sent' || c.status === 'received' || c.status === 'exception' || c.status === 'resolved').length,
    received: confirmations.filter((c: Confirmation) => c.status === 'received' || c.status === 'resolved').length,
    exceptions: confirmations.filter((c: Confirmation) => c.has_exception).length,
    responseRate: confirmations.filter((c: Confirmation) => c.status === 'sent' || c.status === 'received' || c.status === 'exception' || c.status === 'resolved').length > 0
      ? Math.round((confirmations.filter((c: Confirmation) => c.status === 'received' || c.status === 'resolved').length / confirmations.filter((c: Confirmation) => c.status === 'sent' || c.status === 'received' || c.status === 'exception' || c.status === 'resolved').length) * 100)
      : 0,
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      not_sent: { label: 'Not Sent', variant: 'secondary' as const, icon: Clock },
      sent: { label: 'Sent', variant: 'default' as const, icon: Send },
      received: { label: 'Received', variant: 'default' as const, icon: CheckCircle2 },
      exception: { label: 'Exception', variant: 'destructive' as const, icon: AlertCircle },
      resolved: { label: 'Resolved', variant: 'default' as const, icon: CheckCircle2 },
      alternative_procedures: { label: 'Alt. Proc.', variant: 'secondary' as const, icon: FileText },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.not_sent;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  const getTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      accounts_receivable: 'A/R',
      accounts_payable: 'A/P',
      bank: 'Bank',
      attorney: 'Attorney',
      debt: 'Debt',
      inventory_consignment: 'Inventory',
      other: 'Other',
    };
    return types[type] || type;
  };

  const handleViewDetails = (confirmation: Confirmation) => {
    setSelectedConfirmation(confirmation);
    setDetailDialogOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sent</p>
              <p className="text-3xl font-bold text-gray-900">{stats.sent}</p>
            </div>
            <Send className="w-8 h-8 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Response Rate</p>
              <p className="text-3xl font-bold text-gray-900">{stats.responseRate}%</p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Exceptions</p>
              <p className="text-3xl font-bold text-gray-900">{stats.exceptions}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Filters and Actions */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="bank">Bank</option>
              <option value="accounts_receivable">A/R</option>
              <option value="accounts_payable">A/P</option>
              <option value="attorney">Attorney</option>
              <option value="debt">Debt</option>
              <option value="inventory_consignment">Inventory</option>
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Statuses</option>
              <option value="not_sent">Not Sent</option>
              <option value="sent">Sent</option>
              <option value="received">Received</option>
              <option value="exception">Exception</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <Button
            onClick={() => setCreateDialogOpen(true)}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Confirmation
          </Button>
        </div>
      </Card>

      {/* Confirmations Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  As of Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sent Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredConfirmations.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-500 font-medium">No confirmations found</p>
                    <p className="text-sm text-gray-400 mt-1">
                      {confirmations.length === 0
                        ? 'Create your first confirmation to get started'
                        : 'Try adjusting your filters'}
                    </p>
                  </td>
                </tr>
              ) : (
                filteredConfirmations.map((confirmation: Confirmation) => (
                  <tr key={confirmation.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {confirmation.entity_name}
                          </div>
                          {confirmation.entity_email && (
                            <div className="text-sm text-gray-500 flex items-center gap-1">
                              <Mail className="w-3 h-3" />
                              {confirmation.entity_email}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant="outline">{getTypeLabel(confirmation.confirmation_type)}</Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        ${confirmation.amount?.toLocaleString() || 'N/A'}
                      </div>
                      {confirmation.has_exception && confirmation.difference_amount && (
                        <div className="text-xs text-red-600">
                          Diff: ${confirmation.difference_amount.toLocaleString()}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(confirmation.as_of_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(confirmation.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {confirmation.sent_date
                        ? new Date(confirmation.sent_date).toLocaleDateString()
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewDetails(confirmation)}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>

                        {confirmation.status === 'not_sent' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => markSentMutation.mutate(confirmation.id)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <Send className="w-4 h-4" />
                          </Button>
                        )}

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteMutation.mutate(confirmation.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Dialogs */}
      <CreateConfirmationDialog
        engagementId={engagementId}
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      {selectedConfirmation && (
        <ConfirmationDetailDialog
          confirmation={selectedConfirmation}
          engagementId={engagementId}
          open={detailDialogOpen}
          onOpenChange={setDetailDialogOpen}
        />
      )}
    </div>
  );
}
