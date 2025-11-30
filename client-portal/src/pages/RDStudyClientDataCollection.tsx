/**
 * R&D Study Client Data Collection Page
 *
 * This page is for CLIENTS ONLY to provide data for their R&D Tax Credit Study.
 * Clients can:
 * - Upload payroll and employee data (Excel, CSV)
 * - Describe their R&D projects (with AI assistance)
 * - Enter time allocation estimates
 * - Upload supporting documents
 *
 * Clients CANNOT:
 * - See calculations or credit amounts
 * - View final reports
 * - Access study settings or methodology
 */

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical,
  Upload,
  Users,
  Building2,
  FileSpreadsheet,
  CheckCircle,
  AlertTriangle,
  Clock,
  Send,
  Plus,
  Trash2,
  Wand2,
  Loader2,
  Shield,
  Calendar,
  File,
  X,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Brain,
  Save,
  Info,
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

interface InvitationData {
  client_email: string;
  client_name: string;
  study_name: string;
  tax_year: number;
  firm_name: string;
  invited_by: string;
  deadline: string | null;
  expires_at: string;
}

interface Employee {
  id: string;
  name: string;
  title: string;
  department: string;
  annual_wages: number;
  qualified_time_percentage: number;
  time_source: 'estimate' | 'timesheet' | 'survey';
}

interface Project {
  id: string;
  name: string;
  description: string;
  business_component: string;
  technical_uncertainty: string;
  experimentation_process: string;
  start_date: string;
  end_date: string | null;
  is_ongoing: boolean;
  employees_involved: string[];
}

interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  size: number;
  uploaded_at: string;
}

type TabType = 'welcome' | 'employees' | 'projects' | 'documents' | 'review';

export function RDStudyClientDataCollection() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  // State
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invitation, setInvitation] = useState<InvitationData | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('welcome');
  const [submitted, setSubmitted] = useState(false);

  // Data states
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [notes, setNotes] = useState('');

  // AI generation states
  const [generatingDescription, setGeneratingDescription] = useState<string | null>(null);

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

  // Add employee
  const addEmployee = useCallback(() => {
    const newEmployee: Employee = {
      id: `emp-${Date.now()}`,
      name: '',
      title: '',
      department: '',
      annual_wages: 0,
      qualified_time_percentage: 0,
      time_source: 'estimate',
    };
    setEmployees(prev => [...prev, newEmployee]);
  }, []);

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
      technical_uncertainty: '',
      experimentation_process: '',
      start_date: '',
      end_date: null,
      is_ongoing: true,
      employees_involved: [],
    };
    setProjects(prev => [...prev, newProject]);
  }, []);

  // Update project
  const updateProject = useCallback((id: string, updates: Partial<Project>) => {
    setProjects(prev =>
      prev.map(proj => (proj.id === id ? { ...proj, ...updates } : proj))
    );
  }, []);

  // Remove project
  const removeProject = useCallback((id: string) => {
    setProjects(prev => prev.filter(proj => proj.id !== id));
  }, []);

  // Generate AI description for project
  const generateProjectDescription = useCallback(async (projectId: string) => {
    const project = projects.find(p => p.id === projectId);
    if (!project || !project.name) return;

    setGeneratingDescription(projectId);
    try {
      const response = await axios.post(`${API_BASE_URL}/rd-study/ai/generate-description`, {
        project_name: project.name,
        business_component: project.business_component,
        context: project.description,
      });

      updateProject(projectId, {
        description: response.data.description,
        technical_uncertainty: response.data.technical_uncertainty || project.technical_uncertainty,
        experimentation_process: response.data.experimentation_process || project.experimentation_process,
      });
    } catch (err) {
      console.error('Failed to generate description:', err);
    } finally {
      setGeneratingDescription(null);
    }
  }, [projects, updateProject]);

  // Handle file upload
  const handleFileUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    for (const file of Array.from(files)) {
      const newDoc: UploadedDocument = {
        id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        type: file.type,
        size: file.size,
        uploaded_at: new Date().toISOString(),
      };
      setDocuments(prev => [...prev, newDoc]);
    }
  }, []);

  // Handle Excel import
  const handleExcelImport = useCallback(async (file: File) => {
    // For now, just add as document
    handleFileUpload([file] as unknown as FileList);
  }, [handleFileUpload]);

  // Submit data
  const handleSubmit = useCallback(async () => {
    if (!token) return;

    setSubmitting(true);
    try {
      await axios.post(`${API_BASE_URL}/rd-study/client-data-submission`, {
        token,
        employees,
        projects,
        documents: documents.map(d => ({ name: d.name, type: d.type })),
        submission_notes: notes,
      });
      setSubmitted(true);
    } catch (err) {
      console.error('Submission failed:', err);
      setError('Failed to submit data. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }, [token, employees, projects, documents, notes]);

  // Render loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-green-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Validating your invitation...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error || !invitation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Error</h1>
          <p className="text-gray-600 mb-6">{error || 'Unable to load invitation.'}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Return Home
          </button>
        </div>
      </div>
    );
  }

  // Render success state
  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center"
        >
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Submission Complete!</h1>
          <p className="text-gray-600 mb-4">
            Thank you for providing your R&D study information. {invitation.firm_name} will
            review your data and contact you if they need any additional information.
          </p>
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-500">Study: {invitation.study_name}</p>
            <p className="text-sm text-gray-500">Tax Year: {invitation.tax_year}</p>
          </div>
          <p className="text-sm text-gray-500">You may close this page.</p>
        </motion.div>
      </div>
    );
  }

  // Tab navigation
  const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'welcome', label: 'Welcome', icon: <Info className="w-4 h-4" /> },
    { id: 'employees', label: 'Employees', icon: <Users className="w-4 h-4" /> },
    { id: 'projects', label: 'Projects', icon: <FlaskConical className="w-4 h-4" /> },
    { id: 'documents', label: 'Documents', icon: <FileSpreadsheet className="w-4 h-4" /> },
    { id: 'review', label: 'Review & Submit', icon: <Send className="w-4 h-4" /> },
  ];

  const progress = {
    employees: employees.filter(e => e.name && e.annual_wages > 0).length,
    projects: projects.filter(p => p.name && p.description).length,
    documents: documents.length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                <FlaskConical className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">R&D Tax Credit Study</h1>
                <p className="text-sm text-gray-500">Data Collection for {invitation.firm_name}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{invitation.study_name}</p>
                <p className="text-xs text-gray-500">Tax Year {invitation.tax_year}</p>
              </div>
              {invitation.deadline && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-50 border border-amber-200 rounded-lg">
                  <Clock className="w-4 h-4 text-amber-600" />
                  <span className="text-sm font-medium text-amber-700">Due: {invitation.deadline}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Sidebar Navigation */}
          <nav className="w-64 flex-shrink-0">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sticky top-24">
              <div className="space-y-1">
                {tabs.map((tab, index) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
                      activeTab === tab.id
                        ? 'bg-green-50 text-green-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <span className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium ${
                      activeTab === tab.id ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'
                    }`}>
                      {index + 1}
                    </span>
                    <span className="flex-1">{tab.label}</span>
                    {tab.id === 'employees' && progress.employees > 0 && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                        {progress.employees}
                      </span>
                    )}
                    {tab.id === 'projects' && progress.projects > 0 && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                        {progress.projects}
                      </span>
                    )}
                    {tab.id === 'documents' && progress.documents > 0 && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                        {progress.documents}
                      </span>
                    )}
                  </button>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <Shield className="w-4 h-4" />
                  <span>Your data is secure</span>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1">
            <AnimatePresence mode="wait">
              {/* Welcome Tab */}
              {activeTab === 'welcome' && (
                <motion.div
                  key="welcome"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 p-8"
                >
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">
                    Welcome, {invitation.client_name}!
                  </h2>
                  <p className="text-gray-600 mb-6">
                    {invitation.invited_by} from {invitation.firm_name} has invited you to provide
                    information for your {invitation.tax_year} R&D Tax Credit Study.
                  </p>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-blue-900 mb-2">What you'll need to provide:</h3>
                    <ul className="space-y-2 text-blue-800">
                      <li className="flex items-start gap-2">
                        <Users className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        <span><strong>Employee Information:</strong> Names, titles, wages, and time spent on R&D</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <FlaskConical className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        <span><strong>Project Descriptions:</strong> Details about your R&D activities and technical challenges</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <FileSpreadsheet className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        <span><strong>Supporting Documents:</strong> Payroll reports, org charts, project documentation</span>
                      </li>
                    </ul>
                  </div>

                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-green-900">AI-Powered Assistance</h3>
                    </div>
                    <p className="text-green-800 text-sm">
                      Our AI will help you write professional project descriptions based on your input.
                      Just provide the basics, and we'll help you create detailed, IRS-compliant narratives.
                    </p>
                  </div>

                  <button
                    onClick={() => setActiveTab('employees')}
                    className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Get Started
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </motion.div>
              )}

              {/* Employees Tab */}
              {activeTab === 'employees' && (
                <motion.div
                  key="employees"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">Employee Information</h2>
                        <p className="text-gray-500 text-sm">Add employees who worked on R&D activities</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors">
                          <Upload className="w-4 h-4" />
                          Import Excel
                          <input
                            type="file"
                            accept=".xlsx,.xls,.csv"
                            className="hidden"
                            onChange={(e) => e.target.files && handleExcelImport(e.target.files[0])}
                          />
                        </label>
                        <button
                          onClick={addEmployee}
                          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Plus className="w-4 h-4" />
                          Add Employee
                        </button>
                      </div>
                    </div>

                    {employees.length === 0 ? (
                      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                        <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600 mb-2">No employees added yet</p>
                        <p className="text-gray-500 text-sm mb-4">Add employees manually or import from Excel</p>
                        <button
                          onClick={addEmployee}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          Add First Employee
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {employees.map((employee, index) => (
                          <div
                            key={employee.id}
                            className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                          >
                            <div className="flex items-center justify-between mb-3">
                              <span className="text-sm font-medium text-gray-500">Employee {index + 1}</span>
                              <button
                                onClick={() => removeEmployee(employee.id)}
                                className="p-1 text-red-500 hover:bg-red-50 rounded"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Name *</label>
                                <input
                                  type="text"
                                  value={employee.name}
                                  onChange={(e) => updateEmployee(employee.id, { name: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="John Smith"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Title</label>
                                <input
                                  type="text"
                                  value={employee.title}
                                  onChange={(e) => updateEmployee(employee.id, { title: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="Software Engineer"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Department</label>
                                <input
                                  type="text"
                                  value={employee.department}
                                  onChange={(e) => updateEmployee(employee.id, { department: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="Engineering"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Annual Wages ($) *</label>
                                <input
                                  type="number"
                                  value={employee.annual_wages || ''}
                                  onChange={(e) => updateEmployee(employee.id, { annual_wages: Number(e.target.value) })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="75000"
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
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="50"
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">Time Source</label>
                                <select
                                  value={employee.time_source}
                                  onChange={(e) => updateEmployee(employee.id, { time_source: e.target.value as Employee['time_source'] })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                >
                                  <option value="estimate">Estimate</option>
                                  <option value="timesheet">Timesheet</option>
                                  <option value="survey">Survey</option>
                                </select>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('welcome')}
                      className="px-4 py-2 text-gray-600 hover:text-gray-900"
                    >
                      Back
                    </button>
                    <button
                      onClick={() => setActiveTab('projects')}
                      className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Continue to Projects
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Projects Tab */}
              {activeTab === 'projects' && (
                <motion.div
                  key="projects"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">R&D Projects</h2>
                        <p className="text-gray-500 text-sm">Describe your research and development activities</p>
                      </div>
                      <button
                        onClick={addProject}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                        Add Project
                      </button>
                    </div>

                    {projects.length === 0 ? (
                      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                        <FlaskConical className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600 mb-2">No projects added yet</p>
                        <p className="text-gray-500 text-sm mb-4">Add your R&D projects to qualify for the tax credit</p>
                        <button
                          onClick={addProject}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          Add First Project
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {projects.map((project, index) => (
                          <div
                            key={project.id}
                            className="bg-gray-50 rounded-lg p-6 border border-gray-200"
                          >
                            <div className="flex items-center justify-between mb-4">
                              <span className="text-lg font-semibold text-gray-900">Project {index + 1}</span>
                              <button
                                onClick={() => removeProject(project.id)}
                                className="p-1 text-red-500 hover:bg-red-50 rounded"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
                                <input
                                  type="text"
                                  value={project.name}
                                  onChange={(e) => updateProject(project.id, { name: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="e.g., Next-Gen Platform Development"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Business Component</label>
                                <input
                                  type="text"
                                  value={project.business_component}
                                  onChange={(e) => updateProject(project.id, { business_component: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                  placeholder="e.g., Mobile Application"
                                />
                              </div>
                            </div>

                            <div className="mb-4">
                              <div className="flex items-center justify-between mb-1">
                                <label className="text-sm font-medium text-gray-700">Project Description *</label>
                                <button
                                  onClick={() => generateProjectDescription(project.id)}
                                  disabled={!project.name || generatingDescription === project.id}
                                  className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                                >
                                  {generatingDescription === project.id ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                  ) : (
                                    <Wand2 className="w-4 h-4" />
                                  )}
                                  AI Generate
                                </button>
                              </div>
                              <textarea
                                value={project.description}
                                onChange={(e) => updateProject(project.id, { description: e.target.value })}
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                placeholder="Describe the project's goals and what you were trying to accomplish..."
                              />
                            </div>

                            <div className="mb-4">
                              <label className="block text-sm font-medium text-gray-700 mb-1">Technical Uncertainty</label>
                              <textarea
                                value={project.technical_uncertainty}
                                onChange={(e) => updateProject(project.id, { technical_uncertainty: e.target.value })}
                                rows={2}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                placeholder="What technical challenges did you face? What was uncertain at the start?"
                              />
                            </div>

                            <div className="mb-4">
                              <label className="block text-sm font-medium text-gray-700 mb-1">Experimentation Process</label>
                              <textarea
                                value={project.experimentation_process}
                                onChange={(e) => updateProject(project.id, { experimentation_process: e.target.value })}
                                rows={2}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                placeholder="How did you evaluate alternatives? What experiments or tests did you run?"
                              />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                                <input
                                  type="date"
                                  value={project.start_date}
                                  onChange={(e) => updateProject(project.id, { start_date: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                                <input
                                  type="date"
                                  value={project.end_date || ''}
                                  onChange={(e) => updateProject(project.id, { end_date: e.target.value || null })}
                                  disabled={project.is_ongoing}
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100"
                                />
                              </div>
                              <div className="flex items-end">
                                <label className="flex items-center gap-2 cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={project.is_ongoing}
                                    onChange={(e) => updateProject(project.id, { is_ongoing: e.target.checked })}
                                    className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                                  />
                                  <span className="text-sm text-gray-700">Ongoing project</span>
                                </label>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('employees')}
                      className="px-4 py-2 text-gray-600 hover:text-gray-900"
                    >
                      Back
                    </button>
                    <button
                      onClick={() => setActiveTab('documents')}
                      className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
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
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="mb-4">
                      <h2 className="text-xl font-bold text-gray-900">Supporting Documents</h2>
                      <p className="text-gray-500 text-sm">Upload any relevant documents to support your R&D study</p>
                    </div>

                    <div
                      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-400 transition-colors cursor-pointer"
                      onClick={() => document.getElementById('file-upload')?.click()}
                    >
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600 mb-2">Drag and drop files here, or click to browse</p>
                      <p className="text-gray-400 text-sm">Supports: PDF, Excel, Word, Images (max 25MB each)</p>
                      <input
                        id="file-upload"
                        type="file"
                        multiple
                        accept=".pdf,.xlsx,.xls,.csv,.doc,.docx,.png,.jpg,.jpeg"
                        className="hidden"
                        onChange={(e) => handleFileUpload(e.target.files)}
                      />
                    </div>

                    {documents.length > 0 && (
                      <div className="mt-6">
                        <h3 className="text-sm font-medium text-gray-700 mb-3">Uploaded Files</h3>
                        <div className="space-y-2">
                          {documents.map((doc) => (
                            <div
                              key={doc.id}
                              className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-lg"
                            >
                              <div className="flex items-center gap-3">
                                <File className="w-5 h-5 text-gray-400" />
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                                  <p className="text-xs text-gray-500">
                                    {(doc.size / 1024).toFixed(1)} KB
                                  </p>
                                </div>
                              </div>
                              <button
                                onClick={() => setDocuments(prev => prev.filter(d => d.id !== doc.id))}
                                className="p-1 text-gray-400 hover:text-red-500"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="mt-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Additional Notes</label>
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        placeholder="Any additional information you'd like to share with your CPA..."
                      />
                    </div>
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('projects')}
                      className="px-4 py-2 text-gray-600 hover:text-gray-900"
                    >
                      Back
                    </button>
                    <button
                      onClick={() => setActiveTab('review')}
                      className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
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
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Review Your Submission</h2>

                    <div className="space-y-6">
                      {/* Summary Cards */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Users className="w-5 h-5 text-green-600" />
                            <span className="font-medium text-gray-900">Employees</span>
                          </div>
                          <p className="text-2xl font-bold text-gray-900">{employees.length}</p>
                          <p className="text-sm text-gray-500">
                            {employees.filter(e => e.name && e.annual_wages > 0).length} complete
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <FlaskConical className="w-5 h-5 text-green-600" />
                            <span className="font-medium text-gray-900">Projects</span>
                          </div>
                          <p className="text-2xl font-bold text-gray-900">{projects.length}</p>
                          <p className="text-sm text-gray-500">
                            {projects.filter(p => p.name && p.description).length} complete
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <FileSpreadsheet className="w-5 h-5 text-green-600" />
                            <span className="font-medium text-gray-900">Documents</span>
                          </div>
                          <p className="text-2xl font-bold text-gray-900">{documents.length}</p>
                          <p className="text-sm text-gray-500">files uploaded</p>
                        </div>
                      </div>

                      {/* Warnings */}
                      {(employees.length === 0 || projects.length === 0) && (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-amber-600" />
                            <span className="font-medium text-amber-900">Missing Information</span>
                          </div>
                          <ul className="text-sm text-amber-800 space-y-1">
                            {employees.length === 0 && (
                              <li>No employees added - please add at least one employee</li>
                            )}
                            {projects.length === 0 && (
                              <li>No projects added - please add at least one R&D project</li>
                            )}
                          </ul>
                        </div>
                      )}

                      {/* Submission Info */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-sm text-blue-800">
                          By submitting, your data will be sent securely to <strong>{invitation.firm_name}</strong> for review.
                          They will contact you if they need any additional information.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveTab('documents')}
                      className="px-4 py-2 text-gray-600 hover:text-gray-900"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={submitting || employees.length === 0 || projects.length === 0}
                      className="flex items-center gap-2 px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      {submitting ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Submit Data
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

export default RDStudyClientDataCollection;
