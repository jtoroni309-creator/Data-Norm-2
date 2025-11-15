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
import {
  CreditCard,
  Search,
  Plus,
  Eye,
  XCircle,
  RefreshCw,
  Download,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { api } from '@/lib/api';
import { License, LicenseStatus, PlanType } from '@/types/admin';
import { formatDate, formatCurrency, formatNumber } from '@/lib/utils';

export default function LicensesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const { data: licenses, isLoading } = useQuery({
    queryKey: ['admin-licenses', statusFilter],
    queryFn: () => api.admin.licenses.list(),
  });
  const licensesArray = (licenses as any[]) || [];

  const filteredLicenses = licensesArray.filter((license: License) => {
    const matchesStatus = statusFilter === 'all' || license.status === statusFilter;
    return matchesStatus;
  });

  const getStatusVariant = (status: LicenseStatus) => {
    switch (status) {
      case LicenseStatus.ACTIVE:
        return 'success';
      case LicenseStatus.TRIAL:
        return 'info';
      case LicenseStatus.EXPIRED:
        return 'destructive';
      case LicenseStatus.CANCELLED:
        return 'destructive';
      case LicenseStatus.SUSPENDED:
        return 'warning';
      default:
        return 'default';
    }
  };

  const getPlanColor = (plan: PlanType) => {
    switch (plan) {
      case PlanType.STARTER:
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/20';
      case PlanType.PROFESSIONAL:
        return 'bg-purple-100 text-purple-700 dark:bg-purple-900/20';
      case PlanType.ENTERPRISE:
        return 'bg-orange-100 text-orange-700 dark:bg-orange-900/20';
      case PlanType.CUSTOM:
        return 'bg-green-100 text-green-700 dark:bg-green-900/20';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-900/20';
    }
  };

  const stats = [
    {
      label: 'Total Licenses',
      value: licensesArray.length,
      icon: CreditCard,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      label: 'Active',
      value: licensesArray.filter((l: License) => l.status === LicenseStatus.ACTIVE).length,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      label: 'Trial',
      value: licensesArray.filter((l: License) => l.status === LicenseStatus.TRIAL).length,
      icon: AlertCircle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
    },
    {
      label: 'Expiring Soon',
      value: 5,
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/20',
    },
  ];

  // Mock data for demo
  const mockLicenses: License[] = [
    {
      id: '1',
      customer_id: 'cust-1',
      plan_type: PlanType.ENTERPRISE,
      status: LicenseStatus.ACTIVE,
      seats: 15,
      seats_used: 12,
      features: ['analytics', 'normalize', 'qc', 'api_access'],
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      auto_renew: true,
      billing_cycle: 'monthly' as any,
      price_per_month: 2400,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-11-05T00:00:00Z',
    },
    {
      id: '2',
      customer_id: 'cust-2',
      plan_type: PlanType.PROFESSIONAL,
      status: LicenseStatus.ACTIVE,
      seats: 5,
      seats_used: 4,
      features: ['analytics', 'normalize', 'qc'],
      start_date: '2024-03-15',
      end_date: '2025-03-15',
      auto_renew: true,
      billing_cycle: 'annually',
      price_per_month: 800,
      created_at: '2024-03-15T00:00:00Z',
      updated_at: '2024-11-05T00:00:00Z',
    },
    {
      id: '3',
      customer_id: 'cust-3',
      plan_type: PlanType.TRIAL,
      status: LicenseStatus.TRIAL,
      seats: 3,
      seats_used: 2,
      features: ['analytics', 'normalize'],
      start_date: '2024-11-01',
      end_date: '2024-12-01',
      trial_ends_at: '2024-12-01',
      auto_renew: false,
      billing_cycle: 'monthly' as any,
      price_per_month: 0,
      created_at: '2024-11-01T00:00:00Z',
      updated_at: '2024-11-05T00:00:00Z',
    },
  ];

  const displayLicenses = mockLicenses.length > 0 ? mockLicenses : filteredLicenses;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Licenses</h1>
          <p className="text-muted-foreground">Manage customer licenses and subscriptions</p>
        </div>
        <Button size="lg">
          <Plus className="mr-2 h-4 w-4" />
          Create License
        </Button>
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

      {/* Licenses Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <CardTitle>All Licenses</CardTitle>
              <CardDescription>
                {displayLicenses.length} active subscriptions
              </CardDescription>
            </div>
            <div className="flex flex-col space-y-2 md:flex-row md:items-center md:space-x-2 md:space-y-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search licenses..."
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
                <option value={LicenseStatus.ACTIVE}>Active</option>
                <option value={LicenseStatus.TRIAL}>Trial</option>
                <option value={LicenseStatus.EXPIRED}>Expired</option>
                <option value={LicenseStatus.CANCELLED}>Cancelled</option>
                <option value={LicenseStatus.SUSPENDED}>Suspended</option>
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
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>License ID</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Plan</TableHead>
                    <TableHead>Seats</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>End Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {displayLicenses.map((license: License) => (
                    <TableRow key={license.id}>
                      <TableCell className="font-medium">{license.id}</TableCell>
                      <TableCell>Customer #{license.customer_id}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${getPlanColor(
                            license.plan_type
                          )}`}
                        >
                          {license.plan_type}
                        </span>
                      </TableCell>
                      <TableCell>
                        {license.seats_used} / {license.seats}
                        <div className="mt-1 h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                          <div
                            className="h-full bg-primary"
                            style={{
                              width: `${(license.seats_used / license.seats) * 100}%`,
                            }}
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">
                            {formatCurrency(license.price_per_month)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {license.billing_cycle}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(license.status)}>
                          {license.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p>{formatDate(license.end_date, 'short')}</p>
                          {license.auto_renew && (
                            <p className="text-xs text-muted-foreground flex items-center mt-1">
                              <RefreshCw className="mr-1 h-3 w-3" />
                              Auto-renew
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <XCircle className="h-4 w-4 text-destructive" />
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
