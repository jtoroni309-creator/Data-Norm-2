'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  X,
  Download,
  Send,
  CheckCircle2,
  AlertCircle,
  FileText,
  Calendar,
  DollarSign,
  Building,
  Mail,
  MapPin,
  CreditCard,
  Edit,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface Confirmation {
  id: string;
  confirmation_type: string;
  entity_name: string;
  entity_email?: string;
  entity_address?: string;
  amount: number;
  as_of_date: string;
  status: 'not_sent' | 'sent' | 'received' | 'exception' | 'resolved' | 'alternative_procedures';
  sent_date?: string;
  received_date?: string;
  has_exception: boolean;
  confirmed_amount?: number;
  difference_amount?: number;
  account_number?: string;
  notes?: string;
  exception_notes?: string;
  resolution_notes?: string;
}

interface ConfirmationDetailDialogProps {
  confirmation: Confirmation;
  engagementId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ConfirmationDetailDialog({
  confirmation,
  engagementId,
  open,
  onOpenChange,
}: ConfirmationDetailDialogProps) {
  const queryClient = useQueryClient();
  const [editMode, setEditMode] = useState(false);
  const [responseData, setResponseData] = useState({
    confirmed_amount: confirmation.confirmed_amount?.toString() || '',
    received_date: confirmation.received_date || new Date().toISOString().split('T')[0],
    exception_notes: confirmation.exception_notes || '',
  });

  // Mark as sent mutation
  const markSentMutation = useMutation({
    mutationFn: () =>
      api.post(`/engagements/${engagementId}/confirmations/${confirmation.id}/mark-sent`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confirmations', engagementId] });
      toast.success('Marked as sent');
    },
    onError: () => {
      toast.error('Failed to update confirmation');
    },
  });

  // Record response mutation
  const recordResponseMutation = useMutation({
    mutationFn: (data: any) =>
      api.post(`/engagements/${engagementId}/confirmations/${confirmation.id}/record-response`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confirmations', engagementId] });
      toast.success('Response recorded successfully');
      setEditMode(false);
    },
    onError: () => {
      toast.error('Failed to record response');
    },
  });

  // Generate PDF mutation
  const generatePdfMutation = useMutation({
    mutationFn: () =>
      api.get(`/engagements/${engagementId}/confirmations/${confirmation.id}/generate-pdf`, {
        responseType: 'blob',
      }),
    onSuccess: (response) => {
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `confirmation-${confirmation.entity_name.replace(/\s+/g, '-')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('PDF downloaded successfully');
    },
    onError: () => {
      toast.error('Failed to generate PDF');
    },
  });

  const handleRecordResponse = () => {
    const confirmedAmount = parseFloat(responseData.confirmed_amount);

    if (isNaN(confirmedAmount) || confirmedAmount < 0) {
      toast.error('Please enter a valid confirmed amount');
      return;
    }

    const data = {
      confirmed_amount: confirmedAmount,
      received_date: responseData.received_date,
      exception_notes: responseData.exception_notes.trim() || null,
    };

    recordResponseMutation.mutate(data);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      not_sent: { label: 'Not Sent', className: 'bg-gray-100 text-gray-700', icon: Calendar },
      sent: { label: 'Sent', className: 'bg-blue-100 text-blue-700', icon: Send },
      received: { label: 'Received', className: 'bg-green-100 text-green-700', icon: CheckCircle2 },
      exception: { label: 'Exception', className: 'bg-red-100 text-red-700', icon: AlertCircle },
      resolved: { label: 'Resolved', className: 'bg-purple-100 text-purple-700', icon: CheckCircle2 },
      alternative_procedures: { label: 'Alt. Procedures', className: 'bg-yellow-100 text-yellow-700', icon: FileText },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.not_sent;
    const Icon = config.icon;

    return (
      <Badge className={`${config.className} flex items-center gap-1 text-sm px-3 py-1`}>
        <Icon className="w-4 h-4" />
        {config.label}
      </Badge>
    );
  };

  const getTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      accounts_receivable: 'Accounts Receivable',
      accounts_payable: 'Accounts Payable',
      bank: 'Bank Confirmation',
      attorney: 'Attorney Letter',
      debt: 'Debt Confirmation',
      inventory_consignment: 'Inventory/Consignment',
      other: 'Other',
    };
    return types[type] || type;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center justify-between">
            <span>Confirmation Details</span>
            <button
              onClick={() => onOpenChange(false)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Status and Type */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getStatusBadge(confirmation.status)}
              <Badge variant="outline" className="text-sm px-3 py-1">
                {getTypeLabel(confirmation.confirmation_type)}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => generatePdfMutation.mutate()}
                disabled={generatePdfMutation.isPending}
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                {generatePdfMutation.isPending ? 'Generating...' : 'Download PDF'}
              </Button>
              {confirmation.status === 'not_sent' && (
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => markSentMutation.mutate()}
                  disabled={markSentMutation.isPending}
                  className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600"
                >
                  <Send className="w-4 h-4" />
                  Mark as Sent
                </Button>
              )}
            </div>
          </div>

          {/* Entity Information */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Building className="w-5 h-5 text-blue-600" />
              Entity Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Entity Name</p>
                <p className="font-medium">{confirmation.entity_name}</p>
              </div>
              {confirmation.entity_email && (
                <div>
                  <p className="text-sm text-gray-500 mb-1 flex items-center gap-1">
                    <Mail className="w-4 h-4" />
                    Email
                  </p>
                  <p className="font-medium">{confirmation.entity_email}</p>
                </div>
              )}
              {confirmation.entity_address && (
                <div className="md:col-span-2">
                  <p className="text-sm text-gray-500 mb-1 flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    Address
                  </p>
                  <p className="font-medium whitespace-pre-line">{confirmation.entity_address}</p>
                </div>
              )}
              {confirmation.account_number && (
                <div>
                  <p className="text-sm text-gray-500 mb-1 flex items-center gap-1">
                    <CreditCard className="w-4 h-4" />
                    Account Number
                  </p>
                  <p className="font-medium font-mono">{confirmation.account_number}</p>
                </div>
              )}
            </div>
          </Card>

          {/* Amount and Dates */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              Financial Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Requested Amount</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${confirmation.amount.toLocaleString()}
                </p>
              </div>
              {confirmation.confirmed_amount !== null && confirmation.confirmed_amount !== undefined && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Confirmed Amount</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${confirmation.confirmed_amount.toLocaleString()}
                  </p>
                </div>
              )}
              {confirmation.has_exception && confirmation.difference_amount && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Difference</p>
                  <p className="text-2xl font-bold text-red-600">
                    ${Math.abs(confirmation.difference_amount).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t">
              <div>
                <p className="text-sm text-gray-500 mb-1">As of Date</p>
                <p className="font-medium">
                  {new Date(confirmation.as_of_date).toLocaleDateString()}
                </p>
              </div>
              {confirmation.sent_date && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Sent Date</p>
                  <p className="font-medium">
                    {new Date(confirmation.sent_date).toLocaleDateString()}
                  </p>
                </div>
              )}
              {confirmation.received_date && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Received Date</p>
                  <p className="font-medium">
                    {new Date(confirmation.received_date).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {/* Notes */}
          {confirmation.notes && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-2">Notes</h3>
              <p className="text-gray-700 whitespace-pre-line">{confirmation.notes}</p>
            </Card>
          )}

          {/* Exception Notes */}
          {confirmation.has_exception && confirmation.exception_notes && (
            <Card className="p-6 border-red-200 bg-red-50">
              <h3 className="text-lg font-semibold mb-2 text-red-900 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Exception Notes
              </h3>
              <p className="text-red-800 whitespace-pre-line">{confirmation.exception_notes}</p>
            </Card>
          )}

          {/* Record Response Section */}
          {(confirmation.status === 'sent' || editMode) && (
            <Card className="p-6 border-blue-200 bg-blue-50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-blue-900 flex items-center gap-2">
                  <Edit className="w-5 h-5" />
                  Record Response
                </h3>
                {!editMode && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setEditMode(true)}
                  >
                    Edit Response
                  </Button>
                )}
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-blue-900 mb-2">
                      Confirmed Amount *
                    </label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                        $
                      </span>
                      <input
                        type="number"
                        step="0.01"
                        value={responseData.confirmed_amount}
                        onChange={(e) =>
                          setResponseData((prev) => ({
                            ...prev,
                            confirmed_amount: e.target.value,
                          }))
                        }
                        className="w-full pl-8 pr-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        placeholder="0.00"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-blue-900 mb-2">
                      Received Date *
                    </label>
                    <input
                      type="date"
                      value={responseData.received_date}
                      onChange={(e) =>
                        setResponseData((prev) => ({
                          ...prev,
                          received_date: e.target.value,
                        }))
                      }
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-blue-900 mb-2">
                    Exception Notes (if any)
                  </label>
                  <textarea
                    value={responseData.exception_notes}
                    onChange={(e) =>
                      setResponseData((prev) => ({
                        ...prev,
                        exception_notes: e.target.value,
                      }))
                    }
                    rows={4}
                    className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    placeholder="Describe any exceptions or differences..."
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  {editMode && (
                    <Button
                      variant="outline"
                      onClick={() => setEditMode(false)}
                    >
                      Cancel
                    </Button>
                  )}
                  <Button
                    onClick={handleRecordResponse}
                    disabled={recordResponseMutation.isPending}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                  >
                    {recordResponseMutation.isPending ? 'Recording...' : 'Record Response'}
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
