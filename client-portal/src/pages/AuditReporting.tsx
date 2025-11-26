/**
 * Audit Reporting
 * Generate audit reports, management letters, and client deliverables
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  Download,
  Eye,
  Edit,
  Send,
  CheckCircle2,
  Clock,
  Brain,
  Sparkles,
  Mail,
  Printer,
  Share2,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Report {
  id: string;
  title: string;
  type: string;
  status: 'draft' | 'review' | 'finalized';
  lastModified: string;
  generatedBy?: string;
  aiAssisted: boolean;
}

const AuditReporting: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedReport, setSelectedReport] = useState<string | null>(null);

  const reports: Report[] = [
    {
      id: '1',
      title: 'Independent Auditor's Report',
      type: 'Audit Opinion',
      status: 'review',
      lastModified: '2024-11-22',
      generatedBy: 'Sarah Johnson',
      aiAssisted: true,
    },
    {
      id: '2',
      title: 'Management Letter',
      type: 'Management Communication',
      status: 'draft',
      lastModified: '2024-11-21',
      generatedBy: 'AI Assistant',
      aiAssisted: true,
    },
    {
      id: '3',
      title: 'Financial Statements with Notes',
      type: 'Financial Statements',
      status: 'draft',
      lastModified: '2024-11-20',
      generatedBy: 'John Smith',
      aiAssisted: false,
    },
    {
      id: '4',
      title: 'Internal Control Recommendations',
      type: 'Management Communication',
      status: 'draft',
      lastModified: '2024-11-19',
      generatedBy: 'AI Assistant',
      aiAssisted: true,
    },
    {
      id: '5',
      title: 'Audit Summary Memorandum',
      type: 'Internal Documentation',
      status: 'finalized',
      lastModified: '2024-11-18',
      generatedBy: 'Sarah Johnson',
      aiAssisted: false,
    },
  ];

  const reportTemplates = [
    {
      category: 'Audit Opinions',
      templates: [
        'Unmodified Opinion - Standard',
        'Modified Opinion - Qualified',
        'Modified Opinion - Adverse',
        'Modified Opinion - Disclaimer',
      ],
    },
    {
      category: 'Management Communications',
      templates: [
        'Management Letter',
        'Management Representation Letter',
        'Internal Control Recommendations',
        'Required Communications Letter',
      ],
    },
    {
      category: 'Financial Statements',
      templates: [
        'Balance Sheet',
        'Income Statement',
        'Cash Flow Statement',
        'Statement of Changes in Equity',
        'Notes to Financial Statements',
      ],
    },
    {
      category: 'Internal Documentation',
      templates: [
        'Audit Summary Memorandum',
        'Engagement Completion Checklist',
        'Independence Confirmation',
        'Workpaper Binder Index',
      ],
    },
  ];

  const aiSuggestions = [
    {
      title: 'Enhance Management Letter',
      description: 'AI has identified 3 additional recommendations based on audit findings',
      action: 'Review Suggestions',
    },
    {
      title: 'Update Risk Disclosures',
      description: 'New industry risks identified that may require disclosure in notes',
      action: 'View Risks',
    },
    {
      title: 'Improve Clarity',
      description: 'AI suggests simplified language for 2 complex note disclosures',
      action: 'Apply Changes',
    },
  ];

  const getStatusConfig = (status: string) => {
    const configs = {
      draft: { label: 'Draft', color: 'gray', icon: Edit },
      review: { label: 'In Review', color: 'yellow', icon: Eye },
      finalized: { label: 'Finalized', color: 'green', icon: CheckCircle2 },
    };
    return configs[status as keyof typeof configs] || configs.draft;
  };

  const handleGenerateReport = (template: string) => {
    toast.success(`Generating ${template} with AI assistance...`);
  };

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <button
          onClick={() => navigate(`/firm/engagements/${id}/workspace`)}
          className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-neutral-700" />
        </button>
        <div className="flex-1">
          <h1 className="text-display text-neutral-900 mb-1">Audit Reports & Deliverables</h1>
          <p className="text-body text-neutral-600">
            Generate audit reports, management letters, and client deliverables
          </p>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">Total Reports</p>
            <FileText className="w-4 h-4 text-primary-600" />
          </div>
          <p className="text-title-large text-primary-600 font-semibold">{reports.length}</p>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">Draft</p>
            <Edit className="w-4 h-4 text-neutral-600" />
          </div>
          <p className="text-title-large text-neutral-600 font-semibold">
            {reports.filter((r) => r.status === 'draft').length}
          </p>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">In Review</p>
            <Eye className="w-4 h-4 text-warning-600" />
          </div>
          <p className="text-title-large text-warning-600 font-semibold">
            {reports.filter((r) => r.status === 'review').length}
          </p>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">Finalized</p>
            <CheckCircle2 className="w-4 h-4 text-success-600" />
          </div>
          <p className="text-title-large text-success-600 font-semibold">
            {reports.filter((r) => r.status === 'finalized').length}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports List */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h2 className="text-title text-neutral-900 mb-4">Generated Reports</h2>
            <div className="space-y-3">
              {reports.map((report, index) => {
                const statusConfig = getStatusConfig(report.status);
                const StatusIcon = statusConfig.icon;

                return (
                  <motion.div
                    key={report.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="fluent-card p-5 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-body-strong text-neutral-900">{report.title}</h3>
                          {report.aiAssisted && (
                            <div className="flex items-center gap-1 px-2 py-0.5 bg-purple-50 border border-purple-200 rounded-fluent">
                              <Sparkles className="w-3 h-3 text-purple-600" />
                              <span className="text-caption font-medium text-purple-700">AI Assisted</span>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-caption text-neutral-600">
                          <span>{report.type}</span>
                          <div className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            <span>{new Date(report.lastModified).toLocaleDateString()}</span>
                          </div>
                          {report.generatedBy && <span>By {report.generatedBy}</span>}
                        </div>
                      </div>

                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-${statusConfig.color}-50 text-${statusConfig.color}-700`}
                      >
                        <StatusIcon className="w-3.5 h-3.5" />
                        {statusConfig.label}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button className="fluent-btn-secondary text-sm">
                        <Eye className="w-3.5 h-3.5" />
                        View
                      </button>
                      <button className="fluent-btn-secondary text-sm">
                        <Edit className="w-3.5 h-3.5" />
                        Edit
                      </button>
                      <button className="fluent-btn-secondary text-sm">
                        <Download className="w-3.5 h-3.5" />
                        Download
                      </button>
                      {report.status === 'finalized' && (
                        <button className="fluent-btn-primary text-sm">
                          <Send className="w-3.5 h-3.5" />
                          Send to Client
                        </button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Report Templates */}
          <div>
            <h2 className="text-title text-neutral-900 mb-4">Report Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reportTemplates.map((category, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="fluent-card p-5"
                >
                  <h3 className="text-body-strong text-neutral-900 mb-3">{category.category}</h3>
                  <div className="space-y-2">
                    {category.templates.map((template, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleGenerateReport(template)}
                        className="w-full text-left px-3 py-2 border border-neutral-200 rounded-fluent hover:border-primary-300 hover:bg-primary-50 transition-all text-caption text-neutral-700 hover:text-primary-700"
                      >
                        {template}
                      </button>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* AI Suggestions */}
          <div className="fluent-card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-primary-600" />
              <h3 className="text-body-strong text-neutral-900">AI Suggestions</h3>
            </div>
            <div className="space-y-3">
              {aiSuggestions.map((suggestion, index) => (
                <div key={index} className="p-3 bg-purple-50 border border-purple-200 rounded-fluent">
                  <h4 className="text-caption font-semibold text-purple-900 mb-1">
                    {suggestion.title}
                  </h4>
                  <p className="text-caption text-purple-800 mb-3">{suggestion.description}</p>
                  <button className="text-caption font-medium text-purple-600 hover:text-purple-700">
                    {suggestion.action} →
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Brain className="w-4 h-4" />
                Generate AI Report
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Download className="w-4 h-4" />
                Download All Reports
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Mail className="w-4 h-4" />
                Email to Client
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Printer className="w-4 h-4" />
                Print Package
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Share2 className="w-4 h-4" />
                Share Securely
              </button>
            </div>
          </div>

          {/* Delivery Checklist */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Delivery Checklist</h3>
            <div className="space-y-2">
              {[
                { item: 'Audit Opinion Signed', done: true },
                { item: 'Financial Statements Reviewed', done: true },
                { item: 'Management Letter Approved', done: false },
                { item: 'Required Communications Sent', done: false },
                { item: 'Client Acceptance Obtained', done: false },
              ].map((check, index) => (
                <div key={index} className="flex items-center gap-2">
                  {check.done ? (
                    <CheckCircle2 className="w-4 h-4 text-success-600" />
                  ) : (
                    <div className="w-4 h-4 border-2 border-neutral-300 rounded-full" />
                  )}
                  <span
                    className={`text-caption ${
                      check.done ? 'text-success-700 font-medium' : 'text-neutral-700'
                    }`}
                  >
                    {check.item}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditReporting;
