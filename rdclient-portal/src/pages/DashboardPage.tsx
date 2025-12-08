/**
 * Dashboard Page
 * Main dashboard showing study progress and quick actions
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ClipboardCheck,
  FolderKanban,
  Users,
  FileText,
  Upload,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  Brain,
  Calendar,
  Building2,
} from 'lucide-react';
import { useAuthStore } from '../store/auth';
import studyService from '../services/study.service';
import type { RDStudyInfo } from '../types';

interface ProgressItem {
  id: string;
  label: string;
  path: string;
  icon: React.ElementType;
  completed: boolean;
  count?: number;
  required: boolean;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [studyInfo, setStudyInfo] = useState<RDStudyInfo | null>(null);

  useEffect(() => {
    const loadStudyInfo = async () => {
      try {
        const info = await studyService.getStudyInfo();
        setStudyInfo(info);
      } catch (error) {
        console.error('Failed to load study info:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStudyInfo();
  }, []);

  const progressItems: ProgressItem[] = [
    {
      id: 'eligibility',
      label: 'Eligibility Questionnaire',
      path: '/eligibility',
      icon: ClipboardCheck,
      completed: studyInfo?.progress.eligibility_complete || false,
      required: true,
    },
    {
      id: 'projects',
      label: 'R&D Projects',
      path: '/projects',
      icon: FolderKanban,
      completed: (studyInfo?.progress.projects_added || 0) > 0,
      count: studyInfo?.progress.projects_added,
      required: true,
    },
    {
      id: 'employees',
      label: 'Employees',
      path: '/employees',
      icon: Users,
      completed: (studyInfo?.progress.employees_added || 0) > 0,
      count: studyInfo?.progress.employees_added,
      required: true,
    },
    {
      id: 'tax-returns',
      label: 'Tax Returns (Prior 2 Years)',
      path: '/tax-returns',
      icon: FileText,
      completed: studyInfo?.progress.tax_returns_uploaded || false,
      required: true,
    },
    {
      id: 'documents',
      label: 'Supporting Documents',
      path: '/documents',
      icon: Upload,
      completed: (studyInfo?.progress.documents_uploaded || 0) > 0,
      count: studyInfo?.progress.documents_uploaded,
      required: false,
    },
  ];

  const completedCount = progressItems.filter((item) => item.completed).length;
  const requiredCount = progressItems.filter((item) => item.required).length;
  const requiredCompleted = progressItems.filter((item) => item.required && item.completed).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome, {user?.full_name?.split(' ')[0] || 'there'}!
            </h1>
            <p className="text-gray-600 mt-1">
              Complete the steps below to submit your R&D Tax Credit documentation
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">Study Progress</p>
              <p className="text-2xl font-bold text-primary-600">
                {studyInfo?.progress.overall_percentage || 0}%
              </p>
            </div>
            <div className="w-16 h-16 relative">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="6"
                  fill="none"
                  className="text-gray-200"
                />
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="6"
                  fill="none"
                  strokeDasharray={175.93}
                  strokeDashoffset={175.93 - (175.93 * (studyInfo?.progress.overall_percentage || 0)) / 100}
                  strokeLinecap="round"
                  className="text-primary-600 transition-all duration-500"
                />
              </svg>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Study Info Card */}
      {studyInfo && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="fluent-card p-6"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-gray-900">{studyInfo.name}</h2>
              <p className="text-gray-600">{studyInfo.company_name}</p>
              <div className="flex flex-wrap gap-4 mt-3 text-sm">
                <div className="flex items-center gap-1 text-gray-500">
                  <Calendar className="w-4 h-4" />
                  <span>Tax Year: {studyInfo.tax_year}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Building2 className="w-4 h-4" />
                  <span>CPA Firm: {studyInfo.firm_name}</span>
                </div>
                {studyInfo.deadline && (
                  <div className="flex items-center gap-1 text-orange-600">
                    <Clock className="w-4 h-4" />
                    <span>Deadline: {new Date(studyInfo.deadline).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Progress Steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Required Information</h2>
          <span className="text-sm text-gray-500">
            {requiredCompleted} of {requiredCount} required items complete
          </span>
        </div>

        <div className="space-y-3">
          {progressItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Link
                  to={item.path}
                  className={`flex items-center gap-4 p-4 rounded-xl border-2 transition-all group
                    ${item.completed
                      ? 'border-green-200 bg-green-50 hover:border-green-300'
                      : 'border-gray-200 bg-white hover:border-primary-300 hover:bg-primary-50'
                    }`}
                >
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center
                      ${item.completed ? 'bg-green-100' : 'bg-gray-100 group-hover:bg-primary-100'}`}
                  >
                    {item.completed ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <Icon className="w-5 h-5 text-gray-500 group-hover:text-primary-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className={`font-medium ${item.completed ? 'text-green-800' : 'text-gray-900'}`}>
                        {item.label}
                      </h3>
                      {item.required && !item.completed && (
                        <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">
                          Required
                        </span>
                      )}
                    </div>
                    {item.count !== undefined && (
                      <p className="text-sm text-gray-500">
                        {item.count} {item.count === 1 ? 'item' : 'items'} added
                      </p>
                    )}
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* AI Assistance Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="fluent-card p-6 bg-gradient-to-br from-primary-50 to-accent-50 border-primary-200"
      >
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">AI-Powered Assistance</h3>
            <p className="text-gray-600 mt-1">
              Our AI assistant is available throughout the portal to help you write compelling project
              descriptions and ensure your R&D activities are properly documented.
            </p>
            <div className="flex flex-wrap gap-2 mt-3">
              <span className="text-xs bg-white/80 text-primary-700 px-3 py-1 rounded-full">
                Project Descriptions
              </span>
              <span className="text-xs bg-white/80 text-primary-700 px-3 py-1 rounded-full">
                4-Part Test Answers
              </span>
              <span className="text-xs bg-white/80 text-primary-700 px-3 py-1 rounded-full">
                Eligibility Analysis
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <Link
          to="/team"
          className="fluent-card p-5 hover:shadow-fluent-8 transition-shadow group"
        >
          <Users className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
            Invite Team Members
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Add colleagues to help provide information
          </p>
        </Link>

        <Link
          to="/documents"
          className="fluent-card p-5 hover:shadow-fluent-8 transition-shadow group"
        >
          <Upload className="w-8 h-8 text-primary-600 mb-3" />
          <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
            Upload Documents
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Add supporting documentation
          </p>
        </Link>

        <div className="fluent-card p-5 bg-gray-50">
          <TrendingUp className="w-8 h-8 text-gray-400 mb-3" />
          <h3 className="font-semibold text-gray-600">Submit for Review</h3>
          <p className="text-sm text-gray-400 mt-1">
            Complete all required items first
          </p>
        </div>
      </motion.div>
    </div>
  );
}
