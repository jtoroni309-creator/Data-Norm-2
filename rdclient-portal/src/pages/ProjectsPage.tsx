/**
 * Projects Page
 * R&D Projects management with AI-assisted descriptions
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FolderKanban,
  Plus,
  Edit3,
  Trash2,
  Brain,
  Sparkles,
  ChevronDown,
  ChevronUp,
  CheckCircle,
  AlertCircle,
  Clock,
  Save,
  Loader2,
  X,
  Info,
  Target,
  Beaker,
  Microscope,
  Lightbulb,
} from 'lucide-react';
import studyService from '../services/study.service';
import toast from 'react-hot-toast';
import type { RDProject, FourPartTest } from '../types';

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

export default function ProjectsPage() {
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<RDProject[]>([]);
  const [expandedProject, setExpandedProject] = useState<string | null>(null);
  const [editingProject, setEditingProject] = useState<RDProject | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState<string | null>(null);

  // New project form state
  const [newProject, setNewProject] = useState<Partial<RDProject>>({
    name: '',
    description: '',
    business_component: '',
    department: '',
    start_date: '',
    is_ongoing: true,
    four_part_test: { ...defaultFourPartTest },
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await studyService.getProjects();
      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleAddProject = async () => {
    if (!newProject.name) {
      toast.error('Project name is required');
      return;
    }

    setSaving(true);
    try {
      const created = await studyService.createProject(newProject);
      setProjects([...projects, created]);
      setShowAddModal(false);
      setNewProject({
        name: '',
        description: '',
        business_component: '',
        department: '',
        start_date: '',
        is_ongoing: true,
        four_part_test: { ...defaultFourPartTest },
      });
      toast.success('Project added');
      setExpandedProject(created.id);
    } catch {
      toast.error('Failed to add project');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateProject = async (project: RDProject) => {
    setSaving(true);
    try {
      const updated = await studyService.updateProject(project.id, project);
      setProjects(projects.map((p) => (p.id === project.id ? updated : p)));
      toast.success('Project saved');
    } catch {
      toast.error('Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      await studyService.deleteProject(projectId);
      setProjects(projects.filter((p) => p.id !== projectId));
      toast.success('Project deleted');
    } catch {
      toast.error('Failed to delete project');
    }
  };

  const handleGenerateAI = async (projectId: string) => {
    const project = projects.find((p) => p.id === projectId);
    if (!project?.name) {
      toast.error('Please enter a project name first');
      return;
    }

    setGenerating(projectId);
    try {
      const result = await studyService.generateProjectDescription(projectId);
      const updatedProject = {
        ...project,
        description: result.description,
        four_part_test: {
          ...project.four_part_test,
          ...result.four_part_test_suggestions,
        },
      };
      setProjects(projects.map((p) => (p.id === projectId ? { ...p, ...updatedProject } : p)));
      toast.success('AI suggestions added - please review and edit as needed');
    } catch {
      toast.error('Failed to generate AI suggestions');
    } finally {
      setGenerating(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'qualified':
        return 'text-green-600 bg-green-100';
      case 'not_qualified':
        return 'text-red-600 bg-red-100';
      case 'needs_review':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <FolderKanban className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">R&D Projects</h1>
              <p className="text-gray-600">Add and describe your qualified R&D projects</p>
            </div>
          </div>
          <button onClick={() => setShowAddModal(true)} className="fluent-btn-primary">
            <Plus className="w-5 h-5" />
            Add Project
          </button>
        </div>
      </motion.div>

      {/* AI Info Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fluent-card p-4 bg-gradient-to-r from-primary-50 to-accent-50 border-primary-200"
      >
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-primary-600" />
          <div>
            <p className="font-medium text-gray-900">AI-Powered Project Descriptions</p>
            <p className="text-sm text-gray-600">
              Click the AI button on any project to generate professional descriptions and 4-part test answers
            </p>
          </div>
        </div>
      </motion.div>

      {/* Projects List */}
      {projects.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fluent-card p-12 text-center"
        >
          <FolderKanban className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Projects Yet</h3>
          <p className="text-gray-600 mb-4">Add your first R&D project to get started</p>
          <button onClick={() => setShowAddModal(true)} className="fluent-btn-primary">
            <Plus className="w-5 h-5" />
            Add Your First Project
          </button>
        </motion.div>
      ) : (
        <div className="space-y-4">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              className="fluent-card overflow-hidden"
            >
              {/* Project Header */}
              <div
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setExpandedProject(expandedProject === project.id ? null : project.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <FolderKanban className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{project.name}</h3>
                      <p className="text-sm text-gray-500">{project.business_component || 'No business component specified'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(project.qualification_status)}`}>
                      {project.qualification_status === 'qualified' && <CheckCircle className="w-3 h-3 inline mr-1" />}
                      {project.qualification_status === 'not_qualified' && <AlertCircle className="w-3 h-3 inline mr-1" />}
                      {project.qualification_status === 'pending' && <Clock className="w-3 h-3 inline mr-1" />}
                      {project.qualification_status.replace('_', ' ')}
                    </span>
                    {expandedProject === project.id ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Expanded Content */}
              <AnimatePresence>
                {expandedProject === project.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="border-t border-gray-100"
                  >
                    <div className="p-6 space-y-6">
                      {/* AI Generate Button */}
                      <button
                        onClick={() => handleGenerateAI(project.id)}
                        disabled={generating === project.id}
                        className="w-full fluent-btn bg-gradient-to-r from-primary-50 to-accent-50 text-primary-700 border-2 border-primary-200 hover:border-primary-300"
                      >
                        {generating === project.id ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Generating AI Suggestions...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-5 h-5" />
                            Generate AI Description & 4-Part Test Answers
                          </>
                        )}
                      </button>

                      {/* Project Description */}
                      <div>
                        <label className="fluent-label flex items-center gap-2">
                          <Lightbulb className="w-4 h-4 text-primary-600" />
                          Project Description
                        </label>
                        <textarea
                          value={project.description}
                          onChange={(e) =>
                            setProjects(projects.map((p) =>
                              p.id === project.id ? { ...p, description: e.target.value } : p
                            ))
                          }
                          className="fluent-textarea"
                          rows={4}
                          placeholder="Describe what this project aims to achieve..."
                        />
                      </div>

                      {/* 4-Part Test Section */}
                      <div className="space-y-4">
                        <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                          <Target className="w-5 h-5 text-primary-600" />
                          IRS 4-Part Test Qualification
                        </h4>

                        {/* Permitted Purpose */}
                        <div className="p-4 bg-gray-50 rounded-xl">
                          <h5 className="font-medium text-gray-900 mb-2">1. Permitted Purpose</h5>
                          <p className="text-sm text-gray-600 mb-3">
                            Does this project aim to develop a new or improved product, process, or software?
                          </p>
                          <textarea
                            value={project.four_part_test.permitted_purpose.answer}
                            onChange={(e) => {
                              const updated = { ...project };
                              updated.four_part_test.permitted_purpose.answer = e.target.value;
                              setProjects(projects.map((p) => (p.id === project.id ? updated : p)));
                            }}
                            className="fluent-textarea"
                            rows={3}
                            placeholder="Describe the new or improved functionality..."
                          />
                        </div>

                        {/* Technological Nature */}
                        <div className="p-4 bg-gray-50 rounded-xl">
                          <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <Microscope className="w-4 h-4 text-primary-600" />
                            2. Technological in Nature
                          </h5>
                          <p className="text-sm text-gray-600 mb-3">
                            Does this project rely on principles of physical science, biology, engineering, or computer science?
                          </p>
                          <textarea
                            value={project.four_part_test.technological_nature.answer}
                            onChange={(e) => {
                              const updated = { ...project };
                              updated.four_part_test.technological_nature.answer = e.target.value;
                              setProjects(projects.map((p) => (p.id === project.id ? updated : p)));
                            }}
                            className="fluent-textarea"
                            rows={3}
                            placeholder="Describe the technical disciplines involved..."
                          />
                        </div>

                        {/* Elimination of Uncertainty */}
                        <div className="p-4 bg-gray-50 rounded-xl">
                          <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <AlertCircle className="w-4 h-4 text-primary-600" />
                            3. Elimination of Uncertainty
                          </h5>
                          <p className="text-sm text-gray-600 mb-3">
                            What technical uncertainties did you face regarding capability, method, or design?
                          </p>
                          <textarea
                            value={project.four_part_test.elimination_uncertainty.answer}
                            onChange={(e) => {
                              const updated = { ...project };
                              updated.four_part_test.elimination_uncertainty.answer = e.target.value;
                              setProjects(projects.map((p) => (p.id === project.id ? updated : p)));
                            }}
                            className="fluent-textarea"
                            rows={3}
                            placeholder="Describe the technical uncertainties and how they were resolved..."
                          />
                        </div>

                        {/* Process of Experimentation */}
                        <div className="p-4 bg-gray-50 rounded-xl">
                          <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <Beaker className="w-4 h-4 text-primary-600" />
                            4. Process of Experimentation
                          </h5>
                          <p className="text-sm text-gray-600 mb-3">
                            What experimentation, testing, or evaluation was conducted to resolve the uncertainties?
                          </p>
                          <textarea
                            value={project.four_part_test.process_experimentation.answer}
                            onChange={(e) => {
                              const updated = { ...project };
                              updated.four_part_test.process_experimentation.answer = e.target.value;
                              setProjects(projects.map((p) => (p.id === project.id ? updated : p)));
                            }}
                            className="fluent-textarea"
                            rows={3}
                            placeholder="Describe your experimentation process..."
                          />
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                        <button
                          onClick={() => handleDeleteProject(project.id)}
                          className="fluent-btn-ghost text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </button>
                        <button
                          onClick={() => handleUpdateProject(project)}
                          disabled={saving}
                          className="fluent-btn-primary"
                        >
                          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                          Save Project
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}

      {/* Add Project Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-lg bg-white rounded-2xl shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900">Add New Project</h2>
                <button onClick={() => setShowAddModal(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="fluent-label">Project Name *</label>
                  <input
                    type="text"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., Advanced Battery Management System"
                  />
                </div>
                <div>
                  <label className="fluent-label">Business Component</label>
                  <input
                    type="text"
                    value={newProject.business_component}
                    onChange={(e) => setNewProject({ ...newProject, business_component: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., Electric Vehicle Powertrain"
                  />
                </div>
                <div>
                  <label className="fluent-label">Department</label>
                  <input
                    type="text"
                    value={newProject.department}
                    onChange={(e) => setNewProject({ ...newProject, department: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., Engineering R&D"
                  />
                </div>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="fluent-label">Start Date</label>
                    <input
                      type="date"
                      value={newProject.start_date}
                      onChange={(e) => setNewProject({ ...newProject, start_date: e.target.value })}
                      className="fluent-input"
                    />
                  </div>
                  <div className="flex items-end pb-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newProject.is_ongoing}
                        onChange={(e) => setNewProject({ ...newProject, is_ongoing: e.target.checked })}
                        className="fluent-checkbox"
                      />
                      <span className="text-sm text-gray-700">Ongoing Project</span>
                    </label>
                  </div>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-600 mt-0.5" />
                  <p className="text-sm text-blue-800">
                    You can add detailed descriptions and 4-part test answers after creating the project
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
                <button onClick={() => setShowAddModal(false)} className="fluent-btn-secondary">
                  Cancel
                </button>
                <button onClick={handleAddProject} disabled={saving} className="fluent-btn-primary">
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  Add Project
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
