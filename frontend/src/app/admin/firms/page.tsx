'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Building2,
  Plus,
  Search,
  MoreHorizontal,
  Edit,
  Trash2,
  Users,
  FileText,
} from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { formatDate } from '@/lib/utils';

interface CPAFirm {
  id: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  license_number: string;
  status: 'active' | 'suspended' | 'trial';
  subscription_plan: 'basic' | 'professional' | 'enterprise';
  user_count: number;
  engagement_count: number;
  created_at: string;
  last_activity: string;
}

export default function CPAFirmsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedFirm, setSelectedFirm] = useState<CPAFirm | null>(null);
  const queryClient = useQueryClient();

  const { data: firms, isLoading } = useQuery({
    queryKey: ['cpa-firms'],
    queryFn: api.admin.customers.list,
  });
  const firmsArray = (firms as any[]) || [];

  const createFirmMutation = useMutation({
    mutationFn: (firmData: any) => api.admin.customers.create(firmData),
    onSuccess: () => {
      toast.success('CPA firm created successfully!');
      queryClient.invalidateQueries({ queryKey: ['cpa-firms'] });
      setIsCreateDialogOpen(false);
    },
    onError: () => {
      toast.error('Failed to create CPA firm');
    },
  });

  const updateFirmMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      api.admin.customers.update(id, data),
    onSuccess: () => {
      toast.success('CPA firm updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['cpa-firms'] });
    },
    onError: () => {
      toast.error('Failed to update CPA firm');
    },
  });

  const deleteFirmMutation = useMutation({
    mutationFn: (id: string) => api.admin.customers.delete(id),
    onSuccess: () => {
      toast.success('CPA firm deleted successfully!');
      queryClient.invalidateQueries({ queryKey: ['cpa-firms'] });
    },
    onError: () => {
      toast.error('Failed to delete CPA firm');
    },
  });

  const filteredFirms = firmsArray.filter((firm: any) =>
    firm.company_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    firm.contact_email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'trial':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'suspended':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'enterprise':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400';
      case 'professional':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'basic':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">CPA Firms</h1>
          <p className="text-muted-foreground">
            Manage CPA firm accounts and subscriptions
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add CPA Firm
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New CPA Firm</DialogTitle>
              <DialogDescription>
                Create a new CPA firm account with subscription details
              </DialogDescription>
            </DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                createFirmMutation.mutate({
                  company_name: formData.get('name'),
                  contact_email: formData.get('email'),
                  contact_phone: formData.get('phone'),
                  address: formData.get('address'),
                  city: formData.get('city'),
                  state: formData.get('state'),
                  zip: formData.get('zip'),
                  license_number: formData.get('license'),
                  company_size: formData.get('plan'),
                  status: 'trial',
                });
              }}
            >
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Firm Name *</Label>
                    <Input id="name" name="name" placeholder="Acme CPA Firm" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="license">License Number *</Label>
                    <Input id="license" name="license" placeholder="CPA-12345" required />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="contact@firm.com"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone *</Label>
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      placeholder="+1 (555) 123-4567"
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input id="address" name="address" placeholder="123 Main St" />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input id="city" name="city" placeholder="New York" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State</Label>
                    <Input id="state" name="state" placeholder="NY" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="zip">ZIP Code</Label>
                    <Input id="zip" name="zip" placeholder="10001" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="plan">Subscription Plan *</Label>
                  <select
                    id="plan"
                    name="plan"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    required
                  >
                    <option value="small">Basic - Up to 5 users</option>
                    <option value="medium">Professional - Up to 20 users</option>
                    <option value="large">Enterprise - Unlimited users</option>
                  </select>
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={createFirmMutation.isPending}>
                  Create Firm
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Firms</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{firmsArray.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Firms</CardTitle>
            <Building2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {firmsArray.filter((f: any) => f.status === 'active').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trial Accounts</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {firmsArray.filter((f: any) => f.status === 'trial').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Engagements</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {firmsArray.reduce((sum: number, f: any) => sum + (f.engagement_count || 0), 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Firms Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>All CPA Firms</CardTitle>
              <CardDescription>
                {filteredFirms.length} of {firmsArray.length} firms
              </CardDescription>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search firms..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Firm Name</TableHead>
                  <TableHead>License</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Plan</TableHead>
                  <TableHead>Users</TableHead>
                  <TableHead>Engagements</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : filteredFirms.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      No CPA firms found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredFirms.map((firm: any) => (
                    <TableRow key={firm.id}>
                      <TableCell className="font-medium">{firm.company_name || 'N/A'}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {firm.license_number || 'N/A'}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="text-sm">{firm.contact_email}</span>
                          <span className="text-xs text-muted-foreground">{firm.contact_phone}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(firm.status)} variant="secondary">
                          {firm.status || 'active'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getPlanColor(firm.company_size)} variant="secondary">
                          {firm.company_size || 'basic'}
                        </Badge>
                      </TableCell>
                      <TableCell>{firm.user_count || 0}</TableCell>
                      <TableCell>{firm.engagement_count || 0}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {firm.created_at ? formatDate(firm.created_at, 'short') : 'N/A'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
