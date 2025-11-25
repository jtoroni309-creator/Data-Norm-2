'use client';

import React, { useState, useEffect, useCallback } from 'react';

// Types
interface Project {
  id: string;
  name: string;
  description: string;
  business_component: string;
  qualification_status: 'pending' | 'qualified' | 'not_qualified' | 'needs_review';
  ai_confidence: number;
  four_part_test: FourPartTestResult;
  total_qre: number;
  risk_flags: RiskFlag[];
  evidence_count: number;
  narratives: Narrative[];
}

interface FourPartTestResult {
  permitted_purpose: TestElement;
  technological_nature: TestElement;
  elimination_of_uncertainty: TestElement;
  process_of_experimentation: TestElement;
  overall_score: number;
}

interface TestElement {
  score: number;
  confidence: number;
  evidence: string[];
  ai_reasoning: string;
  cpa_override?: {
    score: number;
    notes: string;
    timestamp: string;
  };
}

interface RiskFlag {
  type: 'high_allocation' | 'missing_evidence' | 'generic_description' | 'unusual_pattern' | 'state_specific';
  severity: 'low' | 'medium' | 'high';
  message: string;
  resolution?: string;
}

interface Narrative {
  id: string;
  type: 'project' | 'activity' | 'uncertainty';
  content: string;
  ai_generated: boolean;
  cpa_edited: boolean;
  citations: Citation[];
}

interface Citation {
  source: string;
  text: string;
  document_id?: string;
}

interface Employee {
  id: string;
  name: string;
  title: string;
  department: string;
  total_compensation: number;
  rd_allocation_percent: number;
  qualified_wages: number;
  projects: { project_id: string; allocation_percent: number }[];
  evidence_strength: 'strong' | 'moderate' | 'weak';
}

interface QREItem {
  id: string;
  category: 'wages' | 'supplies' | 'contract_research';
  description: string;
  amount: number;
  qualified_amount: number;
  allocation_percent: number;
  project_id: string;
  evidence_ids: string[];
  status: 'approved' | 'pending' | 'rejected';
}

interface CalculationResult {
  federal_regular: {
    total_qre: number;
    base_amount: number;
    credit: number;
  };
  federal_asc: {
    total_qre: number;
    average_prior_qre: number;
    credit: number;
  };
  recommended_method: 'regular' | 'asc';
  state_credits: { [state: string]: number };
  total_credit: number;
}

interface Study {
  id: string;
  entity_name: string;
  tax_year: number;
  status: string;
  projects: Project[];
  employees: Employee[];
  qre_items: QREItem[];
  calculation: CalculationResult;
}

// Props
interface ReviewConsoleProps {
  studyId: string;
  onComplete?: () => void;
}

// Sub-components
const RiskBadge: React.FC<{ flag: RiskFlag }> = ({ flag }) => {
  const colors = {
    low: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    medium: 'bg-orange-100 text-orange-800 border-orange-200',
    high: 'bg-red-100 text-red-800 border-red-200',
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs border ${colors[flag.severity]}`}>
      {flag.severity === 'high' && '⚠️ '}
      {flag.message}
    </span>
  );
};

const ConfidenceIndicator: React.FC<{ confidence: number }> = ({ confidence }) => {
  const getColor = () => {
    if (confidence >= 0.85) return 'bg-green-500';
    if (confidence >= 0.70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all`}
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
      <span className="text-sm text-gray-600">{(confidence * 100).toFixed(0)}%</span>
    </div>
  );
};

const FourPartTestCard: React.FC<{
  result: FourPartTestResult;
  onOverride: (element: string, score: number, notes: string) => void;
}> = ({ result, onOverride }) => {
  const [expandedElement, setExpandedElement] = useState<string | null>(null);
  const [overrideNotes, setOverrideNotes] = useState('');
  const [overrideScore, setOverrideScore] = useState(0);

  const elements = [
    { key: 'permitted_purpose', label: 'Permitted Purpose', data: result.permitted_purpose },
    { key: 'technological_nature', label: 'Technological in Nature', data: result.technological_nature },
    { key: 'elimination_of_uncertainty', label: 'Elimination of Uncertainty', data: result.elimination_of_uncertainty },
    { key: 'process_of_experimentation', label: 'Process of Experimentation', data: result.process_of_experimentation },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h4 className="font-semibold text-gray-900 mb-3">4-Part Test Analysis</h4>
      <div className="space-y-3">
        {elements.map(({ key, label, data }) => (
          <div key={key} className="border-b border-gray-100 pb-3 last:border-0">
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setExpandedElement(expandedElement === key ? null : key)}
            >
              <span className="text-sm font-medium text-gray-700">{label}</span>
              <div className="flex items-center gap-3">
                <span className={`font-semibold ${getScoreColor(data.score)}`}>
                  {(data.score * 100).toFixed(0)}%
                </span>
                {data.cpa_override && (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                    Override: {(data.cpa_override.score * 100).toFixed(0)}%
                  </span>
                )}
                <span className="text-gray-400">{expandedElement === key ? '▼' : '▶'}</span>
              </div>
            </div>

            {expandedElement === key && (
              <div className="mt-3 pl-4 space-y-3">
                <div>
                  <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">AI Reasoning</h5>
                  <p className="text-sm text-gray-600">{data.ai_reasoning}</p>
                </div>

                <div>
                  <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Evidence</h5>
                  <ul className="text-sm text-gray-600 list-disc list-inside">
                    {data.evidence.map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-gray-50 rounded p-3">
                  <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">CPA Override</h5>
                  <div className="flex gap-3">
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">Score</label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={overrideScore}
                        onChange={(e) => setOverrideScore(parseInt(e.target.value))}
                        className="w-full"
                      />
                      <span className="text-sm">{overrideScore}%</span>
                    </div>
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">Notes (required)</label>
                      <textarea
                        value={overrideNotes}
                        onChange={(e) => setOverrideNotes(e.target.value)}
                        className="w-full text-sm border rounded p-2"
                        rows={2}
                        placeholder="Explain the override reason..."
                      />
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      if (overrideNotes.trim()) {
                        onOverride(key, overrideScore / 100, overrideNotes);
                        setOverrideNotes('');
                      }
                    }}
                    disabled={!overrideNotes.trim()}
                    className="mt-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Apply Override
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="font-medium text-gray-700">Overall Qualification Score</span>
          <span className={`text-lg font-bold ${getScoreColor(result.overall_score)}`}>
            {(result.overall_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
};

const NarrativeEditor: React.FC<{
  narrative: Narrative;
  onSave: (content: string) => void;
}> = ({ narrative, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(narrative.content);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <h5 className="font-medium text-gray-700 capitalize">{narrative.type} Narrative</h5>
          {narrative.ai_generated && (
            <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded">
              AI Generated
            </span>
          )}
          {narrative.cpa_edited && (
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
              CPA Edited
            </span>
          )}
        </div>
        <button
          onClick={() => {
            if (isEditing) {
              onSave(content);
            }
            setIsEditing(!isEditing);
          }}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {isEditing ? 'Save' : 'Edit'}
        </button>
      </div>

      {isEditing ? (
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full border rounded p-3 text-sm min-h-[150px]"
        />
      ) : (
        <p className="text-sm text-gray-600 whitespace-pre-wrap">{narrative.content}</p>
      )}

      {narrative.citations.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <h6 className="text-xs font-semibold text-gray-500 uppercase mb-2">Citations</h6>
          <ul className="space-y-1">
            {narrative.citations.map((citation, i) => (
              <li key={i} className="text-xs text-gray-500">
                [{i + 1}] {citation.source}: "{citation.text}"
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const EmployeeAllocationEditor: React.FC<{
  employee: Employee;
  projects: Project[];
  onUpdate: (employeeId: string, updates: Partial<Employee>) => void;
}> = ({ employee, projects, onUpdate }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [allocations, setAllocations] = useState(employee.projects);

  const totalAllocation = allocations.reduce((sum, a) => sum + a.allocation_percent, 0);

  const handleAllocationChange = (projectId: string, percent: number) => {
    const updated = allocations.map((a) =>
      a.project_id === projectId ? { ...a, allocation_percent: percent } : a
    );
    setAllocations(updated);
  };

  const handleSave = () => {
    onUpdate(employee.id, { projects: allocations });
  };

  return (
    <div className="border border-gray-200 rounded-lg">
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div>
          <span className="font-medium text-gray-900">{employee.name}</span>
          <span className="text-sm text-gray-500 ml-2">({employee.title})</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              ${employee.qualified_wages.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">
              {employee.rd_allocation_percent}% R&D
            </div>
          </div>
          <span
            className={`px-2 py-1 text-xs rounded ${
              employee.evidence_strength === 'strong'
                ? 'bg-green-100 text-green-800'
                : employee.evidence_strength === 'moderate'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {employee.evidence_strength} evidence
          </span>
          <span className="text-gray-400">{isExpanded ? '▼' : '▶'}</span>
        </div>
      </div>

      {isExpanded && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <div className="mt-4">
            <h5 className="text-sm font-semibold text-gray-700 mb-2">Project Allocations</h5>
            <div className="space-y-2">
              {allocations.map((allocation) => {
                const project = projects.find((p) => p.id === allocation.project_id);
                return (
                  <div key={allocation.project_id} className="flex items-center gap-3">
                    <span className="flex-1 text-sm text-gray-600">
                      {project?.name || 'Unknown Project'}
                    </span>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={allocation.allocation_percent}
                      onChange={(e) =>
                        handleAllocationChange(allocation.project_id, parseInt(e.target.value) || 0)
                      }
                      className="w-20 text-sm border rounded px-2 py-1"
                    />
                    <span className="text-sm text-gray-500">%</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span
                className={`text-sm ${
                  totalAllocation > 100 ? 'text-red-600 font-semibold' : 'text-gray-600'
                }`}
              >
                Total: {totalAllocation}%
                {totalAllocation > 100 && ' (exceeds 100%)'}
              </span>
              <button
                onClick={handleSave}
                disabled={totalAllocation > 100}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const CalculationSummary: React.FC<{
  calculation: CalculationResult;
  onMethodChange: (method: 'regular' | 'asc') => void;
}> = ({ calculation, onMethodChange }) => {
  const [selectedMethod, setSelectedMethod] = useState(calculation.recommended_method);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Credit Calculation Summary</h3>

      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Regular Credit */}
        <div
          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
            selectedMethod === 'regular'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          onClick={() => {
            setSelectedMethod('regular');
            onMethodChange('regular');
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-700">Regular Credit</h4>
            <input
              type="radio"
              checked={selectedMethod === 'regular'}
              onChange={() => {}}
              className="h-4 w-4 text-blue-600"
            />
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Total QRE:</span>
              <span className="font-medium">${calculation.federal_regular.total_qre.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Base Amount:</span>
              <span className="font-medium">${calculation.federal_regular.base_amount.toLocaleString()}</span>
            </div>
            <div className="flex justify-between border-t border-gray-200 pt-1 mt-1">
              <span className="text-gray-700 font-medium">Credit:</span>
              <span className="text-lg font-bold text-green-600">
                ${calculation.federal_regular.credit.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* ASC Credit */}
        <div
          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
            selectedMethod === 'asc'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          onClick={() => {
            setSelectedMethod('asc');
            onMethodChange('asc');
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-700">Alternative Simplified Credit</h4>
            <input
              type="radio"
              checked={selectedMethod === 'asc'}
              onChange={() => {}}
              className="h-4 w-4 text-blue-600"
            />
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Total QRE:</span>
              <span className="font-medium">${calculation.federal_asc.total_qre.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Avg Prior QRE:</span>
              <span className="font-medium">${calculation.federal_asc.average_prior_qre.toLocaleString()}</span>
            </div>
            <div className="flex justify-between border-t border-gray-200 pt-1 mt-1">
              <span className="text-gray-700 font-medium">Credit:</span>
              <span className="text-lg font-bold text-green-600">
                ${calculation.federal_asc.credit.toLocaleString()}
              </span>
            </div>
          </div>
          {calculation.recommended_method === 'asc' && (
            <div className="mt-2">
              <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                Recommended
              </span>
            </div>
          )}
        </div>
      </div>

      {/* State Credits */}
      {Object.keys(calculation.state_credits).length > 0 && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-700 mb-3">State Credits</h4>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(calculation.state_credits).map(([state, credit]) => (
              <div key={state} className="flex justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">{state}:</span>
                <span className="text-sm font-medium">${credit.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Total */}
      <div className="pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-900">Total Credit</span>
          <span className="text-2xl font-bold text-green-600">
            ${calculation.total_credit.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
};

// Main Component
export const ReviewConsole: React.FC<ReviewConsoleProps> = ({ studyId, onComplete }) => {
  const [study, setStudy] = useState<Study | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'projects' | 'employees' | 'qre' | 'calculation' | 'narratives'>('projects');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [approvalStatus, setApprovalStatus] = useState<{ [key: string]: 'approved' | 'rejected' | 'pending' }>({});

  // Fetch study data
  useEffect(() => {
    const fetchStudy = async () => {
      try {
        const response = await fetch(`/api/rd-study/${studyId}`);
        if (response.ok) {
          const data = await response.json();
          setStudy(data);
          // Initialize approval status
          const status: { [key: string]: 'approved' | 'rejected' | 'pending' } = {};
          data.projects.forEach((p: Project) => {
            status[p.id] = p.qualification_status === 'qualified' ? 'approved' : 'pending';
          });
          setApprovalStatus(status);
        }
      } catch (error) {
        console.error('Failed to fetch study:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStudy();
  }, [studyId]);

  const handleProjectApproval = async (projectId: string, status: 'approved' | 'rejected') => {
    try {
      await fetch(`/api/rd-study/${studyId}/projects/${projectId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      setApprovalStatus((prev) => ({ ...prev, [projectId]: status }));
    } catch (error) {
      console.error('Failed to update project status:', error);
    }
  };

  const handleOverride = async (projectId: string, element: string, score: number, notes: string) => {
    try {
      await fetch(`/api/rd-study/${studyId}/projects/${projectId}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ element, score, notes }),
      });
      // Refresh study data
      const response = await fetch(`/api/rd-study/${studyId}`);
      if (response.ok) {
        setStudy(await response.json());
      }
    } catch (error) {
      console.error('Failed to apply override:', error);
    }
  };

  const handleNarrativeSave = async (narrativeId: string, content: string) => {
    try {
      await fetch(`/api/rd-study/${studyId}/narratives/${narrativeId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
    } catch (error) {
      console.error('Failed to save narrative:', error);
    }
  };

  const handleEmployeeUpdate = async (employeeId: string, updates: Partial<Employee>) => {
    try {
      await fetch(`/api/rd-study/${studyId}/employees/${employeeId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      // Refresh study data
      const response = await fetch(`/api/rd-study/${studyId}`);
      if (response.ok) {
        setStudy(await response.json());
      }
    } catch (error) {
      console.error('Failed to update employee:', error);
    }
  };

  const handleMethodChange = async (method: 'regular' | 'asc') => {
    try {
      await fetch(`/api/rd-study/${studyId}/calculation/method`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ method }),
      });
    } catch (error) {
      console.error('Failed to change method:', error);
    }
  };

  const handleFinalizeStudy = async () => {
    const pendingProjects = Object.values(approvalStatus).filter((s) => s === 'pending').length;
    if (pendingProjects > 0) {
      alert(`Please review all projects. ${pendingProjects} project(s) still pending.`);
      return;
    }

    try {
      await fetch(`/api/rd-study/${studyId}/finalize`, {
        method: 'POST',
      });
      onComplete?.();
    } catch (error) {
      console.error('Failed to finalize study:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!study) {
    return (
      <div className="text-center py-12 text-gray-500">
        Study not found or failed to load.
      </div>
    );
  }

  const tabs = [
    { key: 'projects', label: 'Projects', count: study.projects.length },
    { key: 'employees', label: 'Employees', count: study.employees.length },
    { key: 'qre', label: 'QRE Items', count: study.qre_items.length },
    { key: 'calculation', label: 'Calculation' },
    { key: 'narratives', label: 'Narratives' },
  ];

  const pendingCount = Object.values(approvalStatus).filter((s) => s === 'pending').length;
  const highRiskCount = study.projects.filter((p) =>
    p.risk_flags.some((f) => f.severity === 'high')
  ).length;

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{study.entity_name}</h1>
            <p className="text-gray-500">Tax Year {study.tax_year} - R&D Tax Credit Study Review</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
              Generate Preview
            </button>
            <button
              onClick={handleFinalizeStudy}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Finalize Study
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Total QRE</div>
            <div className="text-2xl font-bold text-gray-900">
              ${study.calculation.federal_asc.total_qre.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Estimated Credit</div>
            <div className="text-2xl font-bold text-green-600">
              ${study.calculation.total_credit.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Pending Review</div>
            <div className="text-2xl font-bold text-yellow-600">{pendingCount}</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500">High Risk Items</div>
            <div className="text-2xl font-bold text-red-600">{highRiskCount}</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.count !== undefined && (
                <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Project List */}
            <div className="col-span-1 space-y-3">
              <h3 className="font-semibold text-gray-700 mb-3">Projects</h3>
              {study.projects.map((project) => (
                <div
                  key={project.id}
                  onClick={() => setSelectedProject(project)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedProject?.id === project.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 truncate">{project.name}</span>
                    <span
                      className={`px-2 py-0.5 text-xs rounded ${
                        approvalStatus[project.id] === 'approved'
                          ? 'bg-green-100 text-green-800'
                          : approvalStatus[project.id] === 'rejected'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {approvalStatus[project.id]}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">${project.total_qre.toLocaleString()}</span>
                    <ConfidenceIndicator confidence={project.ai_confidence} />
                  </div>
                  {project.risk_flags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {project.risk_flags.slice(0, 2).map((flag, i) => (
                        <RiskBadge key={i} flag={flag} />
                      ))}
                      {project.risk_flags.length > 2 && (
                        <span className="text-xs text-gray-500">
                          +{project.risk_flags.length - 2} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Project Detail */}
            <div className="col-span-2">
              {selectedProject ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-gray-900">{selectedProject.name}</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleProjectApproval(selectedProject.id, 'approved')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          approvalStatus[selectedProject.id] === 'approved'
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-green-50 hover:text-green-700'
                        }`}
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleProjectApproval(selectedProject.id, 'rejected')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          approvalStatus[selectedProject.id] === 'rejected'
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-700'
                        }`}
                      >
                        Reject
                      </button>
                    </div>
                  </div>

                  <p className="text-gray-600">{selectedProject.description}</p>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Business Component:</span>
                      <span className="ml-2 font-medium">{selectedProject.business_component}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Total QRE:</span>
                      <span className="ml-2 font-medium">${selectedProject.total_qre.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Evidence Items:</span>
                      <span className="ml-2 font-medium">{selectedProject.evidence_count}</span>
                    </div>
                  </div>

                  {selectedProject.risk_flags.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h4 className="font-medium text-yellow-800 mb-2">Risk Flags</h4>
                      <div className="space-y-2">
                        {selectedProject.risk_flags.map((flag, i) => (
                          <div key={i} className="flex items-start gap-2">
                            <RiskBadge flag={flag} />
                            {flag.resolution && (
                              <span className="text-sm text-gray-600">
                                Suggested: {flag.resolution}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <FourPartTestCard
                    result={selectedProject.four_part_test}
                    onOverride={(element, score, notes) =>
                      handleOverride(selectedProject.id, element, score, notes)
                    }
                  />

                  {selectedProject.narratives.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-semibold text-gray-700">Project Narratives</h4>
                      {selectedProject.narratives.map((narrative) => (
                        <NarrativeEditor
                          key={narrative.id}
                          narrative={narrative}
                          onSave={(content) => handleNarrativeSave(narrative.id, content)}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-96 text-gray-400">
                  Select a project to review
                </div>
              )}
            </div>
          </div>
        )}

        {/* Employees Tab */}
        {activeTab === 'employees' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-700">Employee Allocations</h3>
              <div className="text-sm text-gray-500">
                Total Qualified Wages: $
                {study.employees
                  .reduce((sum, e) => sum + e.qualified_wages, 0)
                  .toLocaleString()}
              </div>
            </div>
            {study.employees.map((employee) => (
              <EmployeeAllocationEditor
                key={employee.id}
                employee={employee}
                projects={study.projects}
                onUpdate={handleEmployeeUpdate}
              />
            ))}
          </div>
        )}

        {/* QRE Tab */}
        {activeTab === 'qre' && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qualified</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {study.qre_items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          item.category === 'wages'
                            ? 'bg-blue-100 text-blue-800'
                            : item.category === 'supplies'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-purple-100 text-purple-800'
                        }`}
                      >
                        {item.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.description}</td>
                    <td className="px-4 py-3 text-sm text-right text-gray-600">
                      ${item.amount.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                      ${item.qualified_amount.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          item.status === 'approved'
                            ? 'bg-green-100 text-green-800'
                            : item.status === 'rejected'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Calculation Tab */}
        {activeTab === 'calculation' && (
          <CalculationSummary
            calculation={study.calculation}
            onMethodChange={handleMethodChange}
          />
        )}

        {/* Narratives Tab */}
        {activeTab === 'narratives' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-700">Study Narratives</h3>
              <button className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Regenerate All
              </button>
            </div>
            {study.projects.flatMap((p) =>
              p.narratives.map((narrative) => (
                <div key={narrative.id}>
                  <div className="text-sm text-gray-500 mb-1">Project: {p.name}</div>
                  <NarrativeEditor
                    narrative={narrative}
                    onSave={(content) => handleNarrativeSave(narrative.id, content)}
                  />
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewConsole;
