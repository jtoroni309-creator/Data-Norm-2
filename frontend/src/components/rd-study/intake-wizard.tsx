'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  ChevronLeft,
  ChevronRight,
  Building2,
  Calendar,
  MapPin,
  Lightbulb,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

interface IntakeWizardProps {
  clientId?: string;
  onComplete?: (studyId: string) => void;
}

interface WizardState {
  step: number;
  // Step 1: Basic Info
  name: string;
  taxYear: number;
  entityType: string;
  entityName: string;
  ein: string;
  fiscalYearStart: string;
  fiscalYearEnd: string;
  isShortYear: boolean;
  shortYearDays: number;
  // Step 2: Controlled Group
  isControlledGroup: boolean;
  controlledGroupName: string;
  aggregationMethod: string;
  // Step 3: States
  states: string[];
  primaryState: string;
  // Step 4: Scoping
  industry: string;
  industryNaics: string;
  businessDescription: string;
  rdActivitiesDescription: string;
  departmentsInvolved: string[];
  estimatedRdHeadcount: number;
  estimatedRdSpend: number;
}

const ENTITY_TYPES = [
  { value: 'c_corp', label: 'C Corporation' },
  { value: 's_corp', label: 'S Corporation' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'llc_corp', label: 'LLC (taxed as Corporation)' },
  { value: 'llc_partnership', label: 'LLC (taxed as Partnership)' },
  { value: 'llc_disregarded', label: 'LLC (Disregarded Entity)' },
  { value: 'sole_proprietor', label: 'Sole Proprietor' },
];

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
];

const STATES_WITH_CREDITS = [
  'CA', 'TX', 'NY', 'MA', 'NJ', 'PA', 'GA', 'AZ', 'CT', 'IL',
  'OH', 'WA', 'MN', 'CO', 'WI', 'VA', 'UT', 'NC', 'MD', 'SC',
  'IN', 'OR'
];

const INDUSTRIES = [
  'Software & Technology',
  'Manufacturing',
  'Biotechnology & Pharmaceuticals',
  'Aerospace & Defense',
  'Medical Devices',
  'Automotive',
  'Electronics',
  'Chemical',
  'Food & Beverage',
  'Construction & Engineering',
  'Other'
];

const DEPARTMENTS = [
  'Engineering',
  'Research & Development',
  'Product Development',
  'Software Development',
  'Quality Assurance',
  'Manufacturing Engineering',
  'Process Engineering',
  'Design',
  'IT/Systems',
  'Other'
];

export function IntakeWizard({ clientId, onComplete }: IntakeWizardProps) {
  const router = useRouter();
  const currentYear = new Date().getFullYear();

  const [state, setState] = useState<WizardState>({
    step: 1,
    name: '',
    taxYear: currentYear - 1,
    entityType: '',
    entityName: '',
    ein: '',
    fiscalYearStart: `${currentYear - 1}-01-01`,
    fiscalYearEnd: `${currentYear - 1}-12-31`,
    isShortYear: false,
    shortYearDays: 365,
    isControlledGroup: false,
    controlledGroupName: '',
    aggregationMethod: 'standalone',
    states: [],
    primaryState: '',
    industry: '',
    industryNaics: '',
    businessDescription: '',
    rdActivitiesDescription: '',
    departmentsInvolved: [],
    estimatedRdHeadcount: 0,
    estimatedRdSpend: 0,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);

  const totalSteps = 4;
  const progress = (state.step / totalSteps) * 100;

  const updateState = (updates: Partial<WizardState>) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  const nextStep = () => {
    if (state.step < totalSteps) {
      updateState({ step: state.step + 1 });
    }
  };

  const prevStep = () => {
    if (state.step > 1) {
      updateState({ step: state.step - 1 });
    }
  };

  const toggleState = (stateCode: string) => {
    const current = state.states;
    if (current.includes(stateCode)) {
      updateState({ states: current.filter(s => s !== stateCode) });
    } else {
      updateState({ states: [...current, stateCode] });
    }
  };

  const toggleDepartment = (dept: string) => {
    const current = state.departmentsInvolved;
    if (current.includes(dept)) {
      updateState({ departmentsInvolved: current.filter(d => d !== dept) });
    } else {
      updateState({ departmentsInvolved: [...current, dept] });
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/rd-studies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: clientId,
          name: state.name || `R&D Study ${state.taxYear} - ${state.entityName}`,
          tax_year: state.taxYear,
          entity_type: state.entityType,
          entity_name: state.entityName,
          ein: state.ein,
          fiscal_year_start: state.fiscalYearStart,
          fiscal_year_end: state.fiscalYearEnd,
          is_short_year: state.isShortYear,
          short_year_days: state.shortYearDays,
          is_controlled_group: state.isControlledGroup,
          controlled_group_name: state.controlledGroupName,
          aggregation_method: state.aggregationMethod,
          states: state.states,
          primary_state: state.primaryState,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create study');
      }

      const data = await response.json();

      if (onComplete) {
        onComplete(data.id);
      } else {
        router.push(`/rd-studies/${data.id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchAiSuggestions = async () => {
    if (!state.industry || !state.rdActivitiesDescription) return;

    try {
      const response = await fetch('/api/rd-studies/ai-scoping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          industry: state.industry,
          business_description: state.businessDescription,
          rd_activities: state.rdActivitiesDescription,
          departments: state.departmentsInvolved,
        }),
      });

      if (response.ok) {
        const suggestions = await response.json();
        setAiSuggestions(suggestions);
      }
    } catch (err) {
      console.error('Failed to get AI suggestions:', err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-2xl font-bold">New R&D Tax Credit Study</h2>
          <span className="text-sm text-muted-foreground">
            Step {state.step} of {totalSteps}
          </span>
        </div>
        <Progress value={progress} className="h-2" />

        {/* Step Indicators */}
        <div className="flex justify-between mt-4">
          {[
            { num: 1, label: 'Basic Info', icon: Building2 },
            { num: 2, label: 'Controlled Group', icon: Building2 },
            { num: 3, label: 'State Nexus', icon: MapPin },
            { num: 4, label: 'Scoping', icon: Lightbulb },
          ].map(({ num, label, icon: Icon }) => (
            <div
              key={num}
              className={`flex items-center gap-2 ${
                state.step >= num ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  state.step > num
                    ? 'bg-primary text-primary-foreground'
                    : state.step === num
                    ? 'bg-primary/20 text-primary'
                    : 'bg-muted'
                }`}
              >
                {state.step > num ? <CheckCircle className="w-4 h-4" /> : num}
              </div>
              <span className="text-sm hidden md:inline">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Step 1: Basic Information */}
      {state.step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Entity & Tax Year Information
            </CardTitle>
            <CardDescription>
              Provide basic information about the entity and tax year for this study
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="entityName">Entity Name *</Label>
                <Input
                  id="entityName"
                  value={state.entityName}
                  onChange={(e) => updateState({ entityName: e.target.value })}
                  placeholder="ABC Corporation"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ein">EIN</Label>
                <Input
                  id="ein"
                  value={state.ein}
                  onChange={(e) => updateState({ ein: e.target.value })}
                  placeholder="XX-XXXXXXX"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="entityType">Entity Type *</Label>
                <Select
                  value={state.entityType}
                  onValueChange={(value) => updateState({ entityType: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select entity type" />
                  </SelectTrigger>
                  <SelectContent>
                    {ENTITY_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="taxYear">Tax Year *</Label>
                <Select
                  value={state.taxYear.toString()}
                  onValueChange={(value) => updateState({ taxYear: parseInt(value) })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[0, 1, 2, 3, 4].map((offset) => (
                      <SelectItem key={offset} value={(currentYear - offset).toString()}>
                        {currentYear - offset}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="fiscalYearStart">Fiscal Year Start *</Label>
                <Input
                  id="fiscalYearStart"
                  type="date"
                  value={state.fiscalYearStart}
                  onChange={(e) => updateState({ fiscalYearStart: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="fiscalYearEnd">Fiscal Year End *</Label>
                <Input
                  id="fiscalYearEnd"
                  type="date"
                  value={state.fiscalYearEnd}
                  onChange={(e) => updateState({ fiscalYearEnd: e.target.value })}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="isShortYear"
                checked={state.isShortYear}
                onCheckedChange={(checked) => updateState({ isShortYear: checked as boolean })}
              />
              <Label htmlFor="isShortYear">This is a short tax year</Label>
            </div>

            {state.isShortYear && (
              <div className="space-y-2">
                <Label htmlFor="shortYearDays">Days in Short Year</Label>
                <Input
                  id="shortYearDays"
                  type="number"
                  value={state.shortYearDays}
                  onChange={(e) => updateState({ shortYearDays: parseInt(e.target.value) })}
                />
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Controlled Group */}
      {state.step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Controlled Group & Aggregation
            </CardTitle>
            <CardDescription>
              If this entity is part of a controlled group, provide aggregation details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="isControlledGroup"
                checked={state.isControlledGroup}
                onCheckedChange={(checked) => updateState({ isControlledGroup: checked as boolean })}
              />
              <Label htmlFor="isControlledGroup">
                This entity is part of a controlled group of corporations
              </Label>
            </div>

            {state.isControlledGroup && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="controlledGroupName">Controlled Group Name</Label>
                  <Input
                    id="controlledGroupName"
                    value={state.controlledGroupName}
                    onChange={(e) => updateState({ controlledGroupName: e.target.value })}
                    placeholder="Parent Company Group"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="aggregationMethod">Aggregation Method</Label>
                  <Select
                    value={state.aggregationMethod}
                    onValueChange={(value) => updateState({ aggregationMethod: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="standalone">
                        Standalone - Calculate credit for this entity only
                      </SelectItem>
                      <SelectItem value="aggregated">
                        Aggregated - Calculate group credit and allocate
                      </SelectItem>
                      <SelectItem value="allocated">
                        Allocated - Use pre-determined allocation percentage
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Under IRC §41(f)(1), all members of a controlled group are treated as a single
                    taxpayer for purposes of computing the R&D credit. The credit must be allocated
                    among group members.
                  </AlertDescription>
                </Alert>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: State Nexus */}
      {state.step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              State Nexus
            </CardTitle>
            <CardDescription>
              Select states where qualified research activities were performed
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>States with R&D Activity</Label>
              <div className="flex flex-wrap gap-2 p-4 border rounded-lg">
                {US_STATES.map((stateCode) => {
                  const hasCredit = STATES_WITH_CREDITS.includes(stateCode);
                  const isSelected = state.states.includes(stateCode);

                  return (
                    <Badge
                      key={stateCode}
                      variant={isSelected ? 'default' : 'outline'}
                      className={`cursor-pointer ${
                        hasCredit ? 'border-green-500' : ''
                      }`}
                      onClick={() => toggleState(stateCode)}
                    >
                      {stateCode}
                      {hasCredit && !isSelected && (
                        <span className="ml-1 text-green-500">*</span>
                      )}
                    </Badge>
                  );
                })}
              </div>
              <p className="text-xs text-muted-foreground">
                * States with R&D tax credit programs
              </p>
            </div>

            {state.states.length > 0 && (
              <div className="space-y-2">
                <Label htmlFor="primaryState">Primary State</Label>
                <Select
                  value={state.primaryState}
                  onValueChange={(value) => updateState({ primaryState: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select primary state" />
                  </SelectTrigger>
                  <SelectContent>
                    {state.states.map((stateCode) => (
                      <SelectItem key={stateCode} value={stateCode}>
                        {stateCode}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {state.states.filter(s => STATES_WITH_CREDITS.includes(s)).length > 0 && (
              <Alert>
                <CheckCircle className="h-4 w-4 text-green-500" />
                <AlertDescription>
                  {state.states.filter(s => STATES_WITH_CREDITS.includes(s)).length} of your
                  selected states have R&D tax credit programs. State credits will be calculated
                  in addition to the Federal credit.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 4: Scoping */}
      {state.step === 4 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5" />
              Initial Scoping
            </CardTitle>
            <CardDescription>
              Help us understand your R&D activities for AI-powered scoping
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="industry">Industry *</Label>
                <Select
                  value={state.industry}
                  onValueChange={(value) => updateState({ industry: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select industry" />
                  </SelectTrigger>
                  <SelectContent>
                    {INDUSTRIES.map((ind) => (
                      <SelectItem key={ind} value={ind}>
                        {ind}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="naics">NAICS Code (optional)</Label>
                <Input
                  id="naics"
                  value={state.industryNaics}
                  onChange={(e) => updateState({ industryNaics: e.target.value })}
                  placeholder="e.g., 541511"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="businessDescription">Business Description</Label>
              <Textarea
                id="businessDescription"
                value={state.businessDescription}
                onChange={(e) => updateState({ businessDescription: e.target.value })}
                placeholder="Briefly describe what your company does..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="rdActivities">R&D Activities Description *</Label>
              <Textarea
                id="rdActivities"
                value={state.rdActivitiesDescription}
                onChange={(e) => updateState({ rdActivitiesDescription: e.target.value })}
                placeholder="Describe the research and development activities your company performs..."
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label>Departments Involved in R&D</Label>
              <div className="flex flex-wrap gap-2">
                {DEPARTMENTS.map((dept) => (
                  <Badge
                    key={dept}
                    variant={state.departmentsInvolved.includes(dept) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => toggleDepartment(dept)}
                  >
                    {dept}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="headcount">Estimated R&D Headcount</Label>
                <Input
                  id="headcount"
                  type="number"
                  value={state.estimatedRdHeadcount || ''}
                  onChange={(e) => updateState({ estimatedRdHeadcount: parseInt(e.target.value) || 0 })}
                  placeholder="Number of R&D employees"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rdSpend">Estimated Annual R&D Spend ($)</Label>
                <Input
                  id="rdSpend"
                  type="number"
                  value={state.estimatedRdSpend || ''}
                  onChange={(e) => updateState({ estimatedRdSpend: parseInt(e.target.value) || 0 })}
                  placeholder="Annual R&D expenditure"
                />
              </div>
            </div>

            {state.rdActivitiesDescription && (
              <Button
                variant="outline"
                onClick={fetchAiSuggestions}
                className="w-full"
              >
                <Lightbulb className="w-4 h-4 mr-2" />
                Get AI-Powered Suggestions
              </Button>
            )}

            {aiSuggestions && (
              <Card className="bg-blue-50 dark:bg-blue-950">
                <CardHeader>
                  <CardTitle className="text-sm">AI Scoping Suggestions</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-2">
                  <p><strong>Likely Qualifying Areas:</strong></p>
                  <ul className="list-disc pl-4">
                    {aiSuggestions.suggested_areas?.map((area: string, i: number) => (
                      <li key={i}>{area}</li>
                    ))}
                  </ul>
                  {aiSuggestions.estimated_credit_range && (
                    <p className="mt-2">
                      <strong>Estimated Credit Range:</strong>{' '}
                      ${aiSuggestions.estimated_credit_range.min?.toLocaleString()} -{' '}
                      ${aiSuggestions.estimated_credit_range.max?.toLocaleString()}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={state.step === 1}
        >
          <ChevronLeft className="w-4 h-4 mr-2" />
          Previous
        </Button>

        {state.step < totalSteps ? (
          <Button onClick={nextStep}>
            Next
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Creating Study...' : 'Create Study'}
          </Button>
        )}
      </div>
    </div>
  );
}

export default IntakeWizard;
