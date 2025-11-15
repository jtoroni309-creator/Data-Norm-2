'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  ArrowLeft,
  Edit,
  Ban,
  CheckCircle,
  Mail,
  Phone,
  Building2,
  Calendar,
  Clock,
  CreditCard,
  BarChart3,
  FileText,
  Activity,
  Shield,
} from 'lucide-react';
import { api } from '@/lib/api';
import { Customer, CustomerStatus } from '@/types/admin';
import { formatDate, formatCurrency, formatNumber } from '@/lib/utils';
import { FraudDetectionSettings } from '@/components/admin/fraud-detection-settings';

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.id as string;

  const { data: customer, isLoading } = useQuery({
    queryKey: ['admin-customer', customerId],
    queryFn: () => api.admin.customers.get(customerId),
  });

  const { data: licenses = [] } = useQuery({
    queryKey: ['admin-customer-licenses', customerId],
    queryFn: () => api.admin.licenses.list(customerId),
  });

  const { data: usage } = useQuery({
    queryKey: ['admin-customer-usage', customerId],
    queryFn: () => api.admin.usage.getByCustomer(customerId),
  });

  const { data: invoices = [] } = useQuery({
    queryKey: ['admin-customer-invoices', customerId],
    queryFn: () => api.admin.invoices.list(customerId),
  });

  const { data: activity = [] } = useQuery({
    queryKey: ['admin-customer-activity', customerId],
    queryFn: () => api.admin.activity.list(customerId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const mockCustomer: Customer = (customer as Customer) || {
    id: customerId,
    company_name: 'Acme Corporation',
    contact_name: 'John Smith',
    contact_email: 'john.smith@acme.com',
    contact_phone: '+1 (555) 123-4567',
    industry: 'Technology',
    company_size: 'medium',
    status: CustomerStatus.ACTIVE,
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-11-05T00:00:00Z',
    last_login: '2024-11-05T14:30:00Z',
  };

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
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/admin/customers')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{mockCustomer.company_name}</h1>
            <p className="text-muted-foreground">Customer ID: {customerId}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={getStatusVariant(mockCustomer.status)} className="text-sm">
            {mockCustomer.status}
          </Badge>
          <Button variant="outline">
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          {mockCustomer.status === CustomerStatus.ACTIVE ? (
            <Button variant="outline">
              <Ban className="mr-2 h-4 w-4" />
              Suspend
            </Button>
          ) : (
            <Button variant="outline">
              <CheckCircle className="mr-2 h-4 w-4" />
              Activate
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="licenses">Licenses</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="fraud-detection">
            <Shield className="mr-2 h-4 w-4" />
            Fraud Detection
          </TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Customer Information */}
            <Card>
              <CardHeader>
                <CardTitle>Customer Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Building2 className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Company Name</p>
                    <p className="text-sm text-muted-foreground">{mockCustomer.company_name}</p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Mail className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Contact Email</p>
                    <p className="text-sm text-muted-foreground">{mockCustomer.contact_email}</p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Phone className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Contact Phone</p>
                    <p className="text-sm text-muted-foreground">
                      {mockCustomer.contact_phone || 'N/A'}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Building2 className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Industry</p>
                    <p className="text-sm text-muted-foreground">
                      {mockCustomer.industry || 'N/A'}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Building2 className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Company Size</p>
                    <p className="text-sm text-muted-foreground capitalize">
                      {mockCustomer.company_size || 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Account Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Account Timeline</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Created</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(mockCustomer.created_at, 'long')}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Last Updated</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(mockCustomer.updated_at, 'relative')}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Activity className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Last Login</p>
                    <p className="text-sm text-muted-foreground">
                      {mockCustomer.last_login
                        ? formatDate(mockCustomer.last_login, 'relative')
                        : 'Never'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-3xl font-bold">{licenses.length || 1}</p>
                  <p className="text-sm text-muted-foreground">Active Licenses</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-3xl font-bold">15</p>
                  <p className="text-sm text-muted-foreground">Total Users</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-3xl font-bold">{formatCurrency(2400)}</p>
                  <p className="text-sm text-muted-foreground">Monthly Revenue</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-3xl font-bold">342</p>
                  <p className="text-sm text-muted-foreground">Total Engagements</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="licenses" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Licenses</CardTitle>
              <CardDescription>Manage customer licenses and subscriptions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1].map((_, index) => (
                  <div key={index} className="rounded-lg border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <CreditCard className="h-5 w-5 text-muted-foreground" />
                          <p className="font-medium">Enterprise Plan</p>
                          <Badge variant="success">Active</Badge>
                        </div>
                        <div className="mt-2 grid gap-2 text-sm text-muted-foreground md:grid-cols-3">
                          <span>15 seats (12 used)</span>
                          <span>Renews: Dec 31, 2024</span>
                          <span>{formatCurrency(2400)}/month</span>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Manage
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="usage" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Usage Metrics</CardTitle>
              <CardDescription>Resource consumption and platform usage</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Engagements</p>
                  <p className="mt-1 text-2xl font-bold">342</p>
                  <p className="text-xs text-muted-foreground">+23 this month</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Analytics Runs</p>
                  <p className="mt-1 text-2xl font-bold">1,247</p>
                  <p className="text-xs text-muted-foreground">+156 this month</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Storage Used</p>
                  <p className="mt-1 text-2xl font-bold">42.3 GB</p>
                  <p className="text-xs text-muted-foreground">of 100 GB limit</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="invoices" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Invoices</CardTitle>
              <CardDescription>Billing history and payment records</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Invoice #</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {[1, 2, 3].map((_, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">INV-{2024000 + index}</TableCell>
                        <TableCell>{formatDate(new Date(), 'short')}</TableCell>
                        <TableCell>{formatCurrency(2400)}</TableCell>
                        <TableCell>
                          <Badge variant="success">Paid</Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm">
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fraud-detection" className="space-y-4">
          <FraudDetectionSettings customerId={customerId} />
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Activity Log</CardTitle>
              <CardDescription>Recent customer actions and events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((_, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">User logged in</p>
                      <p className="text-sm text-muted-foreground">
                        john.smith@acme.com • {formatDate(new Date(), 'relative')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
