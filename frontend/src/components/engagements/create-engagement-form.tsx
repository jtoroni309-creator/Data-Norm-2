'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { EngagementType, EngagementStatus } from '@/types';
import { toast } from 'sonner';

interface CreateEngagementFormProps {
  onSuccess: () => void;
}

export default function CreateEngagementForm({ onSuccess }: CreateEngagementFormProps) {
  const [formData, setFormData] = useState({
    client_name: '',
    engagement_type: EngagementType.AUDIT,
    fiscal_year_end: '',
    partner_id: '',
    manager_id: '',
    status: EngagementStatus.PLANNING,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch users for partner/manager selection (mock for now)
  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      // Mock users - in production this would fetch from /users endpoint
      return [
        { id: '1', full_name: 'John Smith', role: 'partner' },
        { id: '2', full_name: 'Sarah Johnson', role: 'partner' },
        { id: '3', full_name: 'Mike Davis', role: 'manager' },
        { id: '4', full_name: 'Emily Brown', role: 'manager' },
      ];
    },
  });

  const createMutation = useMutation({
    mutationFn: api.engagements.create,
    onSuccess: () => {
      toast.success('Engagement created successfully!');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create engagement');
    },
  });

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.client_name.trim()) {
      newErrors.client_name = 'Client name is required';
    }

    if (!formData.fiscal_year_end) {
      newErrors.fiscal_year_end = 'Fiscal year end is required';
    }

    if (!formData.partner_id) {
      newErrors.partner_id = 'Partner is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Clean up empty manager_id
    const submitData = {
      ...formData,
      manager_id: formData.manager_id || undefined,
    };

    createMutation.mutate(submitData);
  };

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const partners = users.filter((u: any) => u.role === 'partner');
  const managers = users.filter((u: any) => u.role === 'manager');

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="client_name">
            Client Name <span className="text-destructive">*</span>
          </Label>
          <Input
            id="client_name"
            value={formData.client_name}
            onChange={(e) => handleChange('client_name', e.target.value)}
            placeholder="ABC Corporation"
            error={errors.client_name}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="engagement_type">
            Engagement Type <span className="text-destructive">*</span>
          </Label>
          <select
            id="engagement_type"
            value={formData.engagement_type}
            onChange={(e) => handleChange('engagement_type', e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value={EngagementType.AUDIT}>Audit</option>
            <option value={EngagementType.REVIEW}>Review</option>
            <option value={EngagementType.COMPILATION}>Compilation</option>
            <option value={EngagementType.TAX}>Tax</option>
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="fiscal_year_end">
            Fiscal Year End <span className="text-destructive">*</span>
          </Label>
          <Input
            id="fiscal_year_end"
            type="date"
            value={formData.fiscal_year_end}
            onChange={(e) => handleChange('fiscal_year_end', e.target.value)}
            error={errors.fiscal_year_end}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <select
            id="status"
            value={formData.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value={EngagementStatus.PLANNING}>Planning</option>
            <option value={EngagementStatus.FIELDWORK}>Fieldwork</option>
            <option value={EngagementStatus.REVIEW}>Review</option>
            <option value={EngagementStatus.COMPLETED}>Completed</option>
            <option value={EngagementStatus.ARCHIVED}>Archived</option>
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="partner_id">
            Partner <span className="text-destructive">*</span>
          </Label>
          <select
            id="partner_id"
            value={formData.partner_id}
            onChange={(e) => handleChange('partner_id', e.target.value)}
            className={`flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
              errors.partner_id ? 'border-destructive' : 'border-input'
            }`}
          >
            <option value="">Select partner...</option>
            {partners.map((partner: any) => (
              <option key={partner.id} value={partner.id}>
                {partner.full_name}
              </option>
            ))}
          </select>
          {errors.partner_id && <p className="text-sm text-destructive">{errors.partner_id}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="manager_id">Manager (Optional)</Label>
          <select
            id="manager_id"
            value={formData.manager_id}
            onChange={(e) => handleChange('manager_id', e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="">Select manager...</option>
            {managers.map((manager: any) => (
              <option key={manager.id} value={manager.id}>
                {manager.full_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancel
        </Button>
        <Button type="submit" loading={createMutation.isPending}>
          Create Engagement
        </Button>
      </div>
    </form>
  );
}
