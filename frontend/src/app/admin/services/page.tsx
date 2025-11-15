'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Server,
  Database,
  Cloud,
  Cpu,
  HardDrive,
  Activity,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Settings2,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface Service {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'stopped' | 'error' | 'starting' | 'stopping';
  enabled: boolean;
  icon: any;
  category: 'core' | 'analytics' | 'integrations' | 'storage';
  health: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  uptime: string;
  requests_per_min: number;
  error_rate: number;
}

// Mock services data - would come from API
const mockServices: Service[] = [
  {
    id: 'identity',
    name: 'Identity Service',
    description: 'Authentication and authorization service',
    status: 'error',
    enabled: true,
    icon: Server,
    category: 'core',
    health: 'unhealthy',
    uptime: '0%',
    requests_per_min: 0,
    error_rate: 100,
  },
  {
    id: 'ingestion',
    name: 'Data Ingestion',
    description: 'Process and import financial data',
    status: 'running',
    enabled: true,
    icon: Database,
    category: 'core',
    health: 'healthy',
    uptime: '99.9%',
    requests_per_min: 125,
    error_rate: 0.1,
  },
  {
    id: 'normalize',
    name: 'Normalization Service',
    description: 'AI-powered data normalization and mapping',
    status: 'running',
    enabled: true,
    icon: Cpu,
    category: 'core',
    health: 'healthy',
    uptime: '99.8%',
    requests_per_min: 85,
    error_rate: 0.2,
  },
  {
    id: 'analytics',
    name: 'Analytics Engine',
    description: 'JE testing and anomaly detection',
    status: 'error',
    enabled: true,
    icon: Activity,
    category: 'analytics',
    health: 'unhealthy',
    uptime: '0%',
    requests_per_min: 0,
    error_rate: 100,
  },
  {
    id: 'qc',
    name: 'Quality Control',
    description: 'Automated quality checks and compliance',
    status: 'running',
    enabled: true,
    icon: CheckCircle2,
    category: 'analytics',
    health: 'healthy',
    uptime: '99.7%',
    requests_per_min: 45,
    error_rate: 0.3,
  },
  {
    id: 'reporting',
    name: 'Reporting Service',
    description: 'Generate audit reports and disclosures',
    status: 'running',
    enabled: true,
    icon: Server,
    category: 'analytics',
    health: 'healthy',
    uptime: '99.9%',
    requests_per_min: 30,
    error_rate: 0.1,
  },
  {
    id: 'connectors',
    name: 'Data Connectors',
    description: 'QuickBooks, Xero, and other integrations',
    status: 'error',
    enabled: false,
    icon: Cloud,
    category: 'integrations',
    health: 'unhealthy',
    uptime: '0%',
    requests_per_min: 0,
    error_rate: 100,
  },
  {
    id: 'minio',
    name: 'Object Storage',
    description: 'File and document storage service',
    status: 'running',
    enabled: true,
    icon: HardDrive,
    category: 'storage',
    health: 'healthy',
    uptime: '100%',
    requests_per_min: 200,
    error_rate: 0,
  },
];

export default function ServicesPage() {
  const [services] = useState<Service[]>(mockServices);
  const queryClient = useQueryClient();

  const toggleServiceMutation = useMutation({
    mutationFn: async ({ serviceId, enabled }: { serviceId: string; enabled: boolean }) => {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return { serviceId, enabled };
    },
    onSuccess: (data) => {
      toast.success(
        `Service ${data.enabled ? 'enabled' : 'disabled'} successfully!`
      );
      queryClient.invalidateQueries({ queryKey: ['services'] });
    },
    onError: () => {
      toast.error('Failed to toggle service');
    },
  });

  const restartServiceMutation = useMutation({
    mutationFn: async (serviceId: string) => {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return serviceId;
    },
    onSuccess: () => {
      toast.success('Service restarted successfully!');
      queryClient.invalidateQueries({ queryKey: ['services'] });
    },
    onError: () => {
      toast.error('Failed to restart service');
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'stopped':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'starting':
      case 'stopping':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'unhealthy':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  const categorizedServices = {
    core: services.filter((s) => s.category === 'core'),
    analytics: services.filter((s) => s.category === 'analytics'),
    integrations: services.filter((s) => s.category === 'integrations'),
    storage: services.filter((s) => s.category === 'storage'),
  };

  const renderServiceCard = (service: Service) => (
    <Card key={service.id} className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <service.icon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">{service.name}</CardTitle>
              <CardDescription className="text-sm">{service.description}</CardDescription>
            </div>
          </div>
          <Badge className={getStatusColor(service.status)} variant="secondary">
            {service.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Health Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getHealthIcon(service.health)}
            <span className="text-sm font-medium capitalize">{service.health}</span>
          </div>
          <span className="text-sm text-muted-foreground">Uptime: {service.uptime}</span>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Requests/min</p>
            <p className="font-medium">{service.requests_per_min}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Error Rate</p>
            <p className={cn('font-medium', service.error_rate > 1 ? 'text-red-600' : '')}>
              {service.error_rate}%
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between border-t pt-4">
          <div className="flex items-center space-x-2">
            <Switch
              id={`${service.id}-enabled`}
              checked={service.enabled}
              onCheckedChange={(checked) =>
                toggleServiceMutation.mutate({ serviceId: service.id, enabled: checked })
              }
              disabled={toggleServiceMutation.isPending}
            />
            <Label htmlFor={`${service.id}-enabled`} className="text-sm">
              {service.enabled ? 'Enabled' : 'Disabled'}
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => restartServiceMutation.mutate(service.id)}
              disabled={!service.enabled || restartServiceMutation.isPending}
            >
              <RefreshCw
                className={cn(
                  'h-4 w-4 mr-1',
                  restartServiceMutation.isPending && 'animate-spin'
                )}
              />
              Restart
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const healthyCount = services.filter((s) => s.health === 'healthy').length;
  const unhealthyCount = services.filter((s) => s.health === 'unhealthy').length;
  const enabledCount = services.filter((s) => s.enabled).length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Services & Features</h1>
          <p className="text-muted-foreground">
            Manage and monitor all backend services and features
          </p>
        </div>
        <Button variant="outline">
          <Settings2 className="mr-2 h-4 w-4" />
          Global Settings
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Services</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{services.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Healthy</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{healthyCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unhealthy</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{unhealthyCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enabled</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{enabledCount}/{services.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Core Services */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Core Services</h2>
          <p className="text-sm text-muted-foreground">Essential system services</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {categorizedServices.core.map(renderServiceCard)}
        </div>
      </div>

      {/* Analytics Services */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Analytics Services</h2>
          <p className="text-sm text-muted-foreground">AI-powered analysis and testing</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {categorizedServices.analytics.map(renderServiceCard)}
        </div>
      </div>

      {/* Integration Services */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Integration Services</h2>
          <p className="text-sm text-muted-foreground">External data connectors</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {categorizedServices.integrations.map(renderServiceCard)}
        </div>
      </div>

      {/* Storage Services */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Storage Services</h2>
          <p className="text-sm text-muted-foreground">Data persistence and file storage</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {categorizedServices.storage.map(renderServiceCard)}
        </div>
      </div>
    </div>
  );
}
