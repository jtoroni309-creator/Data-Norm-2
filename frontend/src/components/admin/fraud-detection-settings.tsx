'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  AlertCircle,
  Shield,
  TrendingUp,
  Bell,
  Mail,
  Smartphone,
  Webhook,
  Save,
  CheckCircle,
} from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface FraudDetectionSettings {
  id: string;
  customer_id: string;
  is_enabled: boolean;
  real_time_monitoring: boolean;
  ml_detection: boolean;
  rule_based_detection: boolean;
  anomaly_detection: boolean;
  alert_email: boolean;
  alert_sms: boolean;
  alert_webhook: boolean;
  webhook_url?: string;
  min_alert_severity: 'low' | 'medium' | 'high' | 'critical';
  auto_case_creation_threshold: number;
  daily_transaction_limit?: number;
  high_risk_amount_threshold: number;
  created_at: string;
  enabled_at?: string;
}

interface FraudStatistics {
  total_transactions: number;
  flagged_transactions: number;
  flagged_percentage: number;
  total_cases: number;
  open_cases: number;
  resolved_cases: number;
  total_alerts: number;
  critical_alerts: number;
  average_fraud_score: number;
  total_potential_loss: number;
}

interface Props {
  customerId: string;
}

export function FraudDetectionSettings({ customerId }: Props) {
  const queryClient = useQueryClient();
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch fraud detection settings
  const { data: settings, isLoading: settingsLoading } = useQuery<FraudDetectionSettings>({
    queryKey: ['fraud-detection-settings', customerId],
    queryFn: async () => {
      const response = await fetch(`/api/fraud-detection/feature-flags/${customerId}`);
      if (!response.ok) throw new Error('Failed to fetch settings');
      return response.json();
    },
  });

  // Fetch fraud statistics
  const { data: stats, isLoading: statsLoading } = useQuery<FraudStatistics>({
    queryKey: ['fraud-detection-stats', customerId],
    queryFn: async () => {
      const response = await fetch(`/api/fraud-detection/statistics?customer_id=${customerId}`);
      if (!response.ok) throw new Error('Failed to fetch statistics');
      return response.json();
    },
    enabled: settings?.is_enabled === true,
  });

  const [formData, setFormData] = useState<Partial<FraudDetectionSettings>>(settings || {});

  // Update form data when settings load
  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  // Update settings mutation
  const updateSettings = useMutation({
    mutationFn: async (data: Partial<FraudDetectionSettings>) => {
      const response = await fetch(`/api/fraud-detection/feature-flags/${customerId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to update settings');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['fraud-detection-settings', customerId]);
      queryClient.invalidateQueries(['fraud-detection-stats', customerId]);
      toast.success('Fraud detection settings updated successfully');
      setHasChanges(false);
    },
    onError: (error) => {
      toast.error('Failed to update settings: ' + (error as Error).message);
    },
  });

  const handleToggle = (field: keyof FraudDetectionSettings, value: boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleChange = (field: keyof FraudDetectionSettings, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    updateSettings.mutate(formData);
  };

  if (settingsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const isEnabled = formData.is_enabled ?? false;

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      <Card className={isEnabled ? 'border-green-500 bg-green-50/50' : 'border-yellow-500 bg-yellow-50/50'}>
        <CardContent className="flex items-center justify-between py-4">
          <div className="flex items-center space-x-3">
            <Shield className={`h-8 w-8 ${isEnabled ? 'text-green-600' : 'text-yellow-600'}`} />
            <div>
              <h3 className="text-lg font-semibold">
                Fraud Detection {isEnabled ? 'Enabled' : 'Disabled'}
              </h3>
              <p className="text-sm text-muted-foreground">
                {isEnabled
                  ? 'AI-powered fraud detection is actively monitoring transactions'
                  : 'Enable fraud detection to protect customer accounts'}
              </p>
            </div>
          </div>
          <Switch
            checked={isEnabled}
            onCheckedChange={(checked) => handleToggle('is_enabled', checked)}
          />
        </CardContent>
      </Card>

      {/* Statistics (only show if enabled) */}
      {isEnabled && stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold">{stats.total_transactions.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">Total Transactions</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-orange-600">
                  {stats.flagged_transactions.toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">
                  Flagged ({stats.flagged_percentage.toFixed(1)}%)
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-red-600">{stats.open_cases}</p>
                <p className="text-sm text-muted-foreground">Open Cases</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-yellow-600">{stats.critical_alerts}</p>
                <p className="text-sm text-muted-foreground">Critical Alerts</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detection Methods */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Detection Methods</span>
          </CardTitle>
          <CardDescription>Configure which fraud detection techniques to use</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <Label htmlFor="real-time" className="text-base font-medium">
                Real-Time Monitoring
              </Label>
              <p className="text-sm text-muted-foreground">
                Monitor transactions as they occur for immediate fraud detection
              </p>
            </div>
            <Switch
              id="real-time"
              checked={formData.real_time_monitoring ?? true}
              onCheckedChange={(checked) => handleToggle('real_time_monitoring', checked)}
              disabled={!isEnabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex-1">
              <Label htmlFor="ml-detection" className="text-base font-medium">
                Machine Learning Detection
              </Label>
              <p className="text-sm text-muted-foreground">
                Use AI models (Random Forest, XGBoost) to identify fraud patterns
              </p>
            </div>
            <Switch
              id="ml-detection"
              checked={formData.ml_detection ?? true}
              onCheckedChange={(checked) => handleToggle('ml_detection', checked)}
              disabled={!isEnabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex-1">
              <Label htmlFor="rule-based" className="text-base font-medium">
                Rule-Based Detection
              </Label>
              <p className="text-sm text-muted-foreground">
                Apply predefined rules for velocity checks, thresholds, and patterns
              </p>
            </div>
            <Switch
              id="rule-based"
              checked={formData.rule_based_detection ?? true}
              onCheckedChange={(checked) => handleToggle('rule_based_detection', checked)}
              disabled={!isEnabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex-1">
              <Label htmlFor="anomaly" className="text-base font-medium">
                Anomaly Detection
              </Label>
              <p className="text-sm text-muted-foreground">
                Use Isolation Forest to detect unusual transaction patterns
              </p>
            </div>
            <Switch
              id="anomaly"
              checked={formData.anomaly_detection ?? true}
              onCheckedChange={(checked) => handleToggle('anomaly_detection', checked)}
              disabled={!isEnabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* Alert Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Alert Configuration</span>
          </CardTitle>
          <CardDescription>Configure how fraud alerts are delivered</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 flex-1">
              <Mail className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="alert-email" className="text-base font-medium">
                  Email Alerts
                </Label>
                <p className="text-sm text-muted-foreground">Send alerts via email</p>
              </div>
            </div>
            <Switch
              id="alert-email"
              checked={formData.alert_email ?? true}
              onCheckedChange={(checked) => handleToggle('alert_email', checked)}
              disabled={!isEnabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 flex-1">
              <Smartphone className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="alert-sms" className="text-base font-medium">
                  SMS Alerts
                </Label>
                <p className="text-sm text-muted-foreground">Send alerts via SMS</p>
              </div>
            </div>
            <Switch
              id="alert-sms"
              checked={formData.alert_sms ?? false}
              onCheckedChange={(checked) => handleToggle('alert_sms', checked)}
              disabled={!isEnabled}
            />
          </div>

          <Separator />

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 flex-1">
                <Webhook className="h-5 w-5 text-muted-foreground" />
                <div>
                  <Label htmlFor="alert-webhook" className="text-base font-medium">
                    Webhook Alerts
                  </Label>
                  <p className="text-sm text-muted-foreground">Send alerts to webhook URL</p>
                </div>
              </div>
              <Switch
                id="alert-webhook"
                checked={formData.alert_webhook ?? false}
                onCheckedChange={(checked) => handleToggle('alert_webhook', checked)}
                disabled={!isEnabled}
              />
            </div>

            {formData.alert_webhook && (
              <div>
                <Label htmlFor="webhook-url">Webhook URL</Label>
                <Input
                  id="webhook-url"
                  type="url"
                  placeholder="https://your-domain.com/webhook"
                  value={formData.webhook_url || ''}
                  onChange={(e) => handleChange('webhook_url', e.target.value)}
                  disabled={!isEnabled}
                />
              </div>
            )}
          </div>

          <Separator />

          <div className="space-y-2">
            <Label htmlFor="min-severity">Minimum Alert Severity</Label>
            <Select
              value={formData.min_alert_severity || 'medium'}
              onValueChange={(value) => handleChange('min_alert_severity', value)}
              disabled={!isEnabled}
            >
              <SelectTrigger id="min-severity">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low - All alerts</SelectItem>
                <SelectItem value="medium">Medium - Moderate and above</SelectItem>
                <SelectItem value="high">High - High and critical only</SelectItem>
                <SelectItem value="critical">Critical - Critical only</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Only send alerts at or above this severity level
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Thresholds & Limits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5" />
            <span>Thresholds & Limits</span>
          </CardTitle>
          <CardDescription>Configure fraud detection sensitivity and limits</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="case-threshold">Auto Case Creation Threshold</Label>
            <div className="flex items-center space-x-4">
              <Input
                id="case-threshold"
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={formData.auto_case_creation_threshold || 0.85}
                onChange={(e) =>
                  handleChange('auto_case_creation_threshold', parseFloat(e.target.value))
                }
                disabled={!isEnabled}
                className="w-32"
              />
              <span className="text-sm text-muted-foreground">
                ({((formData.auto_case_creation_threshold || 0.85) * 100).toFixed(0)}% confidence)
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Automatically create fraud case when fraud score exceeds this threshold
            </p>
          </div>

          <Separator />

          <div className="space-y-2">
            <Label htmlFor="risk-amount">High Risk Amount Threshold</Label>
            <div className="flex items-center space-x-2">
              <span className="text-sm">$</span>
              <Input
                id="risk-amount"
                type="number"
                min="0"
                step="100"
                value={formData.high_risk_amount_threshold || 5000}
                onChange={(e) =>
                  handleChange('high_risk_amount_threshold', parseFloat(e.target.value))
                }
                disabled={!isEnabled}
                className="w-40"
              />
            </div>
            <p className="text-sm text-muted-foreground">
              Transactions above this amount receive extra scrutiny
            </p>
          </div>

          <Separator />

          <div className="space-y-2">
            <Label htmlFor="daily-limit">Daily Transaction Limit (Optional)</Label>
            <Input
              id="daily-limit"
              type="number"
              min="0"
              placeholder="No limit"
              value={formData.daily_transaction_limit || ''}
              onChange={(e) =>
                handleChange(
                  'daily_transaction_limit',
                  e.target.value ? parseInt(e.target.value) : undefined
                )
              }
              disabled={!isEnabled}
              className="w-40"
            />
            <p className="text-sm text-muted-foreground">
              Alert when daily transaction count exceeds this limit
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      {hasChanges && (
        <div className="flex items-center justify-between rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">You have unsaved changes</p>
          <Button onClick={handleSave} disabled={updateSettings.isPending}>
            {updateSettings.isPending ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      )}

      {/* Last Updated */}
      {settings?.enabled_at && (
        <div className="text-sm text-muted-foreground text-center">
          Fraud detection enabled on {new Date(settings.enabled_at).toLocaleString()}
        </div>
      )}
    </div>
  );
}
