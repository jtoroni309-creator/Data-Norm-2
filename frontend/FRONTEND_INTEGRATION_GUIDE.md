# Frontend Integration Guide
## Connecting Engagement, Disclosures, and Reporting Services to UI

---

## ✅ What's Been Implemented

### 1. **API Client Expansion** (`src/lib/api.ts`)

All service endpoints have been added to the API client:

####  Engagement Service
- ✅ Full CRUD operations
- ✅ **State transitions** (`transition()`)
- ✅ Team member management
- ✅ Binder tree operations
- ✅ Workpaper management

#### Disclosures Service
- ✅ Template management
- ✅ Engagement disclosures
- ✅ AI draft generation
- ✅ Checklist management

#### Reporting Service
- ✅ Report templates
- ✅ Report generation
- ✅ E-signature management
- ✅ Opinion generation
- ✅ PDF download

#### Confirmations Service
- ✅ Wire/bank confirmations
- ✅ Letter generation
- ✅ Response tracking
- ✅ Summary statistics

---

## 🎨 UI Component Patterns

### Engagement Workflow Component

**File:** `src/components/engagements/engagement-workflow.tsx`

```typescript
'use client';

import { useState } from 'use';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChevronRight, Lock, CheckCircle2, XCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from '@/hooks/use-toast';

interface EngagementWorkflowProps {
  engagement_id: string;
}

const WORKFLOW_STATES = [
  { status: 'draft', label: 'Draft', icon: '📝' },
  { status: 'planning', label: 'Planning', icon: '📋' },
  { status: 'fieldwork', label: 'Fieldwork', icon: '🔍' },
  { status: 'review', label: 'Review', icon: '👁️' },
  { status: 'finalized', label: 'Finalized', icon: '✅' },
];

const VALID_TRANSITIONS: Record<string, string[]> = {
  draft: ['planning'],
  planning: ['fieldwork', 'draft'],
  fieldwork: ['review', 'planning'],
  review: ['finalized', 'fieldwork'],
  finalized: [],
};

export function EngagementWorkflow({ engagementId }: EngagementWorkflowProps) {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  // Fetch engagement data
  const { data: engagement, isLoading } = useQuery({
    queryKey: ['engagement', engagementId],
    queryFn: () => api.engagements.get(engagementId),
  });

  // Transition mutation
  const transitionMutation = useMutation({
    mutationFn: ({ newStatus }: { newStatus: string }) =>
      api.engagements.transition(engagementId, newStatus),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['engagement', engagementId] });
      toast({ title: 'Success', description: 'Engagement status updated' });
      setError(null);
    },
    onError: (err: any) => {
      const errorMsg = err.response?.data?.detail || 'Failed to transition status';
      setError(errorMsg);
      toast({ title: 'Error', description: errorMsg, variant: 'destructive' });
    },
  });

  const handleTransition = (newStatus: string) => {
    transitionMutation.mutate({ newStatus });
  };

  if (isLoading) return <div>Loading...</div>;
  if (!engagement) return <div>Engagement not found</div>;

  const currentStatus = engagement.status;
  const validNext = VALID_TRANSITIONS[currentStatus] || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Engagement Workflow</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Current Status */}
        <div className="mb-6">
          <div className="text-sm text-muted-foreground mb-2">Current Status</div>
          <Badge variant="default" className="text-lg px-4 py-2">
            {currentStatus.toUpperCase()}
          </Badge>
          {engagement.locked_at && (
            <div className="mt-2 flex items-center text-sm text-amber-600">
              <Lock className="h-4 w-4 mr-2" />
              Locked on {new Date(engagement.locked_at).toLocaleDateString()}
            </div>
          )}
        </div>

        {/* Workflow Timeline */}
        <div className="space-y-4 mb-6">
          {WORKFLOW_STATES.map((state, index) => {
            const isComplete = WORKFLOW_STATES.findIndex(s => s.status === currentStatus) > index;
            const isCurrent = state.status === currentStatus;
            const isNext = validNext.includes(state.status);

            return (
              <div key={state.status} className="flex items-center">
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  isComplete ? 'bg-green-500 text-white' :
                  isCurrent ? 'bg-blue-500 text-white' :
                  'bg-gray-200 text-gray-500'
                }`}>
                  {isComplete ? <CheckCircle2 className="h-5 w-5" /> : <span>{state.icon}</span>}
                </div>
                <div className="ml-4 flex-1">
                  <div className={`font-medium ${isCurrent ? 'text-blue-600' : ''}`}>
                    {state.label}
                  </div>
                  {isNext && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-1"
                      onClick={() => handleTransition(state.status)}
                      disabled={transitionMutation.isPending}
                    >
                      Move to {state.label} <ChevronRight className="ml-2 h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-start">
              <XCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3" />
              <div>
                <div className="font-medium text-red-800">Cannot Transition</div>
                <div className="text-sm text-red-700 mt-1">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Finalization Requirements */}
        {currentStatus === 'review' && (
          <div className="mt-6 bg-amber-50 border border-amber-200 rounded-md p-4">
            <div className="font-medium text-amber-800 mb-2">Finalization Requirements</div>
            <ul className="text-sm text-amber-700 space-y-1">
              <li>✓ All blocking QC policies must pass</li>
              <li>✓ Partner signature must be completed</li>
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

### Disclosures Management Page

**File:** `src/app/(dashboard)/dashboard/disclosures/[engagementId]/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, FileText, Sparkles, CheckSquare } from 'lucide-react';
import { api } from '@/lib/api';

export default function DisclosuresPage({ params }: { params: { engagementId: string } }) {
  const { engagementId } = params;
  const queryClient = useQueryClient();
  const [selectedStandard, setSelectedStandard] = useState('GAAP');

  // Fetch disclosures
  const { data: disclosures = [], isLoading } = useQuery({
    queryKey: ['disclosures', engagementId],
    queryFn: () => api.disclosures.byEngagement.list(engagementId),
  });

  // Fetch checklist
  const { data: checklist } = useQuery({
    queryKey: ['disclosure-checklist', engagementId, selectedStandard],
    queryFn: () => api.disclosures.checklists.get(engagementId, selectedStandard),
  });

  // AI Draft Generation
  const aiDraftMutation = useMutation({
    mutationFn: (disclosureId: string) =>
      api.disclosures.byEngagement.aiDraft(disclosureId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['disclosures', engagementId] });
    },
  });

  // Create disclosure
  const createMutation = useMutation({
    mutationFn: (data: any) =>
      api.disclosures.byEngagement.create(engagementId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['disclosures', engagementId] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Disclosures</h1>
          <p className="text-muted-foreground">Manage financial statement disclosures</p>
        </div>
        <Button onClick={() => createMutation.mutate({ title: 'New Disclosure' })}>
          <Plus className="mr-2 h-4 w-4" />
          New Disclosure
        </Button>
      </div>

      <Tabs defaultValue="disclosures">
        <TabsList>
          <TabsTrigger value="disclosures">
            <FileText className="mr-2 h-4 w-4" />
            Disclosures
          </TabsTrigger>
          <TabsTrigger value="checklist">
            <CheckSquare className="mr-2 h-4 w-4" />
            Checklist
          </TabsTrigger>
        </TabsList>

        <TabsContent value="disclosures">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {disclosures.map((disclosure: any) => (
              <Card key={disclosure.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{disclosure.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">
                      Status: {disclosure.status}
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => aiDraftMutation.mutate(disclosure.id)}
                        disabled={aiDraftMutation.isPending}
                      >
                        <Sparkles className="mr-2 h-4 w-4" />
                        AI Draft
                      </Button>
                      <Button size="sm" variant="ghost">
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="checklist">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Disclosure Checklist - {selectedStandard}</CardTitle>
                <select
                  value={selectedStandard}
                  onChange={(e) => setSelectedStandard(e.target.value)}
                  className="rounded-md border px-3 py-2"
                >
                  <option value="GAAP">US GAAP</option>
                  <option value="IFRS">IFRS</option>
                  <option value="GASB">GASB</option>
                </select>
              </div>
            </CardHeader>
            <CardContent>
              {checklist?.items?.map((item: any, index: number) => (
                <div key={index} className="flex items-center space-x-3 py-2">
                  <input type="checkbox" checked={item.completed} readOnly />
                  <span className={item.completed ? 'line-through text-muted-foreground' : ''}>
                    {item.description}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

### Reporting & Signatures Page

**File:** `src/app/(dashboard)/dashboard/reporting/[engagementId]/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { FileText, Download, Send, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { api } from '@/lib/api';

export default function ReportingPage({ params }: { params: { engagementId: string } }) {
  const { engagementId } = params;
  const queryClient = useQueryClient();

  // Fetch reports
  const { data: reports = [] } = useQuery({
    queryKey: ['reports', engagementId],
    queryFn: () => api.reporting.reports.list(engagementId),
  });

  // Generate report
  const generateMutation = useMutation({
    mutationFn: (reportId: string) =>
      api.reporting.reports.generate(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', engagementId] });
    },
  });

  // Send for signature
  const sendSignatureMutation = useMutation({
    mutationFn: ({ reportId, signers }: { reportId: string; signers: any[] }) =>
      api.reporting.signatures.create(reportId, { signers }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', engagementId] });
    },
  });

  // Download report
  const handleDownload = async (reportId: string, filename: string) => {
    const blob = await api.reporting.reports.download(reportId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'report.pdf';
    a.click();
  };

  const getSignatureStatus = (report: any) => {
    if (!report.signature_status) return null;

    const statusConfig = {
      completed: { icon: CheckCircle2, color: 'text-green-600', label: 'Completed' },
      sent: { icon: Send, color: 'text-blue-600', label: 'Sent' },
      pending: { icon: Clock, color: 'text-amber-600', label: 'Pending' },
      declined: { icon: XCircle, color: 'text-red-600', label: 'Declined' },
    };

    const config = statusConfig[report.signature_status as keyof typeof statusConfig];
    if (!config) return null;

    const Icon = config.icon;
    return (
      <div className={`flex items-center ${config.color}`}>
        <Icon className="h-4 w-4 mr-2" />
        {config.label}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">Generate and manage engagement reports</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Engagement Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Signature Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reports.map((report: any) => (
                <TableRow key={report.id}>
                  <TableCell className="font-medium">{report.report_type}</TableCell>
                  <TableCell>
                    <Badge variant={report.status === 'finalized' ? 'success' : 'default'}>
                      {report.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{getSignatureStatus(report)}</TableCell>
                  <TableCell>{new Date(report.created_at).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      {report.status === 'draft' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => generateMutation.mutate(report.id)}
                        >
                          Generate
                        </Button>
                      )}
                      {report.file_path && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDownload(report.id, report.file_name)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                      {report.status === 'finalized' && !report.signature_status && (
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm">
                              <Send className="mr-2 h-4 w-4" />
                              Send for Signature
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Send for E-Signature</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <p className="text-sm text-muted-foreground">
                                Configure signers for this report
                              </p>
                              {/* Add signer configuration UI here */}
                              <Button
                                onClick={() =>
                                  sendSignatureMutation.mutate({
                                    reportId: report.id,
                                    signers: [
                                      { name: 'Partner', email: 'partner@firm.com', role: 'partner' },
                                    ],
                                  })
                                }
                              >
                                Send
                              </Button>
                            </div>
                          </DialogContent>
                        </Dialog>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 🔧 Integration Checklist

### 1. Update Sidebar Navigation

**File:** `src/components/layout/sidebar.tsx`

Add navigation links:

```typescript
const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Engagements', href: '/dashboard/engagements', icon: FolderOpen },
  { name: 'Disclosures', href: '/dashboard/disclosures', icon: FileText },
  { name: 'Reporting', href: '/dashboard/reporting', icon: FileCheck },
  { name: 'QC', href: '/dashboard/qc', icon: CheckCircle },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart },
];
```

### 2. Create Route Files

Create these files in `src/app/(dashboard)/dashboard/`:

- ✅ `disclosures/page.tsx` - Disclosures list
- ✅ `disclosures/[engagementId]/page.tsx` - Engagement disclosures
- ✅ `reporting/page.tsx` - Reports list
- ✅ `reporting/[engagementId]/page.tsx` - Engagement reports
- ✅ `engagements/[id]/workflow/page.tsx` - Engagement workflow

### 3. Add TypeScript Types

**File:** `src/types/index.ts`

```typescript
// Engagement Workflow
export enum EngagementStatus {
  DRAFT = 'draft',
  PLANNING = 'planning',
  FIELDWORK = 'fieldwork',
  REVIEW = 'review',
  FINALIZED = 'finalized',
}

export interface Engagement {
  id: string;
  client_id: string;
  name: string;
  engagement_type: string;
  status: EngagementStatus;
  fiscal_year_end: string;
  locked_at?: string;
  locked_by?: string;
  created_at: string;
  updated_at: string;
}

// Disclosures
export interface Disclosure {
  id: string;
  engagement_id: string;
  title: string;
  content: string;
  status: 'draft' | 'review' | 'approved';
  disclosure_type: string;
  created_at: string;
}

export interface DisclosureChecklist {
  standard: string;
  items: ChecklistItem[];
  completed_count: number;
  total_count: number;
}

export interface ChecklistItem {
  id: string;
  description: string;
  completed: boolean;
  reference: string;
}

// Reporting
export interface Report {
  id: string;
  engagement_id: string;
  report_type: 'audit_opinion' | 'review_opinion' | 'compilation_report';
  title: string;
  status: 'draft' | 'generated' | 'finalized';
  file_name?: string;
  file_path?: string;
  signature_status?: 'pending' | 'sent' | 'completed' | 'declined';
  created_at: string;
}

export interface SignatureEnvelope {
  id: string;
  report_id: string;
  status: 'pending' | 'sent' | 'delivered' | 'signed' | 'completed' | 'declined';
  signers: Signer[];
  created_at: string;
}

export interface Signer {
  name: string;
  email: string;
  role: string;
  signed_at?: string;
}
```

---

## 📋 Usage Examples

### 1. Transition Engagement Status

```typescript
import { api } from '@/lib/api';

// Transition from planning to fieldwork
await api.engagements.transition(engagementId, 'fieldwork');
```

### 2. Generate AI Disclosure Draft

```typescript
import { api } from '@/lib/api';

// Generate AI draft for disclosure
const draft = await api.disclosures.byEngagement.aiDraft(disclosureId);
```

### 3. Generate and Download Report

```typescript
import { api } from '@/lib/api';

// Generate report
await api.reporting.reports.generate(reportId);

// Download PDF
const blob = await api.reporting.reports.download(reportId);
const url = window.URL.createObjectURL(blob);
window.open(url);
```

### 4. Send Report for E-Signature

```typescript
import { api } from '@/lib/api';

// Create signature envelope
const envelope = await api.reporting.signatures.create(reportId, {
  signers: [
    { name: 'John Partner', email: 'partner@firm.com', role: 'partner' },
    { name: 'Jane Manager', email: 'manager@firm.com', role: 'manager' },
  ],
});

// Send envelope
await api.reporting.signatures.send(envelope.id);
```

---

## 🚀 Next Steps

1. **Create UI Pages**
   - Copy the component examples above
   - Customize styling to match your design system
   - Add form validation and error handling

2. **Add Navigation**
   - Update sidebar with new routes
   - Add breadcrumbs for nested pages

3. **Implement State Management**
   - Use React Query for server state
   - Use Zustand/Redux for client state if needed

4. **Add Error Handling**
   - Create error boundary components
   - Add toast notifications for user feedback

5. **Testing**
   - Write unit tests for components
   - Add integration tests for workflows
   - Test error scenarios

---

## 📚 API Reference

All API methods are now available in `src/lib/api.ts`:

- `api.engagements.*` - Engagement operations
- `api.disclosures.*` - Disclosure management
- `api.reporting.*` - Report generation
- `api.confirmations.*` - Confirmation management

Each endpoint follows REST conventions and returns typed responses.

---

## ⚠️ Important Notes

### Error Handling

All API calls should be wrapped in try/catch:

```typescript
try {
  await api.engagements.transition(id, newStatus);
  toast({ title: 'Success', description: 'Status updated' });
} catch (error: any) {
  const message = error.response?.data?.detail || 'Operation failed';
  toast({ title: 'Error', description: message, variant: 'destructive' });
}
```

### Loading States

Always show loading indicators:

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['engagement', id],
  queryFn: () => api.engagements.get(id),
});

if (isLoading) return <Skeleton />;
if (error) return <ErrorAlert />;
```

### Permissions

Check user permissions before showing actions:

```typescript
const canFinalize = user.role === 'partner' && engagement.status === 'review';
```

---

## 🎯 Summary

All three priority services are now fully integrated into the frontend API client:

✅ **Engagement Management** - Complete workflow, team, binder, workpapers
✅ **Disclosures** - Templates, checklists, AI drafts
✅ **Reporting** - Generation, signatures, downloads

Use the component patterns above as templates for building your UI pages!
