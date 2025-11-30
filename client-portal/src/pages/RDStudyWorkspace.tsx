/**
 * R&D Study Workspace
 *
 * Comprehensive workspace for managing individual R&D tax credit studies.
 * Enhanced UI/UX with working import tools, manual data entry, and progress saving.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTheme } from '../App';
import {
  RDStudy,
  RDProject,
  RDEmployee,
  RDQRE,
  RDStudyStatus,
  RDQualificationStatus,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Status badge component
const StatusBadge: React.FC<{ status: string; className?: string }> = ({ status, className = '' }) => {
  const getStatusColor = (s: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      intake: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      data_collection: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      qualification: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      qre_analysis: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
      calculation: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
      review: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      cpa_review: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      cpa_approval: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
      approved: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300',
      finalized: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      locked: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      qualified: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      not_qualified: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      needs_review: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      pending: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    };
    return colors[s.toLowerCase()] || colors.draft;
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)} ${className}`}>
      {status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
    </span>
  );
};

// Progress bar component
const ProgressBar: React.FC<{ progress: number; label?: string }> = ({ progress, label }) => (
  <div className="w-full">
    {label && <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">{label}</div>}
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
      <div
        className="bg-blue-600 h-2 rounded-full transition-all duration-500"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  </div>
);

// Modal component
const Modal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}> = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={onClose} />
        <div className={`relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl ${sizes[size]} w-full transform transition-all`}>
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="p-4">{children}</div>
        </div>
      </div>
    </div>
  );
};

// Employee form interface
interface EmployeeFormData {
  name: string;
  title: string;
  department: string;
  total_wages: string;
  qualified_time_percentage: string;
}

// Project form interface
interface ProjectFormData {
  name: string;
  description: string;
  department: string;
  business_component: string;
  start_date: string;
  end_date: string;
  is_ongoing: boolean;
}

// File analysis result interface
interface FileAnalysisResult {
  success: boolean;
  filename: string;
  file_size: number;
  sheets: Array<{ name: string; row_count: number }>;
  detected_data_types: string[];
  primary_data_type: string;
  columns: string[];
  column_mappings: Array<{
    source_column: string;
    confidence: number;
    suggested_field: string | null;
    data_type: string | null;
  }>;
  sample_data: Record<string, unknown>[];
  total_rows: number;
  overall_confidence: number;
  issues: Array<{ type: string; message: string; severity: string }>;
  recommendations: string[];
}

// Main component
const RDStudyWorkspace: React.FC = () => {
  const { id: studyId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { theme } = useTheme();

  // State
  const [study, setStudy] = useState<RDStudy | null>(null);
  const [employees, setEmployees] = useState<RDEmployee[]>([]);
  const [projects, setProjects] = useState<RDProject[]>([]);
  const [qres, setQres] = useState<RDQRE[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'data' | 'employees' | 'projects' | 'qre' | 'calculate' | 'export'>('overview');

  // Modal states
  const [showEmployeeModal, setShowEmployeeModal] = useState(false);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<RDEmployee | null>(null);
  const [editingProject, setEditingProject] = useState<RDProject | null>(null);

  // Form states
  const [employeeForm, setEmployeeForm] = useState<EmployeeFormData>({
    name: '',
    title: '',
    department: '',
    total_wages: '',
    qualified_time_percentage: '50',
  });
  const [projectForm, setProjectForm] = useState<ProjectFormData>({
    name: '',
    description: '',
    department: '',
    business_component: '',
    start_date: '',
    end_date: '',
    is_ongoing: false,
  });

  // File upload states
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [fileAnalysis, setFileAnalysis] = useState<FileAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [importing, setImporting] = useState(false);
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});

  // Calculation state
  const [calculationResult, setCalculationResult] = useState<any>(null);
  const [calculating, setCalculating] = useState(false);

  // Get auth token
  const getAuthHeaders = useCallback(() => {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, []);

  // Load study data
  const loadStudy = useCallback(async () => {
    if (!studyId) return;
    setLoading(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      const [studyRes, employeesRes, projectsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/rd-study/studies/${studyId}`, { headers }),
        axios.get(`${API_BASE_URL}/rd-study/studies/${studyId}/employees`, { headers }).catch(() => ({ data: [] })),
        axios.get(`${API_BASE_URL}/rd-study/studies/${studyId}/projects`, { headers }).catch(() => ({ data: [] })),
      ]);

      setStudy(studyRes.data);
      setEmployees(Array.isArray(employeesRes.data) ? employeesRes.data : []);
      setProjects(Array.isArray(projectsRes.data) ? projectsRes.data : []);
    } catch (err: any) {
      console.error('Error loading study:', err);
      setError(err.response?.data?.detail || 'Failed to load study. Please check your connection and try again.');
      // DO NOT use demo data - show error and let user retry
      setStudy(null);
    } finally {
      setLoading(false);
    }
  }, [studyId, getAuthHeaders]);

  useEffect(() => {
    loadStudy();
  }, [loadStudy]);

  // Auto-hide success message
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Handle employee form submission
  const handleSaveEmployee = async () => {
    if (!studyId || !employeeForm.name) return;
    setSaving(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      const payload = {
        name: employeeForm.name,
        title: employeeForm.title || null,
        department: employeeForm.department || null,
        total_wages: parseFloat(employeeForm.total_wages.replace(/[,$]/g, '')) || 0,
        qualified_time_percentage: parseFloat(employeeForm.qualified_time_percentage) || 50,
      };

      if (editingEmployee) {
        // Update existing employee
        await axios.patch(
          `${API_BASE_URL}/rd-study/studies/${studyId}/employees/${editingEmployee.id}`,
          payload,
          { headers }
        );
        setSuccessMessage('Employee updated successfully');
      } else {
        // Create new employee
        await axios.post(
          `${API_BASE_URL}/rd-study/studies/${studyId}/employees`,
          payload,
          { headers }
        );
        setSuccessMessage('Employee added successfully');
      }

      // Reload employees and close modal
      const res = await axios.get(`${API_BASE_URL}/rd-study/studies/${studyId}/employees`, { headers });
      setEmployees(Array.isArray(res.data) ? res.data : []);
      setShowEmployeeModal(false);
      setEditingEmployee(null);
      setEmployeeForm({ name: '', title: '', department: '', total_wages: '', qualified_time_percentage: '50' });
    } catch (err: any) {
      console.error('Error saving employee:', err);
      setError(err.response?.data?.detail || 'Failed to save employee');
    } finally {
      setSaving(false);
    }
  };

  // Handle project form submission
  const handleSaveProject = async () => {
    if (!studyId || !projectForm.name) return;
    setSaving(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      const payload = {
        name: projectForm.name,
        description: projectForm.description || null,
        department: projectForm.department || null,
        business_component: projectForm.business_component || null,
        start_date: projectForm.start_date || null,
        end_date: projectForm.end_date || null,
        is_ongoing: projectForm.is_ongoing,
      };

      if (editingProject) {
        // Update existing project
        await axios.patch(
          `${API_BASE_URL}/rd-study/studies/${studyId}/projects/${editingProject.id}`,
          payload,
          { headers }
        );
        setSuccessMessage('Project updated successfully');
      } else {
        // Create new project
        await axios.post(
          `${API_BASE_URL}/rd-study/studies/${studyId}/projects`,
          payload,
          { headers }
        );
        setSuccessMessage('Project added successfully');
      }

      // Reload projects and close modal
      const res = await axios.get(`${API_BASE_URL}/rd-study/studies/${studyId}/projects`, { headers });
      setProjects(Array.isArray(res.data) ? res.data : []);
      setShowProjectModal(false);
      setEditingProject(null);
      setProjectForm({ name: '', description: '', department: '', business_component: '', start_date: '', end_date: '', is_ongoing: false });
    } catch (err: any) {
      console.error('Error saving project:', err);
      setError(err.response?.data?.detail || 'Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  // Handle file analysis
  const handleAnalyzeFile = async () => {
    if (!uploadFile || !studyId) return;
    setAnalyzing(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      const formData = new FormData();
      formData.append('file', uploadFile);

      const res = await axios.post(
        `${API_BASE_URL}/rd-study/studies/${studyId}/upload/analyze`,
        formData,
        { headers: { ...headers, 'Content-Type': 'multipart/form-data' } }
      );

      setFileAnalysis(res.data);

      // Set default column mappings
      const defaultMappings: Record<string, string> = {};
      res.data.column_mappings?.forEach((m: any) => {
        if (m.suggested_field && m.confidence > 0.5) {
          defaultMappings[m.suggested_field] = m.source_column;
        }
      });
      setColumnMappings(defaultMappings);
    } catch (err: any) {
      console.error('Error analyzing file:', err);
      setError(err.response?.data?.detail || 'Failed to analyze file');
    } finally {
      setAnalyzing(false);
    }
  };

  // Handle data import
  const handleImportData = async () => {
    if (!fileAnalysis || !studyId) return;
    setImporting(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      // Use all_data if available (from AI analysis), otherwise use sample_data
      const dataToImport = (fileAnalysis as any).all_data || fileAnalysis.sample_data;

      const res = await axios.post(
        `${API_BASE_URL}/rd-study/studies/${studyId}/upload/import`,
        {
          data_type: fileAnalysis.primary_data_type,
          mappings: columnMappings,
          data: dataToImport,
        },
        { headers }
      );

      setSuccessMessage(`Successfully imported ${res.data.imported_count} records`);
      setShowImportModal(false);
      setFileAnalysis(null);
      setUploadFile(null);

      // Reload data
      loadStudy();
    } catch (err: any) {
      console.error('Error importing data:', err);
      setError(err.response?.data?.detail || 'Failed to import data');
    } finally {
      setImporting(false);
    }
  };

  // Handle credit calculation
  const handleCalculateCredits = async () => {
    if (!studyId) return;
    setCalculating(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      const res = await axios.post(
        `${API_BASE_URL}/rd-study/studies/${studyId}/calculate`,
        { include_states: true },
        { headers }
      );

      setCalculationResult(res.data);
      setSuccessMessage('Credits calculated successfully');
      loadStudy(); // Reload to get updated totals
    } catch (err: any) {
      console.error('Error calculating credits:', err);
      setError(err.response?.data?.detail || 'Failed to calculate credits');
    } finally {
      setCalculating(false);
    }
  };

  // Run AI study completion
  const handleAIComplete = async () => {
    if (!studyId) return;
    setCalculating(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      const res = await axios.post(
        `${API_BASE_URL}/rd-study/studies/${studyId}/ai/complete-study`,
        {},
        { headers }
      );

      setSuccessMessage(`AI Analysis complete! Federal Credit: ${formatCurrency(res.data.results?.final_credit)}`);
      loadStudy();
    } catch (err: any) {
      console.error('Error running AI completion:', err);
      setError(err.response?.data?.detail || 'Failed to run AI completion');
    } finally {
      setCalculating(false);
    }
  };

  // Calculate study progress
  const studyProgress = useMemo(() => {
    let progress = 0;
    if (study) {
      if (employees.length > 0) progress += 25;
      if (projects.length > 0) progress += 25;
      if (study.total_qre && study.total_qre > 0) progress += 25;
      if (study.federal_credit_final && study.federal_credit_final > 0) progress += 25;
    }
    return progress;
  }, [study, employees, projects]);

  // Format currency
  const formatCurrency = (value: number | string | null | undefined) => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (num == null || isNaN(num)) return '$0.00';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <div className={`${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b sticky top-0 z-10`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => navigate('/firm/rd-studies')}
                  className={`p-2 rounded-lg ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors`}
                >
                  <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <div>
                  <h1 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    {study?.name || 'R&D Study'}
                  </h1>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                      {study?.entity_name} | Tax Year {study?.tax_year}
                    </span>
                    {study?.status && <StatusBadge status={study.status} />}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-48">
                  <ProgressBar progress={studyProgress} label={`${studyProgress}% Complete`} />
                </div>
                <button
                  onClick={loadStudy}
                  className={`px-4 py-2 rounded-lg ${theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'} transition-colors flex items-center gap-2`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center gap-3">
            <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="text-green-800 dark:text-green-200">{successMessage}</span>
          </div>
        </div>
      )}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3">
            <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-800 dark:text-red-200">{error}</span>
            <button onClick={() => setError(null)} className="ml-auto text-red-600 dark:text-red-400 hover:text-red-800">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className={`${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} rounded-xl shadow-sm overflow-hidden`}>
          <div className={`flex border-b ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'} overflow-x-auto`}>
            {[
              { id: 'overview', label: 'Overview', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
              { id: 'data', label: 'Data Import', icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12' },
              { id: 'employees', label: 'Employees', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
              { id: 'projects', label: 'Projects', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
              { id: 'qre', label: 'QRE Summary', icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z' },
              { id: 'calculate', label: 'Calculate', icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z' },
              { id: 'export', label: 'Export', icon: 'M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? `${theme === 'dark' ? 'text-blue-400 border-blue-400' : 'text-blue-600 border-blue-600'} border-b-2`
                    : `${theme === 'dark' ? 'text-gray-400 hover:text-gray-300' : 'text-gray-500 hover:text-gray-700'}`
                }`}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
                </svg>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-blue-50'} rounded-xl p-4`}>
                    <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-blue-600'}`}>Employees</div>
                    <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-blue-900'}`}>{employees.length}</div>
                  </div>
                  <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-green-50'} rounded-xl p-4`}>
                    <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-green-600'}`}>Projects</div>
                    <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-green-900'}`}>{projects.length}</div>
                  </div>
                  <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-purple-50'} rounded-xl p-4`}>
                    <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-purple-600'}`}>Total QRE</div>
                    <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-purple-900'}`}>{formatCurrency(study?.total_qre)}</div>
                  </div>
                  <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-emerald-50'} rounded-xl p-4`}>
                    <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-emerald-600'}`}>Total Credits</div>
                    <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-emerald-900'}`}>{formatCurrency(study?.total_credits)}</div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div>
                  <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Quick Actions</h3>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <button
                      onClick={() => setShowImportModal(true)}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 transition-all"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <span className="text-sm font-medium">Import Data</span>
                    </button>
                    <button
                      onClick={() => setShowEmployeeModal(true)}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700 transition-all"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                      <span className="text-sm font-medium">Add Employee</span>
                    </button>
                    <button
                      onClick={() => setShowProjectModal(true)}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 text-white hover:from-purple-600 hover:to-purple-700 transition-all"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span className="text-sm font-medium">Add Project</span>
                    </button>
                    <button
                      onClick={handleAIComplete}
                      disabled={calculating || employees.length === 0}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-600 text-white hover:from-indigo-600 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <span className="text-sm font-medium">{calculating ? 'Running...' : 'AI Complete'}</span>
                    </button>
                    <button
                      onClick={handleCalculateCredits}
                      disabled={calculating || employees.length === 0}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 text-white hover:from-amber-600 hover:to-amber-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      <span className="text-sm font-medium">{calculating ? 'Calculating...' : 'Calculate'}</span>
                    </button>
                  </div>
                </div>

                {/* Getting Started Guide */}
                {employees.length === 0 && projects.length === 0 && (
                  <div className={`${theme === 'dark' ? 'bg-blue-900/20 border-blue-800' : 'bg-blue-50 border-blue-200'} border rounded-xl p-6`}>
                    <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-blue-300' : 'text-blue-900'}`}>Getting Started</h3>
                    <div className="space-y-3">
                      {[
                        { step: 1, text: 'Import payroll data or add employees manually', done: employees.length > 0 },
                        { step: 2, text: 'Add R&D projects with descriptions', done: projects.length > 0 },
                        { step: 3, text: 'Run AI analysis to qualify projects and allocate time', done: false },
                        { step: 4, text: 'Calculate and review credits', done: (study?.total_credits || 0) > 0 },
                      ].map((item) => (
                        <div key={item.step} className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                            item.done
                              ? 'bg-green-500 text-white'
                              : theme === 'dark' ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'
                          }`}>
                            {item.done ? (
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            ) : item.step}
                          </div>
                          <span className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'} ${item.done ? 'line-through opacity-50' : ''}`}>
                            {item.text}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Data Import Tab */}
            {activeTab === 'data' && (
              <div className="space-y-6">
                {/* Excel/CSV Import Section */}
                <div>
                  <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    Import from Excel/CSV
                  </h3>
                  <div className={`border-2 border-dashed rounded-xl p-8 text-center ${theme === 'dark' ? 'border-gray-600' : 'border-gray-300'}`}>
                    <svg className={`w-12 h-12 mx-auto mb-4 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <h4 className={`text-base font-medium mb-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>AI-Powered Excel Parser</h4>
                    <p className={`text-sm mb-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                      Upload payroll data, project lists, or expense reports. Our AI will intelligently detect and extract all relevant information.
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setUploadFile(file);
                          setShowImportModal(true);
                        }
                      }}
                      className="hidden"
                      id="file-upload"
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Select Excel/CSV File
                    </label>
                  </div>
                </div>

                {/* Payroll API Connections Section */}
                <div>
                  <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    Connect Payroll Provider
                  </h3>
                  <p className={`text-sm mb-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    Connect directly to your payroll system for automatic data import. We'll securely pull employee and wage information.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      {
                        id: 'adp_run',
                        name: 'ADP Run',
                        desc: 'RUN Powered by ADP for small businesses',
                        logo: '🅰️',
                        color: 'from-red-500 to-red-600'
                      },
                      {
                        id: 'justworks',
                        name: 'Justworks',
                        desc: 'PEO & payroll for growing companies',
                        logo: '🟦',
                        color: 'from-blue-500 to-blue-600'
                      },
                      {
                        id: 'paychex',
                        name: 'Paychex Flex',
                        desc: 'Comprehensive payroll & HR solutions',
                        logo: '🟩',
                        color: 'from-green-500 to-green-600'
                      },
                    ].map((provider) => (
                      <button
                        key={provider.id}
                        onClick={async () => {
                          try {
                            setError(null);
                            const headers = getAuthHeaders();
                            const res = await axios.post(
                              `${API_BASE_URL}/rd-study/studies/${studyId}/payroll/connect`,
                              { provider: provider.id },
                              { headers }
                            );
                            if (res.data.oauth_url) {
                              setSuccessMessage(`Connecting to ${provider.name}. OAuth flow would redirect to: ${res.data.oauth_url}`);
                            } else {
                              setSuccessMessage(`${provider.name} connection initiated`);
                            }
                          } catch (err: any) {
                            setError(err.response?.data?.detail || `Failed to connect to ${provider.name}`);
                          }
                        }}
                        className={`${theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600' : 'bg-white hover:bg-gray-50'} rounded-xl p-5 text-left transition-all border ${theme === 'dark' ? 'border-gray-600' : 'border-gray-200'} hover:shadow-lg`}
                      >
                        <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${provider.color} flex items-center justify-center text-white text-xl mb-3`}>
                          {provider.logo}
                        </div>
                        <div className={`font-semibold mb-1 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{provider.name}</div>
                        <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{provider.desc}</div>
                        <div className={`mt-3 text-sm font-medium ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`}>
                          Connect →
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Supported formats info */}
                <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'} rounded-xl p-6`}>
                  <h4 className={`font-semibold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Supported Data Types</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { name: 'Payroll Data', desc: 'Employee names, titles, wages, departments', icon: '💰' },
                      { name: 'Project Lists', desc: 'R&D projects with descriptions & timelines', icon: '📋' },
                      { name: 'Expense Reports', desc: 'Supplies, contractors, and research costs', icon: '📊' },
                    ].map((item) => (
                      <div key={item.name} className={`${theme === 'dark' ? 'bg-gray-600' : 'bg-white'} rounded-lg p-4`}>
                        <div className="text-2xl mb-2">{item.icon}</div>
                        <div className={`font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{item.name}</div>
                        <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Manual Entry Tip */}
                <div className={`${theme === 'dark' ? 'bg-blue-900/20 border-blue-800' : 'bg-blue-50 border-blue-200'} border rounded-xl p-4`}>
                  <div className="flex items-start gap-3">
                    <svg className={`w-5 h-5 mt-0.5 ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <div className={`font-medium ${theme === 'dark' ? 'text-blue-300' : 'text-blue-900'}`}>Prefer Manual Entry?</div>
                      <p className={`text-sm ${theme === 'dark' ? 'text-blue-400' : 'text-blue-700'}`}>
                        You can also add employees and projects manually using the tabs above. Our AI will help estimate qualified R&D percentages.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Employees Tab */}
            {activeTab === 'employees' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    Employees ({employees.length})
                  </h3>
                  <button
                    onClick={() => {
                      setEditingEmployee(null);
                      setEmployeeForm({ name: '', title: '', department: '', total_wages: '', qualified_time_percentage: '50' });
                      setShowEmployeeModal(true);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add Employee
                  </button>
                </div>

                {employees.length === 0 ? (
                  <div className={`text-center py-12 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <p className="mb-4">No employees added yet</p>
                    <button
                      onClick={() => setShowEmployeeModal(true)}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Add your first employee
                    </button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                          <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>Name</th>
                          <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>Title</th>
                          <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>Department</th>
                          <th className={`px-4 py-3 text-right text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>W-2 Wages</th>
                          <th className={`px-4 py-3 text-right text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>Qualified %</th>
                          <th className={`px-4 py-3 text-right text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>Qualified Wages</th>
                          <th className={`px-4 py-3 text-center text-xs font-medium uppercase tracking-wider ${theme === 'dark' ? 'text-gray-300' : 'text-gray-500'}`}>Actions</th>
                        </tr>
                      </thead>
                      <tbody className={`divide-y ${theme === 'dark' ? 'divide-gray-700' : 'divide-gray-200'}`}>
                        {employees.map((emp) => (
                          <tr key={emp.id} className={`${theme === 'dark' ? 'hover:bg-gray-700/50' : 'hover:bg-gray-50'}`}>
                            <td className={`px-4 py-3 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{emp.name}</td>
                            <td className={`px-4 py-3 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>{emp.title || '-'}</td>
                            <td className={`px-4 py-3 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>{emp.department || '-'}</td>
                            <td className={`px-4 py-3 text-right ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>{formatCurrency(emp.total_wages)}</td>
                            <td className={`px-4 py-3 text-right ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>{emp.qualified_time_percentage}%</td>
                            <td className={`px-4 py-3 text-right font-medium ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`}>{formatCurrency(emp.qualified_wages)}</td>
                            <td className="px-4 py-3 text-center">
                              <button
                                onClick={() => {
                                  setEditingEmployee(emp);
                                  setEmployeeForm({
                                    name: emp.name,
                                    title: emp.title || '',
                                    department: emp.department || '',
                                    total_wages: String(emp.total_wages || ''),
                                    qualified_time_percentage: String(emp.qualified_time_percentage || 50),
                                  });
                                  setShowEmployeeModal(true);
                                }}
                                className="text-blue-600 hover:text-blue-700"
                              >
                                Edit
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Projects Tab */}
            {activeTab === 'projects' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                    R&D Projects ({projects.length})
                  </h3>
                  <button
                    onClick={() => {
                      setEditingProject(null);
                      setProjectForm({ name: '', description: '', department: '', business_component: '', start_date: '', end_date: '', is_ongoing: false });
                      setShowProjectModal(true);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add Project
                  </button>
                </div>

                {projects.length === 0 ? (
                  <div className={`text-center py-12 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    <p className="mb-4">No projects added yet</p>
                    <button
                      onClick={() => setShowProjectModal(true)}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Add your first project
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {projects.map((proj) => (
                      <div key={proj.id} className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'} rounded-xl p-4`}>
                        <div className="flex justify-between items-start mb-2">
                          <h4 className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{proj.name}</h4>
                          <StatusBadge status={proj.qualification_status || 'pending'} />
                        </div>
                        {proj.description && (
                          <p className={`text-sm mb-3 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                            {proj.description.slice(0, 150)}{proj.description.length > 150 ? '...' : ''}
                          </p>
                        )}
                        <div className="flex justify-between items-center">
                          <span className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                            {proj.department || 'No department'}
                          </span>
                          <button
                            onClick={() => {
                              setEditingProject(proj);
                              setProjectForm({
                                name: proj.name,
                                description: proj.description || '',
                                department: proj.department || '',
                                business_component: proj.business_component || '',
                                start_date: proj.start_date || '',
                                end_date: proj.end_date || '',
                                is_ongoing: proj.is_ongoing || false,
                              });
                              setShowProjectModal(true);
                            }}
                            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                          >
                            Edit
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* QRE Summary Tab */}
            {activeTab === 'qre' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { label: 'Wage QRE', value: employees.reduce((sum, emp) => sum + (emp.qualified_wages || 0), 0), color: 'blue' },
                    { label: 'Supply QRE', value: qres.filter(q => q.category === 'supplies').reduce((sum, q) => sum + (q.qualified_amount || 0), 0), color: 'green' },
                    { label: 'Contract QRE', value: qres.filter(q => q.category === 'contract_research').reduce((sum, q) => sum + (q.qualified_amount || 0), 0), color: 'purple' },
                  ].map((item) => (
                    <div key={item.label} className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'} rounded-xl p-4`}>
                      <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{item.label}</div>
                      <div className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{formatCurrency(item.value)}</div>
                    </div>
                  ))}
                </div>
                <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-blue-50'} rounded-xl p-6`}>
                  <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-blue-600'}`}>Total Qualified Research Expenses</div>
                  <div className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-blue-900'}`}>{formatCurrency(study?.total_qre)}</div>
                </div>
              </div>
            )}

            {/* Calculate Tab */}
            {activeTab === 'calculate' && (
              <div className="space-y-6">
                <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'} rounded-xl p-6`}>
                  <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Calculate R&D Tax Credits</h3>
                  <p className={`mb-4 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                    Run the calculation engine to compute federal and state R&D tax credits based on your study data.
                  </p>
                  <div className="flex gap-4">
                    <button
                      onClick={handleAIComplete}
                      disabled={calculating || employees.length === 0}
                      className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                      {calculating ? (
                        <>
                          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          Running AI Analysis...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          AI Complete Study
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleCalculateCredits}
                      disabled={calculating || employees.length === 0}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      Calculate Only
                    </button>
                  </div>
                </div>

                {/* Calculation Results */}
                {(study?.federal_credit_final || calculationResult) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className={`${theme === 'dark' ? 'bg-blue-900/30' : 'bg-blue-50'} rounded-xl p-6`}>
                      <div className={`text-sm ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`}>Federal Credit (Regular)</div>
                      <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-blue-900'}`}>{formatCurrency(study?.federal_credit_regular)}</div>
                    </div>
                    <div className={`${theme === 'dark' ? 'bg-green-900/30' : 'bg-green-50'} rounded-xl p-6`}>
                      <div className={`text-sm ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`}>Federal Credit (ASC)</div>
                      <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-green-900'}`}>{formatCurrency(study?.federal_credit_asc)}</div>
                    </div>
                    <div className={`${theme === 'dark' ? 'bg-purple-900/30' : 'bg-purple-50'} rounded-xl p-6`}>
                      <div className={`text-sm ${theme === 'dark' ? 'text-purple-400' : 'text-purple-600'}`}>State Credits</div>
                      <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-purple-900'}`}>{formatCurrency(study?.total_state_credits)}</div>
                    </div>
                    <div className={`${theme === 'dark' ? 'bg-emerald-900/30' : 'bg-emerald-50'} rounded-xl p-6`}>
                      <div className={`text-sm ${theme === 'dark' ? 'text-emerald-400' : 'text-emerald-600'}`}>Total Credits</div>
                      <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-emerald-900'}`}>{formatCurrency(study?.total_credits)}</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Export Tab */}
            {activeTab === 'export' && (
              <div className="space-y-6">
                <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Generate Reports</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { name: 'Excel Workbook', desc: 'Complete study data in Excel format', icon: '📊', type: 'excel' },
                    { name: 'PDF Report', desc: 'Professional PDF study report', icon: '📄', type: 'pdf' },
                    { name: 'Form 6765', desc: 'IRS Form 6765 data', icon: '📋', type: 'form_6765' },
                  ].map((item) => (
                    <button
                      key={item.type}
                      onClick={async () => {
                        try {
                          const headers = getAuthHeaders();
                          await axios.post(
                            `${API_BASE_URL}/rd-study/studies/${studyId}/outputs/generate`,
                            { output_types: [item.type], include_draft_watermark: true },
                            { headers }
                          );
                          setSuccessMessage(`${item.name} generated successfully`);
                        } catch (err: any) {
                          setError(err.response?.data?.detail || `Failed to generate ${item.name}`);
                        }
                      }}
                      className={`${theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-50 hover:bg-gray-100'} rounded-xl p-6 text-left transition-colors`}
                    >
                      <div className="text-3xl mb-3">{item.icon}</div>
                      <div className={`font-semibold mb-1 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{item.name}</div>
                      <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{item.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Employee Modal */}
      <Modal
        isOpen={showEmployeeModal}
        onClose={() => {
          setShowEmployeeModal(false);
          setEditingEmployee(null);
        }}
        title={editingEmployee ? 'Edit Employee' : 'Add Employee'}
      >
        <div className="space-y-4">
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Name *
            </label>
            <input
              type="text"
              value={employeeForm.name}
              onChange={(e) => setEmployeeForm({ ...employeeForm, name: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Title
            </label>
            <input
              type="text"
              value={employeeForm.title}
              onChange={(e) => setEmployeeForm({ ...employeeForm, title: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
              placeholder="Software Engineer"
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Department
            </label>
            <input
              type="text"
              value={employeeForm.department}
              onChange={(e) => setEmployeeForm({ ...employeeForm, department: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
              placeholder="Engineering"
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              W-2 Wages *
            </label>
            <input
              type="text"
              value={employeeForm.total_wages}
              onChange={(e) => setEmployeeForm({ ...employeeForm, total_wages: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
              placeholder="$100,000"
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Qualified Time % (0-100)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={employeeForm.qualified_time_percentage}
              onChange={(e) => setEmployeeForm({ ...employeeForm, qualified_time_percentage: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              onClick={() => {
                setShowEmployeeModal(false);
                setEditingEmployee(null);
              }}
              className={`px-4 py-2 rounded-lg ${theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEmployee}
              disabled={saving || !employeeForm.name || !employeeForm.total_wages}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : editingEmployee ? 'Update' : 'Add Employee'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Add Project Modal */}
      <Modal
        isOpen={showProjectModal}
        onClose={() => {
          setShowProjectModal(false);
          setEditingProject(null);
        }}
        title={editingProject ? 'Edit Project' : 'Add Project'}
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Project Name *
            </label>
            <input
              type="text"
              value={projectForm.name}
              onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
              placeholder="New Product Development"
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Description
            </label>
            <textarea
              rows={4}
              value={projectForm.description}
              onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
              placeholder="Describe the R&D activities, technical uncertainties, and experimentation process..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                Department
              </label>
              <input
                type="text"
                value={projectForm.department}
                onChange={(e) => setProjectForm({ ...projectForm, department: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
                placeholder="Engineering"
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                Business Component
              </label>
              <input
                type="text"
                value={projectForm.business_component}
                onChange={(e) => setProjectForm({ ...projectForm, business_component: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
                placeholder="Software Platform"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_ongoing"
              checked={projectForm.is_ongoing}
              onChange={(e) => setProjectForm({ ...projectForm, is_ongoing: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <label htmlFor="is_ongoing" className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              Project is ongoing
            </label>
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              onClick={() => {
                setShowProjectModal(false);
                setEditingProject(null);
              }}
              className={`px-4 py-2 rounded-lg ${theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
            >
              Cancel
            </button>
            <button
              onClick={handleSaveProject}
              disabled={saving || !projectForm.name}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : editingProject ? 'Update' : 'Add Project'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Import Data Modal */}
      <Modal
        isOpen={showImportModal}
        onClose={() => {
          setShowImportModal(false);
          setFileAnalysis(null);
          setUploadFile(null);
        }}
        title="Import Data"
        size="xl"
      >
        <div className="space-y-4">
          {!fileAnalysis ? (
            <>
              <div className={`border-2 border-dashed rounded-lg p-6 text-center ${theme === 'dark' ? 'border-gray-600' : 'border-gray-300'}`}>
                <input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="import-file"
                />
                <label htmlFor="import-file" className="cursor-pointer">
                  <svg className={`w-10 h-10 mx-auto mb-3 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}>
                    {uploadFile ? uploadFile.name : 'Click to select file or drag & drop'}
                  </p>
                </label>
              </div>
              {uploadFile && (
                <button
                  onClick={handleAnalyzeFile}
                  disabled={analyzing}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {analyzing ? 'Analyzing...' : 'Analyze File'}
                </button>
              )}
            </>
          ) : (
            <>
              <div className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'} rounded-lg p-4`}>
                <div className="flex justify-between items-start">
                  <div>
                    <div className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{fileAnalysis.filename}</div>
                    <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                      {fileAnalysis.total_rows} rows | Detected as: {fileAnalysis.primary_data_type}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${fileAnalysis.overall_confidence > 0.7 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {Math.round(fileAnalysis.overall_confidence * 100)}% confidence
                  </span>
                </div>
              </div>

              {/* Column Mappings */}
              <div>
                <h4 className={`font-medium mb-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Column Mappings</h4>
                <div className="space-y-2">
                  {fileAnalysis.column_mappings.filter(m => m.confidence > 0.3).map((mapping, idx) => (
                    <div key={idx} className="flex items-center gap-3">
                      <span className={`text-sm w-32 truncate ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{mapping.source_column}</span>
                      <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                      <select
                        value={columnMappings[mapping.suggested_field || ''] === mapping.source_column ? mapping.suggested_field || '' : ''}
                        onChange={(e) => setColumnMappings({ ...columnMappings, [e.target.value]: mapping.source_column })}
                        className={`flex-1 px-2 py-1 text-sm border rounded ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'}`}
                      >
                        <option value="">Unmapped</option>
                        <option value="name">Name</option>
                        <option value="title">Title</option>
                        <option value="department">Department</option>
                        <option value="wages">Wages</option>
                        <option value="qualified_time">Qualified %</option>
                        <option value="description">Description</option>
                        <option value="amount">Amount</option>
                        <option value="vendor">Vendor</option>
                      </select>
                      <span className={`text-xs ${mapping.confidence > 0.7 ? 'text-green-600' : 'text-yellow-600'}`}>
                        {Math.round(mapping.confidence * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Data Preview */}
              {fileAnalysis.sample_data.length > 0 && (
                <div>
                  <h4 className={`font-medium mb-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Sample Data</h4>
                  <div className="overflow-x-auto max-h-40">
                    <table className="text-sm w-full">
                      <thead>
                        <tr className={theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}>
                          {fileAnalysis.columns.slice(0, 5).map((col, idx) => (
                            <th key={idx} className="px-2 py-1 text-left">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {fileAnalysis.sample_data.slice(0, 3).map((row, idx) => (
                          <tr key={idx} className={`${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'} border-t`}>
                            {fileAnalysis.columns.slice(0, 5).map((col, cidx) => (
                              <td key={cidx} className="px-2 py-1 truncate max-w-32">{String(row[col] || '')}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => {
                    setFileAnalysis(null);
                    setUploadFile(null);
                  }}
                  className={`px-4 py-2 rounded-lg ${theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
                >
                  Start Over
                </button>
                <button
                  onClick={handleImportData}
                  disabled={importing}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {importing ? 'Importing...' : `Import ${fileAnalysis.total_rows} Records`}
                </button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default RDStudyWorkspace;
