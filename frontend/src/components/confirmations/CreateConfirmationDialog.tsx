'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface CreateConfirmationDialogProps {
  engagementId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateConfirmationDialog({
  engagementId,
  open,
  onOpenChange,
}: CreateConfirmationDialogProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    confirmation_type: 'bank',
    entity_name: '',
    entity_email: '',
    entity_address: '',
    account_number: '',
    amount: '',
    as_of_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const payload = {
        ...data,
        amount: parseFloat(data.amount) || 0,
      };
      return api.post(`/engagements/${engagementId}/confirmations`, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['confirmations', engagementId] });
      toast.success('Confirmation created successfully');
      onOpenChange(false);
      resetForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create confirmation');
    },
  });

  const resetForm = () => {
    setFormData({
      confirmation_type: 'bank',
      entity_name: '',
      entity_email: '',
      entity_address: '',
      account_number: '',
      amount: '',
      as_of_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.entity_name.trim()) {
      toast.error('Entity name is required');
      return;
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      toast.error('Valid amount is required');
      return;
    }
    if (!formData.as_of_date) {
      toast.error('As of date is required');
      return;
    }

    createMutation.mutate(formData);
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center justify-between">
            Create New Confirmation
            <button
              onClick={() => onOpenChange(false)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          {/* Confirmation Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirmation Type *
            </label>
            <select
              value={formData.confirmation_type}
              onChange={(e) => handleChange('confirmation_type', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="bank">Bank Confirmation</option>
              <option value="accounts_receivable">Accounts Receivable</option>
              <option value="accounts_payable">Accounts Payable</option>
              <option value="attorney">Attorney Letter</option>
              <option value="debt">Debt Confirmation</option>
              <option value="inventory_consignment">Inventory/Consignment</option>
              <option value="other">Other</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Select the type of confirmation request
            </p>
          </div>

          {/* Entity Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Entity Name *
              </label>
              <input
                type="text"
                value={formData.entity_name}
                onChange={(e) => handleChange('entity_name', e.target.value)}
                placeholder="e.g., First National Bank"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Entity Email
              </label>
              <input
                type="email"
                value={formData.entity_email}
                onChange={(e) => handleChange('entity_email', e.target.value)}
                placeholder="e.g., confirmations@bank.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Address */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Entity Address
            </label>
            <textarea
              value={formData.entity_address}
              onChange={(e) => handleChange('entity_address', e.target.value)}
              placeholder="123 Main Street&#10;City, State ZIP"
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Account Number and Amount */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Account Number
              </label>
              <input
                type="text"
                value={formData.account_number}
                onChange={(e) => handleChange('account_number', e.target.value)}
                placeholder="e.g., ****1234"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount *
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">
                  $
                </span>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => handleChange('amount', e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
          </div>

          {/* As of Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              As of Date *
            </label>
            <input
              type="date"
              value={formData.as_of_date}
              onChange={(e) => handleChange('as_of_date', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              The date for which the balance should be confirmed
            </p>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Additional notes or special instructions..."
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                onOpenChange(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Confirmation'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
