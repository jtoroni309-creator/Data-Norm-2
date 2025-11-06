'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ArrowLeft,
  Edit,
  BarChart3,
  CheckCircle2,
  FileText,
  Users,
  Calendar,
  Clock,
  Building2,
  User,
  GitCompare,
} from 'lucide-react';
import { api } from '@/lib/api';
import { Engagement, EngagementStatus } from '@/types';
import { formatDate } from '@/lib/utils';

export default function EngagementDetailPage() {
  const params = useParams();
  const router = useRouter();
  const engagementId = params.id as string;

  const { data: engagement, isLoading } = useQuery({
    queryKey: ['engagement', engagementId],
    queryFn: () => api.engagements.get(engagementId),
    enabled: !!engagementId,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!engagement) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h2 className="text-2xl font-bold">Engagement not found</h2>
        <Button className="mt-4" onClick={() => router.push('/dashboard/engagements')}>
          Back to Engagements
        </Button>
      </div>
    );
  }

  const getStatusVariant = (status: EngagementStatus) => {
    switch (status) {
      case EngagementStatus.PLANNING:
        return 'default';
      case EngagementStatus.FIELDWORK:
        return 'info';
      case EngagementStatus.REVIEW:
        return 'warning';
      case EngagementStatus.COMPLETED:
        return 'success';
      case EngagementStatus.ARCHIVED:
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/dashboard/engagements')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{engagement.client_name}</h1>
            <p className="text-muted-foreground">
              {engagement.engagement_type} • FYE: {formatDate(engagement.fiscal_year_end, 'short')}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={getStatusVariant(engagement.status)} className="text-sm">
            {engagement.status}
          </Badge>
          <Button variant="outline">
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="cursor-pointer transition-shadow hover:shadow-md">
          <CardContent className="flex items-center space-x-4 pt-6">
            <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900/20">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium">Run Analytics</p>
              <p className="text-xs text-muted-foreground">JE Testing, Anomalies</p>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer transition-shadow hover:shadow-md">
          <CardContent className="flex items-center space-x-4 pt-6">
            <div className="rounded-full bg-purple-100 p-3 dark:bg-purple-900/20">
              <GitCompare className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium">Normalize Data</p>
              <p className="text-xs text-muted-foreground">Account Mapping</p>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer transition-shadow hover:shadow-md">
          <CardContent className="flex items-center space-x-4 pt-6">
            <div className="rounded-full bg-green-100 p-3 dark:bg-green-900/20">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium">Quality Control</p>
              <p className="text-xs text-muted-foreground">Run Policies</p>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer transition-shadow hover:shadow-md">
          <CardContent className="flex items-center space-x-4 pt-6">
            <div className="rounded-full bg-orange-100 p-3 dark:bg-orange-900/20">
              <FileText className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium">Generate Report</p>
              <p className="text-xs text-muted-foreground">Export Results</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
          <TabsTrigger value="files">Files</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Engagement Details */}
            <Card>
              <CardHeader>
                <CardTitle>Engagement Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Building2 className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Client Name</p>
                    <p className="text-sm text-muted-foreground">{engagement.client_name}</p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Engagement Type</p>
                    <p className="text-sm text-muted-foreground">{engagement.engagement_type}</p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Fiscal Year End</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(engagement.fiscal_year_end, 'long')}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Status</p>
                    <Badge variant={getStatusVariant(engagement.status)}>{engagement.status}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Timeline</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Created</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(engagement.created_at, 'long')}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Last Updated</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(engagement.updated_at, 'relative')}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Engagement Statistics</CardTitle>
              <CardDescription>Key metrics and progress indicators</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="space-y-2">
                  <p className="text-2xl font-bold">156</p>
                  <p className="text-sm text-muted-foreground">Journal Entries Tested</p>
                </div>
                <div className="space-y-2">
                  <p className="text-2xl font-bold">12</p>
                  <p className="text-sm text-muted-foreground">Anomalies Detected</p>
                </div>
                <div className="space-y-2">
                  <p className="text-2xl font-bold">98%</p>
                  <p className="text-sm text-muted-foreground">Mapping Accuracy</p>
                </div>
                <div className="space-y-2">
                  <p className="text-2xl font-bold">45</p>
                  <p className="text-sm text-muted-foreground">QC Policies Passed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="team" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>People working on this engagement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Mock team members */}
                {[
                  { name: 'John Smith', role: 'Partner', email: 'john.smith@firm.com' },
                  { name: 'Sarah Johnson', role: 'Manager', email: 'sarah.johnson@firm.com' },
                  { name: 'Mike Davis', role: 'Senior', email: 'mike.davis@firm.com' },
                ].map((member, index) => (
                  <div key={index} className="flex items-center justify-between rounded-lg border p-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                        {member.name
                          .split(' ')
                          .map((n) => n[0])
                          .join('')}
                      </div>
                      <div>
                        <p className="font-medium">{member.name}</p>
                        <p className="text-sm text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <Badge>{member.role}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest updates and actions on this engagement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Mock activity feed */}
                {[
                  {
                    action: 'Analytics completed',
                    user: 'Sarah Johnson',
                    time: '2 hours ago',
                    icon: BarChart3,
                  },
                  {
                    action: 'QC policies executed',
                    user: 'Mike Davis',
                    time: '5 hours ago',
                    icon: CheckCircle2,
                  },
                  {
                    action: 'Account mapping updated',
                    user: 'John Smith',
                    time: '1 day ago',
                    icon: GitCompare,
                  },
                ].map((activity, index) => (
                  <div key={index} className="flex items-start space-x-4">
                    <div className="rounded-full bg-muted p-2">
                      <activity.icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-sm text-muted-foreground">
                        by {activity.user} • {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="files" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Files & Documents</CardTitle>
              <CardDescription>Uploaded files and generated reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 text-lg font-semibold">No files yet</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  Upload files or generate reports to see them here
                </p>
                <Button className="mt-4">Upload Files</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
