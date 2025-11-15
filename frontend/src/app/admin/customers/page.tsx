'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
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
import {
  Users,
  Search,
  Plus,
  Eye,
  Edit,
  Ban,
  CheckCircle,
  MoreVertical,
  Download,
} from 'lucide-react';
import { api } from '@/lib/api';
import { Customer, CustomerStatus } from '@/types/admin';
import { formatDate } from '@/lib/utils';
import { toast } from 'sonner';

export default function CustomersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const { data: customers , isLoading, refetch } = useQuery({
    queryKey: ['admin-customers', statusFilter],
    queryFn: () => api.admin.customers.list({ status: statusFilter !== 'all' ? statusFilter : undefined }),
  const customersArray = (customers as any[]) || [];
  });

  const suspendMutation = useMutation({
    mutationFn: (customerId: string) => api.admin.customers.suspend(customerId),
    onSuccess: () => {
      toast.success('Customer suspended successfully');
      refetch();
    },
    onError: () => {
      toast.error('Failed to suspend customer');
    },
  });

  const activateMutation = useMutation({
    mutationFn: (customerId: string) => api.admin.customers.activate(customerId),
    onSuccess: () => {
      toast.success('Customer activated successfully');
      refetch();
    },
    onError: () => {
      toast.error('Failed to activate customer');
    },
  });

  const filteredCustomers = customersArray.filter((customer: Customer) =>
    customer.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.contact_email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusVariant = (status: CustomerStatus) => {
    switch (status) {
      case CustomerStatus.ACTIVE:
        return 'success';
      case CustomerStatus.TRIAL:
        return 'info';
      case CustomerStatus.SUSPENDED:
        return 'warning';
      case CustomerStatus.CANCELLED:
        return 'destructive';
      case CustomerStatus.PENDING:
        return 'default';
      default:
        return 'default';
    }
  };

  const stats = [
    {
      label: 'Total Customers',
      value: customersArray.length,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      label: 'Active',
      value: customersArray.filter((c: Customer) => c.status === CustomerStatus.ACTIVE).length,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      label: 'Trial',
      value: customersArray.filter((c: Customer) => c.status === CustomerStatus.TRIAL).length,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
    },
    {
      label: 'Suspended',
      value: customersArray.filter((c: Customer) => c.status === CustomerStatus.SUSPENDED).length,
      icon: Ban,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/20',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Customers</h1>
          <p className="text-muted-foreground">Manage customer accounts and licenses</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg">
              <Plus className="mr-2 h-4 w-4" />
              Add Customer
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Customer</DialogTitle>
            </DialogHeader>
            <div className="py-4">
              <p className="text-sm text-muted-foreground">
                Customer creation form will be implemented here
              </p>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                  <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                </div>
                <div className={`rounded-full p-3 ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Customers Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <CardTitle>All Customers</CardTitle>
              <CardDescription>
                {filteredCustomers.length} of {customersArray.length} customers
              </CardDescription>
            </div>
            <div className="flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search customers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 md:w-[300px]"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="all">All Status</option>
                <option value={CustomerStatus.ACTIVE}>Active</option>
                <option value={CustomerStatus.TRIAL}>Trial</option>
                <option value={CustomerStatus.SUSPENDED}>Suspended</option>
                <option value={CustomerStatus.CANCELLED}>Cancelled</option>
                <option value={CustomerStatus.PENDING}>Pending</option>
              </select>
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          ) : filteredCustomers.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Users className="h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No customers found</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {searchQuery || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Get started by adding your first customer'}
              </p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Company</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Industry</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Last Login</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCustomers.map((customer: Customer) => (
                    <TableRow key={customer.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{customer.company_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {customer.company_size || 'N/A'}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{customer.contact_name}</p>
                          <p className="text-sm text-muted-foreground">{customer.contact_email}</p>
                        </div>
                      </TableCell>
                      <TableCell>{customer.industry || 'N/A'}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(customer.status)}>
                          {customer.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(customer.created_at, 'short')}</TableCell>
                      <TableCell>
                        {customer.last_login
                          ? formatDate(customer.last_login, 'relative')
                          : 'Never'}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => (window.location.href = `/admin/customers/${customer.id}`)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          {customer.status === CustomerStatus.ACTIVE ? (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => suspendMutation.mutate(customer.id)}
                            >
                              <Ban className="h-4 w-4 text-destructive" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => activateMutation.mutate(customer.id)}
                            >
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            </Button>
                          )}
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
