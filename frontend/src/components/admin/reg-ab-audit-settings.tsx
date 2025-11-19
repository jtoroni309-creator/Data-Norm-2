/**
 * Regulation A/B Audit Settings Component
 *
 * Admin interface for enabling/configuring Reg A/B audit feature for organizations
 */

'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Loader2, Save, AlertCircle, CheckCircle2, Shield } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface RegABFeatureFlags {
  id: string;
  organization_id: string;
  is_enabled: boolean;
  allow_client_portal: boolean;
  allow_cpa_portal: boolean;
  auto_workpaper_generation: boolean;
  auto_report_generation: boolean;
  ai_compliance_checking: boolean;
  ai_model_version: string;
  compliance_check_level: string;
  notify_on_completion: boolean;
  notify_cpa_on_ready: boolean;
  notify_client_on_approval: boolean;
  notification_email: string | null;
  require_dual_signoff: boolean;
  retention_years: number;
  created_at: string;
  updated_at: string;
  enabled_at: string | null;
  enabled_by: string | null;
}

interface RegABAuditSettingsProps {
  organizationId: string;
}

export function RegABAuditSettings({ organizationId }: RegABAuditSettingsProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<RegABFeatureFlags | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetchSettings();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [organizationId]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_REG_AB_API_URL || 'http://localhost:8011'}/api/feature-flags/${organizationId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }

      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
      toast.error('Failed to load Regulation A/B settings');
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = <K extends keyof RegABFeatureFlags>(
    key: K,
    value: RegABFeatureFlags[K]
  ) => {
    if (settings) {
      setSettings({ ...settings, [key]: value });
      setHasChanges(true);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    try {
      setSaving(true);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_REG_AB_API_URL || 'http://localhost:8011'}/api/feature-flags/${organizationId}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            is_enabled: settings.is_enabled,
            allow_client_portal: settings.allow_client_portal,
            allow_cpa_portal: settings.allow_cpa_portal,
            auto_workpaper_generation: settings.auto_workpaper_generation,
            auto_report_generation: settings.auto_report_generation,
            ai_compliance_checking: settings.ai_compliance_checking,
            ai_model_version: settings.ai_model_version,
            compliance_check_level: settings.compliance_check_level,
            notify_on_completion: settings.notify_on_completion,
            notify_cpa_on_ready: settings.notify_cpa_on_ready,
            notify_client_on_approval: settings.notify_client_on_approval,
            notification_email: settings.notification_email,
            require_dual_signoff: settings.require_dual_signoff,
            retention_years: settings.retention_years,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      const updatedSettings = await response.json();
      setSettings(updatedSettings);
      setHasChanges(false);

      toast.success('Regulation A/B audit settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  if (!settings) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load Regulation A/B audit settings. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Alert */}
      {settings.is_enabled ? (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-800">Feature Enabled</AlertTitle>
          <AlertDescription className="text-green-700">
            Regulation A/B audit is currently enabled for this organization.
            {settings.enabled_at && ` Enabled on ${new Date(settings.enabled_at).toLocaleDateString()}`}
          </AlertDescription>
        </Alert>
      ) : (
        <Alert>
          <Shield className="h-4 w-4" />
          <AlertTitle>Feature Disabled</AlertTitle>
          <AlertDescription>
            Regulation A/B audit is currently disabled. Enable it below to allow this organization to conduct CMBS audits.
          </AlertDescription>
        </Alert>
      )}

      {/* Master Toggle */}
      <Card>
        <CardHeader>
          <CardTitle>Enable Regulation A/B Audit</CardTitle>
          <CardDescription>
            Master toggle to enable/disable the entire Regulation A/B audit feature for this organization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="is_enabled" className="text-base font-medium">
                Feature Enabled
              </Label>
              <p className="text-sm text-muted-foreground">
                Allow this organization to access Regulation A/B audit functionality
              </p>
            </div>
            <Switch
              id="is_enabled"
              checked={settings.is_enabled}
              onCheckedChange={(checked) => updateSetting('is_enabled', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Portal Access */}
      <Card>
        <CardHeader>
          <CardTitle>Portal Access</CardTitle>
          <CardDescription>
            Configure which portals can access the Regulation A/B audit features
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="allow_client_portal" className="text-base">
                Client Portal Access
              </Label>
              <p className="text-sm text-muted-foreground">
                Allow clients to enter CMBS deals and view audit progress
              </p>
            </div>
            <Switch
              id="allow_client_portal"
              checked={settings.allow_client_portal}
              onCheckedChange={(checked) => updateSetting('allow_client_portal', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="allow_cpa_portal" className="text-base">
                CPA Portal Access
              </Label>
              <p className="text-sm text-muted-foreground">
                Allow CPAs to review workpapers and sign off on reports
              </p>
            </div>
            <Switch
              id="allow_cpa_portal"
              checked={settings.allow_cpa_portal}
              onCheckedChange={(checked) => updateSetting('allow_cpa_portal', checked)}
              disabled={!settings.is_enabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* AI Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>AI Configuration</CardTitle>
          <CardDescription>
            Configure AI-powered compliance checking and document generation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="ai_compliance_checking" className="text-base">
                AI Compliance Checking
              </Label>
              <p className="text-sm text-muted-foreground">
                Use AI to automatically check compliance with PCAOB, GAAP, GAAS, SEC, AICPA
              </p>
            </div>
            <Switch
              id="ai_compliance_checking"
              checked={settings.ai_compliance_checking}
              onCheckedChange={(checked) => updateSetting('ai_compliance_checking', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto_workpaper_generation" className="text-base">
                Auto Workpaper Generation
              </Label>
              <p className="text-sm text-muted-foreground">
                Automatically generate audit workpapers using AI
              </p>
            </div>
            <Switch
              id="auto_workpaper_generation"
              checked={settings.auto_workpaper_generation}
              onCheckedChange={(checked) => updateSetting('auto_workpaper_generation', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto_report_generation" className="text-base">
                Auto Report Generation
              </Label>
              <p className="text-sm text-muted-foreground">
                Automatically generate audit reports using AI
              </p>
            </div>
            <Switch
              id="auto_report_generation"
              checked={settings.auto_report_generation}
              onCheckedChange={(checked) => updateSetting('auto_report_generation', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="ai_model_version">AI Model Version</Label>
            <Select
              value={settings.ai_model_version}
              onValueChange={(value) => updateSetting('ai_model_version', value)}
              disabled={!settings.is_enabled}
            >
              <SelectTrigger id="ai_model_version">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gpt-4-turbo">GPT-4 Turbo (Recommended)</SelectItem>
                <SelectItem value="gpt-4">GPT-4</SelectItem>
                <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Select the AI model to use for compliance checking and generation
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="compliance_check_level">Compliance Check Level</Label>
            <Select
              value={settings.compliance_check_level}
              onValueChange={(value) => updateSetting('compliance_check_level', value)}
              disabled={!settings.is_enabled}
            >
              <SelectTrigger id="compliance_check_level">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="basic">Basic</SelectItem>
                <SelectItem value="standard">Standard</SelectItem>
                <SelectItem value="comprehensive">Comprehensive</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Higher levels perform more thorough compliance checks
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>
            Configure email notifications for audit workflow events
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notify_on_completion" className="text-base">
                Audit Completion
              </Label>
              <p className="text-sm text-muted-foreground">
                Notify when audit processing is complete
              </p>
            </div>
            <Switch
              id="notify_on_completion"
              checked={settings.notify_on_completion}
              onCheckedChange={(checked) => updateSetting('notify_on_completion', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notify_cpa_on_ready" className="text-base">
                CPA Review Ready
              </Label>
              <p className="text-sm text-muted-foreground">
                Notify CPA when audit is ready for review
              </p>
            </div>
            <Switch
              id="notify_cpa_on_ready"
              checked={settings.notify_cpa_on_ready}
              onCheckedChange={(checked) => updateSetting('notify_cpa_on_ready', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notify_client_on_approval" className="text-base">
                Client Report Approval
              </Label>
              <p className="text-sm text-muted-foreground">
                Notify client when report is approved by CPA
              </p>
            </div>
            <Switch
              id="notify_client_on_approval"
              checked={settings.notify_client_on_approval}
              onCheckedChange={(checked) => updateSetting('notify_client_on_approval', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="notification_email">Notification Email</Label>
            <Input
              id="notification_email"
              type="email"
              placeholder="audit@example.com"
              value={settings.notification_email || ''}
              onChange={(e) => updateSetting('notification_email', e.target.value || null)}
              disabled={!settings.is_enabled}
            />
            <p className="text-xs text-muted-foreground">
              Primary email address for audit notifications
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Audit Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Settings</CardTitle>
          <CardDescription>
            Configure audit workflow and retention policies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="require_dual_signoff" className="text-base">
                Require Dual Sign-off
              </Label>
              <p className="text-sm text-muted-foreground">
                Require two CPA signatures before finalizing reports
              </p>
            </div>
            <Switch
              id="require_dual_signoff"
              checked={settings.require_dual_signoff}
              onCheckedChange={(checked) => updateSetting('require_dual_signoff', checked)}
              disabled={!settings.is_enabled}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="retention_years">Retention Period (Years)</Label>
            <Input
              id="retention_years"
              type="number"
              min="1"
              max="10"
              value={settings.retention_years}
              onChange={(e) => updateSetting('retention_years', parseInt(e.target.value) || 7)}
              disabled={!settings.is_enabled}
            />
            <p className="text-xs text-muted-foreground">
              Number of years to retain audit documents (minimum 7 years per SEC requirements)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-4">
        <Button
          variant="outline"
          onClick={fetchSettings}
          disabled={!hasChanges || saving}
        >
          Reset
        </Button>
        <Button
          onClick={handleSave}
          disabled={!hasChanges || saving}
        >
          {saving ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
