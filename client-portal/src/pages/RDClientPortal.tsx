/**
 * R&D Client Portal - Enhanced Data Collection Interface
 *
 * A professional, user-friendly portal for clients to provide R&D Tax Credit data.
 * Supports three data input methods:
 * 1. Manual entry
 * 2. Spreadsheet upload (Excel/CSV)
 * 3. Payroll API connection (ADP, Gusto, Paychex, etc.)
 *
 * Includes comprehensive 4-part test questionnaire for projects.
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical, Upload, Users, Building2, FileSpreadsheet, CheckCircle,
  AlertTriangle, Clock, Send, Plus, Trash2, Wand2, Loader2, Shield,
  Calendar, File, X, ChevronRight, ChevronLeft, ChevronDown, Brain,
  Save, Info, Database, Link, Settings, HelpCircle, CheckSquare,
  Square, AlertCircle, Lightbulb, Target, Microscope, Beaker,
  FileText, DollarSign, Briefcase, ArrowRight, ExternalLink,
  RefreshCw, Lock, Unlock, Eye, EyeOff, Copy, Download, Edit3,
  BarChart3, PieChart, TrendingUp, Zap
} from 'lucide-react';
import axios from 'axios';

// Environment configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
const PORTAL_NAME = import.meta.env.VITE_RD_PORTAL_NAME || 'R&D Tax Credit Portal';

// Types
interface InvitationData {
  study_id: string;
  client_email: string;
  client_name: string;
  company_name: string;
  study_name: string;
  tax_year: number;
  firm_name: string;
  firm_logo?: string;
  invited_by: string;
  deadline: string | null;
  expires_at: string;
  data_requirements: DataRequirement[];
  existing_data?: ExistingData;
}

interface DataRequirement {
  id: string;
  type: 'employees' | 'projects' | 'supplies' | 'contracts' | 'documents';
  label: string;
  description: string;
  required: boolean;
  completed: boolean;
}

interface ExistingData {
  employees_count: number;
  projects_count: number;
  documents_count: number;
  last_submission?: string;
}

interface Employee {
  id: string;
  employee_id?: string;
  name: string;
  title: string;
  department: string;
  hire_date?: string;
  annual_wages: number;
  bonus?: number;
  qualified_time_percentage: number;
  time_source: 'estimate' | 'timesheet' | 'survey' | 'api';
  rd_activities?: string;
  projects_assigned?: string[];
}

interface Project {
  id: string;
  name: string;
  code?: string;
  description: string;
  business_component: string;
  department?: string;
  start_date: string;
  end_date: string | null;
  is_ongoing: boolean;
  employees_involved: string[];
  four_part_test: FourPartTest;
  ai_qualification_score?: number;
}

interface FourPartTest {
  permitted_purpose: {
    answer: string;
    new_functionality: boolean;
    improved_performance: boolean;
    improved_reliability: boolean;
    improved_quality: boolean;
    examples: string;
  };
  technological_nature: {
    answer: string;
    uses_engineering: boolean;
    uses_physics: boolean;
    uses_biology: boolean;
    uses_chemistry: boolean;
    uses_computer_science: boolean;
    specific_technologies: string;
  };
  elimination_uncertainty: {
    answer: string;
    capability_uncertain: boolean;
    method_uncertain: boolean;
    design_uncertain: boolean;
    uncertainty_examples: string;
  };
  process_experimentation: {
    answer: string;
    systematic_approach: boolean;
    tested_alternatives: boolean;
    documented_results: boolean;
    experimentation_examples: string;
  };
}

interface SupplyExpense {
  id: string;
  date: string;
  description: string;
  vendor: string;
  amount: number;
  gl_account?: string;
  project_code?: string;
  qualified_percentage: number;
}

interface ContractResearch {
  id: string;
  contractor_name: string;
  contractor_type: 'university' | 'research_org' | 'consultant' | 'other';
  contract_date: string;
  description: string;
  total_amount: number;
  qualified_percentage: number;
  project_code?: string;
}

interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  category: 'payroll' | 'timesheet' | 'project_docs' | 'contracts' | 'other';
  size: number;
  uploaded_at: string;
  status: 'pending' | 'processing' | 'processed' | 'error';
}

interface PayrollConnection {
  id: string;
  provider: string;
  status: 'connected' | 'pending' | 'error' | 'disconnected';
  last_sync?: string;
  employees_synced?: number;
}

type TabType = 'overview' | 'data-input' | 'employees' | 'projects' | 'expenses' | 'documents' | 'review';
type InputMethod = 'manual' | 'upload' | 'api';

// Default 4-part test values
const defaultFourPartTest: FourPartTest = {
  permitted_purpose: {
    answer: '',
    new_functionality: false,
    improved_performance: false,
    improved_reliability: false,
    improved_quality: false,
    examples: '',
  },
  technological_nature: {
    answer: '',
    uses_engineering: false,
    uses_physics: false,
    uses_biology: false,
    uses_chemistry: false,
    uses_computer_science: false,
    specific_technologies: '',
  },
  elimination_uncertainty: {
    answer: '',
    capability_uncertain: false,
    method_uncertain: false,
    design_uncertain: false,
    uncertainty_examples: '',
  },
  process_experimentation: {
    answer: '',
    systematic_approach: false,
    tested_alternatives: false,
    documented_results: false,
    experimentation_examples: '',
  },
};

// Animation variants
const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

const slideIn = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

export function RDClientPortal() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  // Core state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [invitation, setInvitation] = useState<InvitationData | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [submitted, setSubmitted] = useState(false);

  // Data input method
  const [inputMethod, setInputMethod] = useState<InputMethod>('manual');
  const [showInputMethodSelector, setShowInputMethodSelector] = useState(false);

  // Data states
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [supplies, setSupplies] = useState<SupplyExpense[]>([]);
  const [contracts, setContracts] = useState<ContractResearch[]>([]);
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [payrollConnection, setPayrollConnection] = useState<PayrollConnection | null>(null);
  const [notes, setNotes] = useState('');

  // UI states
  const [expandedProject, setExpandedProject] = useState<string | null>(null);
  const [generatingDescription, setGeneratingDescription] = useState<string | null>(null);
  const [processingUpload, setProcessingUpload] = useState(false);

  // Validate token on mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setError('No invitation token provided. Please use the link from your email.');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(
          `${API_BASE_URL}/rd-study/client-invitations/validate`,
          { params: { token } }
        );
        setInvitation(response.data);

        // Load any existing data
        if (response.data.existing_data) {
          await loadExistingData(response.data.study_id);
        }
      } catch (err) {
        if (axios.isAxiosError(err)) {
          if (err.response?.status === 410) {
            setError('This invitation has expired or already been used. Please contact your CPA firm for a new invitation.');
          } else if (err.response?.status === 404) {
            setError('Invalid invitation link. Please check the link from your email or contact your CPA firm.');
          } else {
            setError('Unable to validate invitation. Please try again later.');
          }
        } else {
          setError('An unexpected error occurred.');
        }
      } finally {
        setLoading(false);
      }
    };

    validateToken();
  }, [token]);

  // Load existing data
  const loadExistingData = async (studyId: string) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/rd-study/client-data/${studyId}`,
        { params: { token } }
      );
      if (response.data.employees) setEmployees(response.data.employees);
      if (response.data.projects) setProjects(response.data.projects);
      if (response.data.supplies) setSupplies(response.data.supplies);
      if (response.data.contracts) setContracts(response.data.contracts);
      if (response.data.documents) setDocuments(response.data.documents);
    } catch (err) {
      console.error('Failed to load existing data:', err);
    }
  };

  // Auto-save functionality
  const autoSave = useCallback(async () => {
    if (!token || !invitation) return;

    setSaving(true);
    try {
      await axios.post(`${API_BASE_URL}/rd-study/client-data/auto-save`, {
        token,
        study_id: invitation.study_id,
        employees,
        projects,
        supplies,
        contracts,
        notes,
      });
      setSuccess('Progress saved');
      setTimeout(() => setSuccess(null), 2000);
    } catch (err) {
      console.error('Auto-save failed:', err);
    } finally {
      setSaving(false);
    }
  }, [token, invitation, employees, projects, supplies, contracts, notes]);

  // Calculate progress
  const progress = useMemo(() => {
    const employeesComplete = employees.filter(e => e.name && e.annual_wages > 0).length;
    const projectsComplete = projects.filter(p =>
      p.name &&
      p.description &&
      p.four_part_test.permitted_purpose.answer
    ).length;
    const hasDocuments = documents.length > 0;

    const total = employees.length + projects.length + documents.length;
    const complete = employeesComplete + projectsComplete + (hasDocuments ? 1 : 0);

    return {
      employees: { total: employees.length, complete: employeesComplete },
      projects: { total: projects.length, complete: projectsComplete },
      documents: documents.length,
      overall: total > 0 ? Math.round((complete / (employees.length + projects.length + 1)) * 100) : 0,
    };
  }, [employees, projects, documents]);

  // Add employee
  const addEmployee = useCallback(() => {
    const newEmployee: Employee = {
      id: `emp-${Date.now()}`,
      name: '',
      title: '',
      department: '',
      annual_wages: 0,
      qualified_time_percentage: 0,
      time_source: inputMethod === 'api' ? 'api' : 'estimate',
    };
    setEmployees(prev => [...prev, newEmployee]);
  }, [inputMethod]);

  // Update employee
  const updateEmployee = useCallback((id: string, updates: Partial<Employee>) => {
    setEmployees(prev =>
      prev.map(emp => (emp.id === id ? { ...emp, ...updates } : emp))
    );
  }, []);

  // Remove employee
  const removeEmployee = useCallback((id: string) => {
    setEmployees(prev => prev.filter(emp => emp.id !== id));
  }, []);

  // Add project
  const addProject = useCallback(() => {
    const newProject: Project = {
      id: `proj-${Date.now()}`,
      name: '',
      description: '',
      business_component: '',
      start_date: '',
      end_date: null,
      is_ongoing: true,
      employees_involved: [],
      four_part_test: { ...defaultFourPartTest },
    };
    setProjects(prev => [...prev, newProject]);
    setExpandedProject(newProject.id);
  }, []);

  // Update project
  const updateProject = useCallback((id: string, updates: Partial<Project>) => {
    setProjects(prev =>
      prev.map(proj => (proj.id === id ? { ...proj, ...updates } : proj))
    );
  }, []);

  // Update project 4-part test
  const updateProjectFourPartTest = useCallback((
    projectId: string,
    section: keyof FourPartTest,
    updates: Partial<FourPartTest[typeof section]>
  ) => {
    setProjects(prev =>
      prev.map(proj => {
        if (proj.id !== projectId) return proj;
        return {
          ...proj,
          four_part_test: {
            ...proj.four_part_test,
            [section]: {
              ...proj.four_part_test[section],
              ...updates,
            },
          },
        };
      })
    );
  }, []);

  // Remove project
  const removeProject = useCallback((id: string) => {
    setProjects(prev => prev.filter(proj => proj.id !== id));
    if (expandedProject === id) setExpandedProject(null);
  }, [expandedProject]);

  // Generate AI description for project
  const generateProjectDescription = useCallback(async (projectId: string) => {
    const project = projects.find(p => p.id === projectId);
    if (!project || !project.name) return;

    setGeneratingDescription(projectId);
    try {
      const response = await axios.post(`${API_BASE_URL}/rd-study/ai/generate-description`, {
        token,
        project_name: project.name,
        business_component: project.business_component,
        context: project.description,
        four_part_test: project.four_part_test,
      });

      updateProject(projectId, {
        description: response.data.description || project.description,
        four_part_test: {
          ...project.four_part_test,
          permitted_purpose: {
            ...project.four_part_test.permitted_purpose,
            answer: response.data.permitted_purpose || project.four_part_test.permitted_purpose.answer,
          },
          technological_nature: {
            ...project.four_part_test.technological_nature,
            answer: response.data.technological_nature || project.four_part_test.technological_nature.answer,
          },
          elimination_uncertainty: {
            ...project.four_part_test.elimination_uncertainty,
            answer: response.data.uncertainty || project.four_part_test.elimination_uncertainty.answer,
          },
          process_experimentation: {
            ...project.four_part_test.process_experimentation,
            answer: response.data.experimentation || project.four_part_test.process_experimentation.answer,
          },
        },
        ai_qualification_score: response.data.qualification_score,
      });

      setSuccess('AI-generated content added. Please review and edit as needed.');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to generate description:', err);
      setError('Failed to generate AI description. Please try again.');
      setTimeout(() => setError(null), 3000);
    } finally {
      setGeneratingDescription(null);
    }
  }, [projects, token, updateProject]);

  // Handle spreadsheet upload
  const handleSpreadsheetUpload = useCallback(async (file: File, dataType: 'employees' | 'supplies' | 'contracts') => {
    if (!token) return;

    setProcessingUpload(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('data_type', dataType);
      formData.append('token', token);

      const response = await axios.post(
        `${API_BASE_URL}/rd-study/client-data/import-spreadsheet`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      if (dataType === 'employees' && response.data.employees) {
        setEmployees(prev => [...prev, ...response.data.employees.map((e: any) => ({
          ...e,
          id: `emp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          time_source: 'api',
        }))]);
      } else if (dataType === 'supplies' && response.data.supplies) {
        setSupplies(prev => [...prev, ...response.data.supplies.map((s: any) => ({
          ...s,
          id: `sup-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        }))]);
      } else if (dataType === 'contracts' && response.data.contracts) {
        setContracts(prev => [...prev, ...response.data.contracts.map((c: any) => ({
          ...c,
          id: `con-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        }))]);
      }

      // Add document record
      const newDoc: UploadedDocument = {
        id: `doc-${Date.now()}`,
        name: file.name,
        type: file.type,
        category: dataType === 'employees' ? 'payroll' : dataType === 'supplies' ? 'other' : 'contracts',
        size: file.size,
        uploaded_at: new Date().toISOString(),
        status: 'processed',
      };
      setDocuments(prev => [...prev, newDoc]);

      setSuccess(`Successfully imported ${response.data.record_count || 0} records from ${file.name}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Spreadsheet upload failed:', err);
      setError('Failed to process spreadsheet. Please check the format and try again.');
      setTimeout(() => setError(null), 5000);
    } finally {
      setProcessingUpload(false);
    }
  }, [token]);

  // Handle document upload
  const handleDocumentUpload = useCallback(async (files: FileList | null, category: UploadedDocument['category']) => {
    if (!files || files.length === 0 || !token) return;

    for (const file of Array.from(files)) {
      const newDoc: UploadedDocument = {
        id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        type: file.type,
        category,
        size: file.size,
        uploaded_at: new Date().toISOString(),
        status: 'pending',
      };
      setDocuments(prev => [...prev, newDoc]);

      // Upload in background
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', category);
        formData.append('token', token);

        await axios.post(
          `${API_BASE_URL}/rd-study/client-data/upload-document`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        );

        setDocuments(prev =>
          prev.map(d => (d.id === newDoc.id ? { ...d, status: 'processed' } : d))
        );
      } catch (err) {
        setDocuments(prev =>
          prev.map(d => (d.id === newDoc.id ? { ...d, status: 'error' } : d))
        );
      }
    }
  }, [token]);

  // Connect payroll API
  const connectPayrollAPI = useCallback(async (provider: string, credentials: any) => {
    if (!token) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/rd-study/client-data/connect-payroll`, {
        token,
        provider,
        credentials,
      });

      setPayrollConnection({
        id: response.data.connection_id,
        provider,
        status: 'pending',
      });

      setSuccess(`Connecting to ${provider}... This may take a few minutes.`);
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError('Failed to connect to payroll provider. Please check your credentials.');
      setTimeout(() => setError(null), 5000);
    }
  }, [token]);

  // Sync payroll data
  const syncPayrollData = useCallback(async () => {
    if (!token || !payrollConnection) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/rd-study/client-data/sync-payroll`, {
        token,
        connection_id: payrollConnection.id,
      });

      if (response.data.employees) {
        setEmployees(response.data.employees.map((e: any) => ({
          ...e,
          id: `emp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          time_source: 'api',
        })));
      }

      setPayrollConnection(prev => prev ? {
        ...prev,
        status: 'connected',
        last_sync: new Date().toISOString(),
        employees_synced: response.data.employees?.length || 0,
      } : null);

      setSuccess(`Synced ${response.data.employees?.length || 0} employees from ${payrollConnection.provider}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to sync payroll data. Please try again.');
      setTimeout(() => setError(null), 5000);
    }
  }, [token, payrollConnection]);

  // Submit data
  const handleSubmit = useCallback(async () => {
    if (!token || !invitation) return;

    setSubmitting(true);
    try {
      await axios.post(`${API_BASE_URL}/rd-study/client-data/submit`, {
        token,
        study_id: invitation.study_id,
        employees,
        projects,
        supplies,
        contracts,
        documents: documents.map(d => ({ id: d.id, name: d.name, type: d.type, category: d.category })),
        notes,
        payroll_connection: payrollConnection ? {
          provider: payrollConnection.provider,
          connection_id: payrollConnection.id,
        } : null,
      });
      setSubmitted(true);
    } catch (err) {
      console.error('Submission failed:', err);
      setError('Failed to submit data. Please try again.');
      setTimeout(() => setError(null), 5000);
    } finally {
      setSubmitting(false);
    }
  }, [token, invitation, employees, projects, supplies, contracts, documents, notes, payrollConnection]);

  // Render loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <FlaskConical className="w-10 h-10 text-white" />
            </div>
            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
              <Loader2 className="w-5 h-5 text-emerald-600 animate-spin" />
            </div>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Your Portal</h2>
          <p className="text-gray-500">Validating your secure access...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !invitation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-gray-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center"
        >
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-10 h-10 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">Access Error</h1>
          <p className="text-gray-600 mb-8">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => window.location.reload()}
              className="w-full px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-medium"
            >
              Try Again
            </button>
            <p className="text-sm text-gray-500">
              Need help? Contact your CPA firm directly.
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  // Render success state
  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-blue-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-lg w-full bg-white rounded-2xl shadow-xl p-8 text-center"
        >
          <div className="w-24 h-24 bg-gradient-to-br from-emerald-400 to-green-500 rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Submission Complete!</h1>
          <p className="text-lg text-gray-600 mb-6">
            Thank you for providing your R&D study information.
          </p>
          <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-xl p-6 mb-8">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-emerald-600">{employees.length}</p>
                <p className="text-sm text-gray-600">Employees</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600">{projects.length}</p>
                <p className="text-sm text-gray-600">Projects</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-600">{documents.length}</p>
                <p className="text-sm text-gray-600">Documents</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 rounded-xl p-4 mb-6 text-left">
            <h3 className="font-semibold text-gray-900 mb-2">What happens next?</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span><strong>{invitation?.firm_name}</strong> will review your data</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span>They may contact you if additional information is needed</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span>You'll receive an update once the study is complete</span>
              </li>
            </ul>
          </div>
          <p className="text-sm text-gray-500">You may safely close this page.</p>
        </motion.div>
      </div>
    );
  }

  if (!invitation) return null;

  // Tab configuration
  const tabs: { id: TabType; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'data-input', label: 'Data Input', icon: <Database className="w-4 h-4" /> },
    { id: 'employees', label: 'Employees', icon: <Users className="w-4 h-4" />, badge: employees.length },
    { id: 'projects', label: 'Projects', icon: <FlaskConical className="w-4 h-4" />, badge: projects.length },
    { id: 'expenses', label: 'Expenses', icon: <DollarSign className="w-4 h-4" />, badge: supplies.length + contracts.length },
    { id: 'documents', label: 'Documents', icon: <FileSpreadsheet className="w-4 h-4" />, badge: documents.length },
    { id: 'review', label: 'Review & Submit', icon: <Send className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50/30">
      {/* Top notification bar */}
      <AnimatePresence>
        {(error || success || saving) && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className={`fixed top-0 left-0 right-0 z-50 px-4 py-3 text-center text-sm font-medium ${
              error ? 'bg-red-500 text-white' :
              success ? 'bg-emerald-500 text-white' :
              'bg-blue-500 text-white'
            }`}
          >
            {error || success || 'Saving...'}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200/60 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              {invitation.firm_logo ? (
                <img src={invitation.firm_logo} alt={invitation.firm_name} className="h-10" />
              ) : (
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-xl flex items-center justify-center shadow-md">
                  <FlaskConical className="w-6 h-6 text-white" />
                </div>
              )}
              <div>
                <h1 className="text-lg font-semibold text-gray-900">{PORTAL_NAME}</h1>
                <p className="text-sm text-gray-500">{invitation.firm_name}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-gray-900">{invitation.company_name}</p>
                <p className="text-xs text-gray-500">Tax Year {invitation.tax_year}</p>
              </div>

              {invitation.deadline && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-50 border border-amber-200 rounded-lg">
                  <Clock className="w-4 h-4 text-amber-600" />
                  <span className="text-sm font-medium text-amber-700">Due: {invitation.deadline}</span>
                </div>
              )}

              <button
                onClick={autoSave}
                disabled={saving}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition-colors"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span className="hidden sm:inline">Save Progress</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Progress bar */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress.overall}%` }}
                className="h-full bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full"
              />
            </div>
            <span className="text-sm font-semibold text-emerald-600">{progress.overall}%</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* Sidebar Navigation */}
          <nav className="w-64 flex-shrink-0 hidden lg:block">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200/60 p-4 sticky top-28">
              <div className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-left transition-all ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-md'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <span className="flex items-center gap-3">
                      {tab.icon}
                      <span className="font-medium">{tab.label}</span>
                    </span>
                    {tab.badge !== undefined && tab.badge > 0 && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        activeTab === tab.id
                          ? 'bg-white/20 text-white'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}>
                        {tab.badge}
                      </span>
                    )}
                  </button>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center gap-2 text-emerald-600 text-sm mb-3">
                  <Shield className="w-4 h-4" />
                  <span className="font-medium">Your data is secure</span>
                </div>
                <p className="text-xs text-gray-500">
                  All information is encrypted and transmitted securely to your CPA firm.
                </p>
              </div>
            </div>
          </nav>

          {/* Mobile tabs */}
          <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-2 z-30">
            <div className="flex justify-around">
              {tabs.slice(0, 5).map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
                    activeTab === tab.id
                      ? 'text-emerald-600'
                      : 'text-gray-500'
                  }`}
                >
                  {tab.icon}
                  <span className="text-xs">{tab.label.split(' ')[0]}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <main className="flex-1 pb-20 lg:pb-0">
            <AnimatePresence mode="wait">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <motion.div
                  key="overview"
                  {...fadeIn}
                  className="space-y-6"
                >
                  {/* Welcome Card */}
                  <div className="bg-gradient-to-r from-emerald-500 to-blue-600 rounded-2xl p-8 text-white shadow-xl">
                    <h2 className="text-2xl font-bold mb-2">
                      Welcome, {invitation.client_name}!
                    </h2>
                    <p className="text-emerald-100 mb-4">
                      {invitation.invited_by} from {invitation.firm_name} has invited you to provide
                      information for your {invitation.tax_year} R&D Tax Credit Study.
                    </p>
                    <div className="flex items-center gap-4">
                      <button
                        onClick={() => setActiveTab('data-input')}
                        className="flex items-center gap-2 px-6 py-3 bg-white text-emerald-600 rounded-xl font-semibold hover:bg-emerald-50 transition-colors"
                      >
                        Get Started
                        <ArrowRight className="w-5 h-5" />
                      </button>
                      {progress.overall > 0 && (
                        <button
                          onClick={() => setActiveTab('review')}
                          className="flex items-center gap-2 px-6 py-3 bg-white/20 text-white rounded-xl font-medium hover:bg-white/30 transition-colors"
                        >
                          Continue Where You Left Off
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-xl p-5 border border-gray-200/60 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Users className="w-5 h-5 text-blue-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-600">Employees</span>
                      </div>
                      <p className="text-3xl font-bold text-gray-900">{employees.length}</p>
                      <p className="text-sm text-gray-500 mt-1">{progress.employees.complete} complete</p>
                    </div>

                    <div className="bg-white rounded-xl p-5 border border-gray-200/60 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                          <FlaskConical className="w-5 h-5 text-emerald-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-600">Projects</span>
                      </div>
                      <p className="text-3xl font-bold text-gray-900">{projects.length}</p>
                      <p className="text-sm text-gray-500 mt-1">{progress.projects.complete} complete</p>
                    </div>

                    <div className="bg-white rounded-xl p-5 border border-gray-200/60 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                          <FileSpreadsheet className="w-5 h-5 text-purple-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-600">Documents</span>
                      </div>
                      <p className="text-3xl font-bold text-gray-900">{documents.length}</p>
                      <p className="text-sm text-gray-500 mt-1">files uploaded</p>
                    </div>

                    <div className="bg-white rounded-xl p-5 border border-gray-200/60 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                          <TrendingUp className="w-5 h-5 text-amber-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-600">Progress</span>
                      </div>
                      <p className="text-3xl font-bold text-gray-900">{progress.overall}%</p>
                      <p className="text-sm text-gray-500 mt-1">completed</p>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-white rounded-2xl p-6 border border-gray-200/60 shadow-sm">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">What you'll need to provide</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="flex items-start gap-4 p-4 bg-blue-50 rounded-xl">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Users className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">Employee Data</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Names, titles, wages, and time spent on R&D activities
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-4 p-4 bg-emerald-50 rounded-xl">
                        <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FlaskConical className="w-6 h-6 text-emerald-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">R&D Projects</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Project details and answers to the IRS 4-part test
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-4 p-4 bg-purple-50 rounded-xl">
                        <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileText className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">Documents</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Payroll reports, org charts, project documentation
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI Assistance Banner */}
                  <div className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
                        <Brain className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold mb-2">AI-Powered Assistance</h3>
                        <p className="text-violet-100 text-sm">
                          Our AI will help you write professional project descriptions and answer the IRS 4-part test questions.
                          Just provide the basics, and we'll help create detailed, IRS-compliant narratives.
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Data Input Method Selection */}
              {activeTab === 'data-input' && (
                <motion.div
                  key="data-input"
                  {...fadeIn}
                  className="space-y-6"
                >
                  <div className="bg-white rounded-2xl p-8 border border-gray-200/60 shadow-sm">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Choose How to Add Your Data</h2>
                    <p className="text-gray-600 mb-8">Select the method that works best for you. You can use multiple methods.</p>

                    <div className="grid md:grid-cols-3 gap-6">
                      {/* Manual Entry */}
                      <button
                        onClick={() => {
                          setInputMethod('manual');
                          setActiveTab('employees');
                        }}
                        className={`text-left p-6 rounded-2xl border-2 transition-all hover:shadow-lg ${
                          inputMethod === 'manual'
                            ? 'border-emerald-500 bg-emerald-50'
                            : 'border-gray-200 hover:border-emerald-300'
                        }`}
                      >
                        <div className="w-14 h-14 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
                          <Edit3 className="w-7 h-7 text-emerald-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Manual Entry</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Enter employee and project information directly using our guided forms.
                        </p>
                        <div className="flex items-center gap-2 text-emerald-600 font-medium">
                          <span>Start Entering</span>
                          <ArrowRight className="w-4 h-4" />
                        </div>
                      </button>

                      {/* Spreadsheet Upload */}
                      <button
                        onClick={() => {
                          setInputMethod('upload');
                          setShowInputMethodSelector(true);
                        }}
                        className={`text-left p-6 rounded-2xl border-2 transition-all hover:shadow-lg ${
                          inputMethod === 'upload'
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-300'
                        }`}
                      >
                        <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                          <Upload className="w-7 h-7 text-blue-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Spreadsheet</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Upload Excel or CSV files with your payroll, employee, or expense data.
                        </p>
                        <div className="flex items-center gap-2 text-blue-600 font-medium">
                          <span>Upload Files</span>
                          <ArrowRight className="w-4 h-4" />
                        </div>
                      </button>

                      {/* API Connection */}
                      <button
                        onClick={() => {
                          setInputMethod('api');
                          setShowInputMethodSelector(true);
                        }}
                        className={`text-left p-6 rounded-2xl border-2 transition-all hover:shadow-lg ${
                          inputMethod === 'api'
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-purple-300'
                        }`}
                      >
                        <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                          <Link className="w-7 h-7 text-purple-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Connect Payroll</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Connect your payroll system (ADP, Gusto, Paychex) to automatically import data.
                        </p>
                        <div className="flex items-center gap-2 text-purple-600 font-medium">
                          <span>Connect API</span>
                          <ArrowRight className="w-4 h-4" />
                        </div>
                      </button>
                    </div>
                  </div>

                  {/* Spreadsheet Upload Section */}
                  {inputMethod === 'upload' && showInputMethodSelector && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="bg-white rounded-2xl p-8 border border-gray-200/60 shadow-sm"
                    >
                      <h3 className="text-xl font-bold text-gray-900 mb-6">Upload Your Data</h3>

                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Payroll Upload */}
                        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
                          <FileSpreadsheet className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                          <h4 className="font-semibold text-gray-900 mb-2">Payroll / Employee Data</h4>
                          <p className="text-sm text-gray-600 mb-4">
                            Upload your payroll report or employee roster (Excel/CSV)
                          </p>
                          <label className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
                            <Upload className="w-4 h-4" />
                            Select File
                            <input
                              type="file"
                              accept=".xlsx,.xls,.csv"
                              className="hidden"
                              onChange={(e) => e.target.files && handleSpreadsheetUpload(e.target.files[0], 'employees')}
                            />
                          </label>
                        </div>

                        {/* Expenses Upload */}
                        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-emerald-400 transition-colors">
                          <DollarSign className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                          <h4 className="font-semibold text-gray-900 mb-2">R&D Expenses</h4>
                          <p className="text-sm text-gray-600 mb-4">
                            Upload supply purchases or contractor invoices (Excel/CSV)
                          </p>
                          <label className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg cursor-pointer hover:bg-emerald-700 transition-colors">
                            <Upload className="w-4 h-4" />
                            Select File
                            <input
                              type="file"
                              accept=".xlsx,.xls,.csv"
                              className="hidden"
                              onChange={(e) => e.target.files && handleSpreadsheetUpload(e.target.files[0], 'supplies')}
                            />
                          </label>
                        </div>
                      </div>

                      {/* Download Template */}
                      <div className="mt-6 p-4 bg-gray-50 rounded-xl">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Download className="w-5 h-5 text-gray-500" />
                            <div>
                              <p className="font-medium text-gray-900">Need a template?</p>
                              <p className="text-sm text-gray-600">Download our Excel template with the required columns</p>
                            </div>
                          </div>
                          <button className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium">
                            Download Template
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {/* API Connection Section */}
                  {inputMethod === 'api' && showInputMethodSelector && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="bg-white rounded-2xl p-8 border border-gray-200/60 shadow-sm"
                    >
                      <h3 className="text-xl font-bold text-gray-900 mb-2">Connect Your Payroll System</h3>
                      <p className="text-gray-600 mb-6">Securely connect your payroll provider to automatically import employee data.</p>

                      <div className="grid md:grid-cols-4 gap-4">
                        {[
                          { id: 'adp', name: 'ADP', logo: '🔵' },
                          { id: 'gusto', name: 'Gusto', logo: '🟠' },
                          { id: 'paychex', name: 'Paychex', logo: '🔴' },
                          { id: 'quickbooks', name: 'QuickBooks', logo: '🟢' },
                        ].map((provider) => (
                          <button
                            key={provider.id}
                            onClick={() => connectPayrollAPI(provider.id, {})}
                            className="flex flex-col items-center gap-3 p-6 border-2 border-gray-200 rounded-xl hover:border-purple-400 hover:bg-purple-50 transition-all"
                          >
                            <span className="text-4xl">{provider.logo}</span>
                            <span className="font-medium text-gray-900">{provider.name}</span>
                          </button>
                        ))}
                      </div>

                      {payrollConnection && (
                        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <CheckCircle className="w-5 h-5 text-green-600" />
                              <div>
                                <p className="font-medium text-green-800">
                                  Connected to {payrollConnection.provider}
                                </p>
                                {payrollConnection.employees_synced && (
                                  <p className="text-sm text-green-700">
                                    {payrollConnection.employees_synced} employees synced
                                  </p>
                                )}
                              </div>
                            </div>
                            <button
                              onClick={syncPayrollData}
                              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                            >
                              <RefreshCw className="w-4 h-4" />
                              Sync Now
                            </button>
                          </div>
                        </div>
                      )}

                      <div className="mt-6 p-4 bg-blue-50 rounded-xl">
                        <div className="flex items-start gap-3">
                          <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                          <div>
                            <p className="font-medium text-blue-900">Secure Connection</p>
                            <p className="text-sm text-blue-700">
                              We use bank-level encryption and never store your login credentials.
                              Data is transmitted directly from your payroll provider.
                            </p>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* Employees Tab */}
              {activeTab === 'employees' && (
                <motion.div
                  key="employees"
                  {...fadeIn}
                  className="space-y-6"
                >
                  <div className="bg-white rounded-2xl p-6 border border-gray-200/60 shadow-sm">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">Employee Information</h2>
                        <p className="text-gray-500 text-sm">Add employees who worked on R&D activities during {invitation.tax_year}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors">
                          <Upload className="w-4 h-4" />
                          Import Excel
                          <input
                            type="file"
                            accept=".xlsx,.xls,.csv"
                            className="hidden"
                            onChange={(e) => e.target.files && handleSpreadsheetUpload(e.target.files[0], 'employees')}
                          />
                        </label>
                        <button
                          onClick={addEmployee}
                          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                        >
                          <Plus className="w-4 h-4" />
                          Add Employee
                        </button>
                      </div>
                    </div>

                    {processingUpload && (
                      <div className="flex items-center justify-center gap-3 p-8 bg-blue-50 rounded-xl mb-6">
                        <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                        <span className="text-blue-700 font-medium">Processing your file...</span>
                      </div>
                    )}

                    {employees.length === 0 && !processingUpload ? (
                      <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                        <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No employees added yet</h3>
                        <p className="text-gray-500 mb-6">Add employees manually or import from a spreadsheet</p>
                        <div className="flex items-center justify-center gap-3">
                          <button
                            onClick={addEmployee}
                            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                          >
                            <Plus className="w-4 h-4" />
                            Add Employee
                          </button>
                          <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                            <Upload className="w-4 h-4" />
                            Import Excel
                            <input
                              type="file"
                              accept=".xlsx,.xls,.csv"
                              className="hidden"
                              onChange={(e) => e.target.files && handleSpreadsheetUpload(e.target.files[0], 'employees')}
                            />
                          </label>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {employees.map((employee, index) => (
                          <motion.div
                            key={employee.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-gray-50 rounded-xl p-5 border border-gray-200"
                          >
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                                  <span className="text-sm font-semibold text-emerald-700">{index + 1}</span>
                                </div>
                                <span className="font-medium text-gray-900">
                                  {employee.name || `Employee ${index + 1}`}
                                </span>
                              </div>
                              <button
                                onClick={() => removeEmployee(employee.id)}
                                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                              <div className="col-span-2 md:col-span-1">
                                <label className="block text-xs font-medium text-gray-600 mb-1">Full Name *</label>
                                <input
                                  type="text"
                                  value={employee.name}
                                  onChange={(e) => updateEmployee(employee.id, { name: e.target.value })}
                                  className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                  placeholder="John Smith"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Job Title</label>
                                <input
                                  type="text"
                                  value={employee.title}
                                  onChange={(e) => updateEmployee(employee.id, { title: e.target.value })}
                                  className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                  placeholder="Software Engineer"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Department</label>
                                <input
                                  type="text"
                                  value={employee.department}
                                  onChange={(e) => updateEmployee(employee.id, { department: e.target.value })}
                                  className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                  placeholder="Engineering"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Annual Wages ($) *</label>
                                <input
                                  type="number"
                                  value={employee.annual_wages || ''}
                                  onChange={(e) => updateEmployee(employee.id, { annual_wages: Number(e.target.value) })}
                                  className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                  placeholder="85000"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">% Time on R&D</label>
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  value={employee.qualified_time_percentage || ''}
                                  onChange={(e) => updateEmployee(employee.id, { qualified_time_percentage: Number(e.target.value) })}
                                  className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                  placeholder="50"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Time Source</label>
                                <select
                                  value={employee.time_source}
                                  onChange={(e) => updateEmployee(employee.id, { time_source: e.target.value as Employee['time_source'] })}
                                  className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                >
                                  <option value="estimate">Estimate</option>
                                  <option value="timesheet">Timesheet</option>
                                  <option value="survey">Survey</option>
                                  <option value="api">API Import</option>
                                </select>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('data-input')}
                      className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                      Back
                    </button>
                    <button
                      onClick={() => setActiveTab('projects')}
                      className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                    >
                      Continue to Projects
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Projects Tab - 4-Part Test */}
              {activeTab === 'projects' && (
                <motion.div
                  key="projects"
                  {...fadeIn}
                  className="space-y-6"
                >
                  <div className="bg-white rounded-2xl p-6 border border-gray-200/60 shadow-sm">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">R&D Projects</h2>
                        <p className="text-gray-500 text-sm">Describe your research and development activities</p>
                      </div>
                      <button
                        onClick={addProject}
                        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                        Add Project
                      </button>
                    </div>

                    {/* 4-Part Test Info Banner */}
                    <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <HelpCircle className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-1">IRS 4-Part Test</h4>
                          <p className="text-sm text-gray-600">
                            Each project must pass all four parts of the IRS test to qualify for the R&D Tax Credit.
                            Our AI will help you write clear, compliant descriptions.
                          </p>
                        </div>
                      </div>
                    </div>

                    {projects.length === 0 ? (
                      <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                        <FlaskConical className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No projects added yet</h3>
                        <p className="text-gray-500 mb-6">Add your R&D projects to qualify for the tax credit</p>
                        <button
                          onClick={addProject}
                          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors mx-auto"
                        >
                          <Plus className="w-4 h-4" />
                          Add First Project
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {projects.map((project, index) => (
                          <motion.div
                            key={project.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden"
                          >
                            {/* Project Header */}
                            <div
                              className="flex items-center justify-between p-5 cursor-pointer hover:bg-gray-100 transition-colors"
                              onClick={() => setExpandedProject(expandedProject === project.id ? null : project.id)}
                            >
                              <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                                  <FlaskConical className="w-5 h-5 text-emerald-600" />
                                </div>
                                <div>
                                  <h3 className="font-semibold text-gray-900">
                                    {project.name || `Project ${index + 1}`}
                                  </h3>
                                  <p className="text-sm text-gray-500">{project.business_component || 'No business component set'}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-3">
                                {project.ai_qualification_score && (
                                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                                    project.ai_qualification_score >= 70
                                      ? 'bg-green-100 text-green-700'
                                      : project.ai_qualification_score >= 50
                                      ? 'bg-yellow-100 text-yellow-700'
                                      : 'bg-red-100 text-red-700'
                                  }`}>
                                    {project.ai_qualification_score}% qualified
                                  </div>
                                )}
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    removeProject(project.id);
                                  }}
                                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                                {expandedProject === project.id ? (
                                  <ChevronUp className="w-5 h-5 text-gray-400" />
                                ) : (
                                  <ChevronDown className="w-5 h-5 text-gray-400" />
                                )}
                              </div>
                            </div>

                            {/* Expanded Project Form */}
                            <AnimatePresence>
                              {expandedProject === project.id && (
                                <motion.div
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  exit={{ opacity: 0, height: 0 }}
                                  className="border-t border-gray-200"
                                >
                                  <div className="p-6 space-y-6">
                                    {/* Basic Info */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
                                        <input
                                          type="text"
                                          value={project.name}
                                          onChange={(e) => updateProject(project.id, { name: e.target.value })}
                                          className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                          placeholder="e.g., Next-Gen Platform Development"
                                        />
                                      </div>
                                      <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Business Component</label>
                                        <input
                                          type="text"
                                          value={project.business_component}
                                          onChange={(e) => updateProject(project.id, { business_component: e.target.value })}
                                          className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                          placeholder="e.g., Mobile Application, Software Platform"
                                        />
                                      </div>
                                    </div>

                                    {/* Project Description with AI */}
                                    <div>
                                      <div className="flex items-center justify-between mb-1">
                                        <label className="text-sm font-medium text-gray-700">Project Description *</label>
                                        <button
                                          onClick={() => generateProjectDescription(project.id)}
                                          disabled={!project.name || generatingDescription === project.id}
                                          className="flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700 disabled:text-gray-400 font-medium"
                                        >
                                          {generatingDescription === project.id ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                          ) : (
                                            <Wand2 className="w-4 h-4" />
                                          )}
                                          AI Generate All
                                        </button>
                                      </div>
                                      <textarea
                                        value={project.description}
                                        onChange={(e) => updateProject(project.id, { description: e.target.value })}
                                        rows={3}
                                        className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        placeholder="Describe what this project does and its goals..."
                                      />
                                    </div>

                                    {/* 4-Part Test Section */}
                                    <div className="border-t border-gray-200 pt-6">
                                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                        <CheckSquare className="w-5 h-5 text-emerald-600" />
                                        IRS 4-Part Test Questionnaire
                                      </h4>

                                      <div className="space-y-6">
                                        {/* Part 1: Permitted Purpose */}
                                        <div className="bg-blue-50 rounded-xl p-5">
                                          <div className="flex items-start gap-3 mb-4">
                                            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                              <Target className="w-4 h-4 text-blue-600" />
                                            </div>
                                            <div>
                                              <h5 className="font-semibold text-gray-900">Part 1: Permitted Purpose</h5>
                                              <p className="text-sm text-gray-600">Was the project intended to develop new or improved functionality, performance, reliability, or quality?</p>
                                            </div>
                                          </div>

                                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                                            {[
                                              { key: 'new_functionality', label: 'New Functionality' },
                                              { key: 'improved_performance', label: 'Improved Performance' },
                                              { key: 'improved_reliability', label: 'Improved Reliability' },
                                              { key: 'improved_quality', label: 'Improved Quality' },
                                            ].map((item) => (
                                              <label key={item.key} className="flex items-center gap-2 p-3 bg-white rounded-lg cursor-pointer hover:bg-blue-100 transition-colors">
                                                <input
                                                  type="checkbox"
                                                  checked={project.four_part_test.permitted_purpose[item.key as keyof typeof project.four_part_test.permitted_purpose] as boolean}
                                                  onChange={(e) => updateProjectFourPartTest(project.id, 'permitted_purpose', { [item.key]: e.target.checked })}
                                                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                                />
                                                <span className="text-sm text-gray-700">{item.label}</span>
                                              </label>
                                            ))}
                                          </div>

                                          <textarea
                                            value={project.four_part_test.permitted_purpose.answer}
                                            onChange={(e) => updateProjectFourPartTest(project.id, 'permitted_purpose', { answer: e.target.value })}
                                            rows={3}
                                            className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                                            placeholder="Describe the new or improved functionality this project was designed to achieve..."
                                          />
                                        </div>

                                        {/* Part 2: Technological Nature */}
                                        <div className="bg-emerald-50 rounded-xl p-5">
                                          <div className="flex items-start gap-3 mb-4">
                                            <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                              <Microscope className="w-4 h-4 text-emerald-600" />
                                            </div>
                                            <div>
                                              <h5 className="font-semibold text-gray-900">Part 2: Technological in Nature</h5>
                                              <p className="text-sm text-gray-600">Did the project rely on hard sciences such as engineering, physics, biology, chemistry, or computer science?</p>
                                            </div>
                                          </div>

                                          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                                            {[
                                              { key: 'uses_engineering', label: 'Engineering' },
                                              { key: 'uses_physics', label: 'Physics' },
                                              { key: 'uses_biology', label: 'Biology' },
                                              { key: 'uses_chemistry', label: 'Chemistry' },
                                              { key: 'uses_computer_science', label: 'Computer Science' },
                                            ].map((item) => (
                                              <label key={item.key} className="flex items-center gap-2 p-3 bg-white rounded-lg cursor-pointer hover:bg-emerald-100 transition-colors">
                                                <input
                                                  type="checkbox"
                                                  checked={project.four_part_test.technological_nature[item.key as keyof typeof project.four_part_test.technological_nature] as boolean}
                                                  onChange={(e) => updateProjectFourPartTest(project.id, 'technological_nature', { [item.key]: e.target.checked })}
                                                  className="w-4 h-4 text-emerald-600 rounded focus:ring-emerald-500"
                                                />
                                                <span className="text-sm text-gray-700">{item.label}</span>
                                              </label>
                                            ))}
                                          </div>

                                          <textarea
                                            value={project.four_part_test.technological_nature.answer}
                                            onChange={(e) => updateProjectFourPartTest(project.id, 'technological_nature', { answer: e.target.value })}
                                            rows={3}
                                            className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                            placeholder="Describe the scientific or technological principles applied in this project..."
                                          />
                                        </div>

                                        {/* Part 3: Elimination of Uncertainty */}
                                        <div className="bg-amber-50 rounded-xl p-5">
                                          <div className="flex items-start gap-3 mb-4">
                                            <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                              <AlertCircle className="w-4 h-4 text-amber-600" />
                                            </div>
                                            <div>
                                              <h5 className="font-semibold text-gray-900">Part 3: Elimination of Uncertainty</h5>
                                              <p className="text-sm text-gray-600">Did the project involve uncertainty about capability, method, or design that could not be resolved through existing knowledge?</p>
                                            </div>
                                          </div>

                                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                                            {[
                                              { key: 'capability_uncertain', label: 'Capability Uncertainty', desc: 'Could it be done at all?' },
                                              { key: 'method_uncertain', label: 'Method Uncertainty', desc: 'What approach would work?' },
                                              { key: 'design_uncertain', label: 'Design Uncertainty', desc: 'What design was optimal?' },
                                            ].map((item) => (
                                              <label key={item.key} className="flex items-start gap-3 p-3 bg-white rounded-lg cursor-pointer hover:bg-amber-100 transition-colors">
                                                <input
                                                  type="checkbox"
                                                  checked={project.four_part_test.elimination_uncertainty[item.key as keyof typeof project.four_part_test.elimination_uncertainty] as boolean}
                                                  onChange={(e) => updateProjectFourPartTest(project.id, 'elimination_uncertainty', { [item.key]: e.target.checked })}
                                                  className="w-4 h-4 text-amber-600 rounded focus:ring-amber-500 mt-0.5"
                                                />
                                                <div>
                                                  <span className="text-sm font-medium text-gray-700">{item.label}</span>
                                                  <p className="text-xs text-gray-500">{item.desc}</p>
                                                </div>
                                              </label>
                                            ))}
                                          </div>

                                          <textarea
                                            value={project.four_part_test.elimination_uncertainty.answer}
                                            onChange={(e) => updateProjectFourPartTest(project.id, 'elimination_uncertainty', { answer: e.target.value })}
                                            rows={3}
                                            className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all"
                                            placeholder="Describe the technical uncertainties that existed at the start of this project..."
                                          />
                                        </div>

                                        {/* Part 4: Process of Experimentation */}
                                        <div className="bg-purple-50 rounded-xl p-5">
                                          <div className="flex items-start gap-3 mb-4">
                                            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                              <Beaker className="w-4 h-4 text-purple-600" />
                                            </div>
                                            <div>
                                              <h5 className="font-semibold text-gray-900">Part 4: Process of Experimentation</h5>
                                              <p className="text-sm text-gray-600">Did the project involve a systematic process of experimentation to evaluate alternatives and resolve uncertainties?</p>
                                            </div>
                                          </div>

                                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                                            {[
                                              { key: 'systematic_approach', label: 'Systematic Approach', desc: 'Used structured methodology' },
                                              { key: 'tested_alternatives', label: 'Tested Alternatives', desc: 'Evaluated multiple solutions' },
                                              { key: 'documented_results', label: 'Documented Results', desc: 'Recorded findings' },
                                            ].map((item) => (
                                              <label key={item.key} className="flex items-start gap-3 p-3 bg-white rounded-lg cursor-pointer hover:bg-purple-100 transition-colors">
                                                <input
                                                  type="checkbox"
                                                  checked={project.four_part_test.process_experimentation[item.key as keyof typeof project.four_part_test.process_experimentation] as boolean}
                                                  onChange={(e) => updateProjectFourPartTest(project.id, 'process_experimentation', { [item.key]: e.target.checked })}
                                                  className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500 mt-0.5"
                                                />
                                                <div>
                                                  <span className="text-sm font-medium text-gray-700">{item.label}</span>
                                                  <p className="text-xs text-gray-500">{item.desc}</p>
                                                </div>
                                              </label>
                                            ))}
                                          </div>

                                          <textarea
                                            value={project.four_part_test.process_experimentation.answer}
                                            onChange={(e) => updateProjectFourPartTest(project.id, 'process_experimentation', { answer: e.target.value })}
                                            rows={3}
                                            className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
                                            placeholder="Describe the experiments, tests, or evaluations conducted during this project..."
                                          />
                                        </div>
                                      </div>
                                    </div>

                                    {/* Project Dates */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                                      <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                                        <input
                                          type="date"
                                          value={project.start_date}
                                          onChange={(e) => updateProject(project.id, { start_date: e.target.value })}
                                          className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                                        />
                                      </div>
                                      <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                                        <input
                                          type="date"
                                          value={project.end_date || ''}
                                          onChange={(e) => updateProject(project.id, { end_date: e.target.value || null })}
                                          disabled={project.is_ongoing}
                                          className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all disabled:bg-gray-100"
                                        />
                                      </div>
                                      <div className="flex items-end">
                                        <label className="flex items-center gap-2 p-3 bg-white rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors w-full">
                                          <input
                                            type="checkbox"
                                            checked={project.is_ongoing}
                                            onChange={(e) => updateProject(project.id, { is_ongoing: e.target.checked })}
                                            className="w-4 h-4 text-emerald-600 rounded focus:ring-emerald-500"
                                          />
                                          <span className="text-sm text-gray-700">Project is ongoing</span>
                                        </label>
                                      </div>
                                    </div>
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('employees')}
                      className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                      Back to Employees
                    </button>
                    <button
                      onClick={() => setActiveTab('documents')}
                      className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                    >
                      Continue to Documents
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Documents Tab */}
              {activeTab === 'documents' && (
                <motion.div
                  key="documents"
                  {...fadeIn}
                  className="space-y-6"
                >
                  <div className="bg-white rounded-2xl p-6 border border-gray-200/60 shadow-sm">
                    <div className="mb-6">
                      <h2 className="text-xl font-bold text-gray-900">Supporting Documents</h2>
                      <p className="text-gray-500 text-sm">Upload documents to support your R&D credit claim</p>
                    </div>

                    {/* Document Categories */}
                    <div className="grid md:grid-cols-2 gap-4 mb-6">
                      {[
                        { category: 'payroll' as const, label: 'Payroll Reports', icon: <DollarSign className="w-6 h-6" />, color: 'blue' },
                        { category: 'timesheet' as const, label: 'Timesheets', icon: <Clock className="w-6 h-6" />, color: 'emerald' },
                        { category: 'project_docs' as const, label: 'Project Documentation', icon: <FileText className="w-6 h-6" />, color: 'purple' },
                        { category: 'contracts' as const, label: 'Contracts & Invoices', icon: <Briefcase className="w-6 h-6" />, color: 'amber' },
                      ].map((item) => (
                        <label
                          key={item.category}
                          className={`flex items-center gap-4 p-5 border-2 border-dashed rounded-xl cursor-pointer transition-all hover:border-${item.color}-400 hover:bg-${item.color}-50`}
                        >
                          <div className={`w-12 h-12 bg-${item.color}-100 rounded-lg flex items-center justify-center text-${item.color}-600`}>
                            {item.icon}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900">{item.label}</h4>
                            <p className="text-sm text-gray-500">Click or drag files here</p>
                          </div>
                          <input
                            type="file"
                            multiple
                            accept=".pdf,.xlsx,.xls,.csv,.doc,.docx,.png,.jpg,.jpeg"
                            className="hidden"
                            onChange={(e) => handleDocumentUpload(e.target.files, item.category)}
                          />
                        </label>
                      ))}
                    </div>

                    {/* Uploaded Documents List */}
                    {documents.length > 0 && (
                      <div className="mt-8">
                        <h3 className="text-sm font-semibold text-gray-700 mb-4">Uploaded Files ({documents.length})</h3>
                        <div className="space-y-2">
                          {documents.map((doc) => (
                            <div
                              key={doc.id}
                              className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-xl border border-gray-200"
                            >
                              <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                                  doc.status === 'processed' ? 'bg-green-100' :
                                  doc.status === 'error' ? 'bg-red-100' :
                                  'bg-blue-100'
                                }`}>
                                  {doc.status === 'processed' ? (
                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                  ) : doc.status === 'error' ? (
                                    <AlertTriangle className="w-5 h-5 text-red-600" />
                                  ) : (
                                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                                  )}
                                </div>
                                <div>
                                  <p className="font-medium text-gray-900">{doc.name}</p>
                                  <p className="text-xs text-gray-500">
                                    {(doc.size / 1024).toFixed(1)} KB • {doc.category}
                                  </p>
                                </div>
                              </div>
                              <button
                                onClick={() => setDocuments(prev => prev.filter(d => d.id !== doc.id))}
                                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Additional Notes */}
                    <div className="mt-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Additional Notes</label>
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        rows={4}
                        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                        placeholder="Any additional information you'd like to share with your CPA firm..."
                      />
                    </div>
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('projects')}
                      className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                      Back to Projects
                    </button>
                    <button
                      onClick={() => setActiveTab('review')}
                      className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                    >
                      Review & Submit
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Review Tab */}
              {activeTab === 'review' && (
                <motion.div
                  key="review"
                  {...fadeIn}
                  className="space-y-6"
                >
                  <div className="bg-white rounded-2xl p-6 border border-gray-200/60 shadow-sm">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Review Your Submission</h2>

                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                        <Users className="w-8 h-8 text-blue-600 mb-3" />
                        <p className="text-3xl font-bold text-gray-900">{employees.length}</p>
                        <p className="text-sm text-gray-600">Employees</p>
                        <p className="text-xs text-blue-600 mt-1">{progress.employees.complete} complete</p>
                      </div>
                      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-5">
                        <FlaskConical className="w-8 h-8 text-emerald-600 mb-3" />
                        <p className="text-3xl font-bold text-gray-900">{projects.length}</p>
                        <p className="text-sm text-gray-600">Projects</p>
                        <p className="text-xs text-emerald-600 mt-1">{progress.projects.complete} complete</p>
                      </div>
                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5">
                        <FileSpreadsheet className="w-8 h-8 text-purple-600 mb-3" />
                        <p className="text-3xl font-bold text-gray-900">{documents.length}</p>
                        <p className="text-sm text-gray-600">Documents</p>
                        <p className="text-xs text-purple-600 mt-1">uploaded</p>
                      </div>
                      <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-5">
                        <TrendingUp className="w-8 h-8 text-amber-600 mb-3" />
                        <p className="text-3xl font-bold text-gray-900">{progress.overall}%</p>
                        <p className="text-sm text-gray-600">Complete</p>
                        <p className="text-xs text-amber-600 mt-1">ready to submit</p>
                      </div>
                    </div>

                    {/* Validation Warnings */}
                    {(employees.length === 0 || projects.length === 0) && (
                      <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-6">
                        <div className="flex items-start gap-3">
                          <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0" />
                          <div>
                            <h4 className="font-semibold text-amber-900 mb-2">Missing Required Information</h4>
                            <ul className="space-y-1 text-sm text-amber-800">
                              {employees.length === 0 && (
                                <li className="flex items-center gap-2">
                                  <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                                  No employees added - please add at least one employee
                                </li>
                              )}
                              {projects.length === 0 && (
                                <li className="flex items-center gap-2">
                                  <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                                  No projects added - please add at least one R&D project
                                </li>
                              )}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Submission Info */}
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
                      <div className="flex items-start gap-3">
                        <Shield className="w-6 h-6 text-blue-600 flex-shrink-0" />
                        <div>
                          <h4 className="font-semibold text-blue-900 mb-1">Secure Submission</h4>
                          <p className="text-sm text-blue-800">
                            By submitting, your data will be encrypted and sent securely to <strong>{invitation.firm_name}</strong>.
                            They will review your information and contact you if they need any clarification.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('documents')}
                      className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                      Back
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={submitting || employees.length === 0 || projects.length === 0}
                      className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-emerald-500 to-blue-600 text-white rounded-xl font-semibold hover:from-emerald-600 hover:to-blue-700 transition-all disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed shadow-lg"
                    >
                      {submitting ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Submit to {invitation.firm_name}
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </main>
        </div>
      </div>
    </div>
  );
}

export default RDClientPortal;
