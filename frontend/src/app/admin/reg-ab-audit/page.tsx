/**
 * Regulation A/B Audit Admin Page
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { RegABAuditSettings } from '@/components/admin/reg-ab-audit-settings';
import { Search } from 'lucide-react';

export default function RegABAuditAdminPage() {
  const [organizationId, setOrganizationId] = useState('');
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null);

  const handleSearch = () => {
    if (organizationId.trim()) {
      setSelectedOrgId(organizationId.trim());
    }
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Regulation A/B Audit Settings</h1>
        <p className="text-muted-foreground mt-2">
          Configure AI-powered CMBS loan audit features for organizations
        </p>
      </div>

      {/* Organization Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Select Organization</CardTitle>
          <CardDescription>
            Enter the organization ID to manage Regulation A/B audit settings
          </CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <div className="flex-1 grid gap-2">
            <Label htmlFor="org-id">Organization ID</Label>
            <Input
              id="org-id"
              placeholder="Enter organization UUID"
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSearch();
                }
              }}
            />
          </div>
          <div className="flex items-end">
            <Button onClick={handleSearch}>
              <Search className="mr-2 h-4 w-4" />
              Load Settings
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Settings Component */}
      {selectedOrgId && (
        <RegABAuditSettings organizationId={selectedOrgId} />
      )}
    </div>
  );
}
