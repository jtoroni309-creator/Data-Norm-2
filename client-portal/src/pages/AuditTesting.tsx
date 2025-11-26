/**
 * Audit Testing
 * Complete testing modules for all audit areas - Revenue, AR, Inventory, Fixed Assets, Liabilities
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  DollarSign,
  Package,
  Building,
  CreditCard,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  Brain,
  Upload,
  Download,
  Play,
  Pause,
  BarChart3,
  FileText,
  Users,
  Calendar,
  Target,
  Zap,
  ChevronRight,
  Plus,
  X,
  Loader2,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { substantiveTestingService, TestModule as APITestModule, Test as APITest, AIAnomaly } from '../services/substantive-testing.service';

interface TestModule {
  id: string;
  name: string;
  icon: any;
  color: string;
  description: string;
  tests: number;
  completed: number;
  anomalies: number;
}

interface Test {
  id: string;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed';
  sampleSize?: number;
  exceptions?: number;
  aiFlags?: number;
}

const iconMap: Record<string, any> = {
  DollarSign,
  FileText,
  Package,
  Building,
  CreditCard,
};

const AuditTesting: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [showSampleModal, setShowSampleModal] = useState(false);
  const [runningTest, setRunningTest] = useState(false);
  const [loading, setLoading] = useState(true);

  // Data from API
  const [testModules, setTestModules] = useState<TestModule[]>([]);
  const [moduleTests, setModuleTests] = useState<Test[]>([]);
  const [aiAnomalies, setAiAnomalies] = useState<AIAnomaly[]>([]);

  useEffect(() => {
    loadTestModules();
  }, [id]);

  useEffect(() => {
    if (selectedModule) {
      loadModuleTests(selectedModule);
    }
  }, [selectedModule]);

  const loadTestModules = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const modules = await substantiveTestingService.getTestModules(id);
      // Map API data to component format with icons
      const mappedModules = modules.map(m => ({
        ...m,
        icon: iconMap[m.icon] || DollarSign,
      }));
      setTestModules(mappedModules);
    } catch (error) {
      console.error('Failed to load test modules:', error);
      toast.error('Failed to load test modules');
    } finally {
      setLoading(false);
    }
  };

  const loadModuleTests = async (moduleId: string) => {
    if (!id) return;
    try {
      const [tests, anomalies] = await Promise.all([
        substantiveTestingService.getTestsForModule(id, moduleId),
        substantiveTestingService.getAIAnomalies(id, moduleId)
      ]);
      setModuleTests(tests);
      setAiAnomalies(anomalies);
    } catch (error) {
      console.error('Failed to load module tests:', error);
    }
  };

  const getStatusConfig = (status: string) => {
    const configs = {
      not_started: { label: 'Not Started', color: 'gray', icon: Pause },
      in_progress: { label: 'In Progress', color: 'blue', icon: Play },
      completed: { label: 'Completed', color: 'green', icon: CheckCircle2 },
    };
    return configs[status as keyof typeof configs] || configs.not_started;
  };

  const handleRunTest = async () => {
    if (!id || !selectedModule) return;
    setRunningTest(true);
    toast.success('Running AI-powered test analysis...');

    try {
      const anomalies = await substantiveTestingService.runAIAnalysis(id, selectedModule);
      setAiAnomalies(anomalies);
      toast.success(`Test completed - ${anomalies.length} anomalies detected`);
    } catch (error) {
      toast.error('AI analysis failed');
    } finally {
      setRunningTest(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="text-body text-neutral-600">Loading audit tests...</p>
        </div>
      </div>
    );
  }

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
          <h1 className="text-display text-neutral-900 mb-1">Audit Testing</h1>
          <p className="text-body text-neutral-600">
            Comprehensive testing modules for all audit areas
          </p>
        </div>
        <div className="flex gap-3">
          <button className="fluent-btn-secondary">
            <Upload className="w-4 h-4" />
            Import Data
          </button>
          <button className="fluent-btn-primary">
            <Download className="w-4 h-4" />
            Export Results
          </button>
        </div>
      </motion.div>

      {/* Test Modules Grid */}
      {!selectedModule && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {testModules.map((module, index) => {
              const Icon = module.icon;
              const completionRate = Math.round((module.completed / module.tests) * 100);

              return (
                <motion.button
                  key={module.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => setSelectedModule(module.id)}
                  className="fluent-card-interactive p-6 text-left"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`w-12 h-12 rounded-fluent bg-${module.color}-100 flex items-center justify-center`}
                    >
                      <Icon className={`w-6 h-6 text-${module.color}-600`} />
                    </div>
                    <ChevronRight className="w-5 h-5 text-neutral-400" />
                  </div>

                  <h3 className="text-body-strong text-neutral-900 mb-2">{module.name}</h3>
                  <p className="text-caption text-neutral-600 mb-4">{module.description}</p>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-caption">
                      <span className="text-neutral-600">Progress</span>
                      <span className="font-semibold text-neutral-900">
                        {module.completed}/{module.tests} tests
                      </span>
                    </div>
                    <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-${module.color}-500`}
                        style={{ width: `${completionRate}%` }}
                      />
                    </div>

                    {module.anomalies > 0 && (
                      <div
                        className={`flex items-center gap-2 px-3 py-2 rounded-fluent bg-warning-50 border border-warning-200`}
                      >
                        <AlertTriangle className="w-4 h-4 text-warning-600" />
                        <span className="text-caption font-medium text-warning-700">
                          {module.anomalies} anomalies detected
                        </span>
                      </div>
                    )}
                  </div>
                </motion.button>
              );
            })}
          </div>

          {/* Overall Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="fluent-card p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-caption text-neutral-600">Total Tests</p>
                <Target className="w-4 h-4 text-primary-600" />
              </div>
              <p className="text-title-large text-primary-600 font-semibold">
                {testModules.reduce((sum, m) => sum + m.tests, 0)}
              </p>
            </div>
            <div className="fluent-card p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-caption text-neutral-600">Completed</p>
                <CheckCircle2 className="w-4 h-4 text-success-600" />
              </div>
              <p className="text-title-large text-success-600 font-semibold">
                {testModules.reduce((sum, m) => sum + m.completed, 0)}
              </p>
            </div>
            <div className="fluent-card p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-caption text-neutral-600">AI Anomalies</p>
                <Brain className="w-4 h-4 text-warning-600" />
              </div>
              <p className="text-title-large text-warning-600 font-semibold">
                {testModules.reduce((sum, m) => sum + m.anomalies, 0)}
              </p>
            </div>
            <div className="fluent-card p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-caption text-neutral-600">Completion</p>
                <BarChart3 className="w-4 h-4 text-accent-600" />
              </div>
              <p className="text-title-large text-accent-600 font-semibold">
                {Math.round(
                  (testModules.reduce((sum, m) => sum + m.completed, 0) /
                    testModules.reduce((sum, m) => sum + m.tests, 0)) *
                    100
                )}
                %
              </p>
            </div>
          </div>
        </>
      )}

      {/* Revenue Testing Detail */}
      {selectedModule === 'revenue' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSelectedModule(null)}
              className="fluent-btn-secondary"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Modules
            </button>
            <div className="flex gap-3">
              <button
                onClick={() => setShowSampleModal(true)}
                className="fluent-btn-secondary"
              >
                <Plus className="w-4 h-4" />
                New Test
              </button>
              <button
                onClick={handleRunTest}
                disabled={runningTest}
                className="fluent-btn-primary"
              >
                <Zap className="w-4 h-4" />
                {runningTest ? 'Running AI Analysis...' : 'Run AI Analysis'}
              </button>
            </div>
          </div>

          {/* Tests List */}
          <div className="space-y-3">
            {moduleTests.map((test, index) => {
              const statusConfig = getStatusConfig(test.status);
              const StatusIcon = statusConfig.icon;

              return (
                <motion.div
                  key={test.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="fluent-card p-5 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-body-strong text-neutral-900">{test.name}</h4>
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-${statusConfig.color}-50 text-${statusConfig.color}-700`}
                        >
                          <StatusIcon className="w-3.5 h-3.5" />
                          {statusConfig.label}
                        </span>
                      </div>
                      <p className="text-caption text-neutral-600 mb-4">{test.description}</p>

                      <div className="flex items-center gap-6 text-caption text-neutral-600">
                        {test.sampleSize && (
                          <div className="flex items-center gap-1">
                            <Target className="w-3.5 h-3.5" />
                            <span>Sample: {test.sampleSize}</span>
                          </div>
                        )}
                        {test.exceptions !== undefined && (
                          <div className="flex items-center gap-1">
                            <AlertTriangle
                              className={`w-3.5 h-3.5 ${
                                test.exceptions > 0 ? 'text-warning-600' : 'text-success-600'
                              }`}
                            />
                            <span>Exceptions: {test.exceptions}</span>
                          </div>
                        )}
                        {test.aiFlags && test.aiFlags > 0 && (
                          <div className="flex items-center gap-1">
                            <Brain className="w-3.5 h-3.5 text-purple-600" />
                            <span className="text-purple-700 font-medium">
                              {test.aiFlags} AI flags
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <button className="fluent-btn-secondary ml-4">
                      View Details
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* AI Anomalies */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-primary-600" />
              <h3 className="text-title text-neutral-900">AI-Detected Anomalies</h3>
            </div>

            <div className="space-y-3">
              {aiAnomalies.map((anomaly, index) => {
                const typeConfig = {
                  high: { color: 'error', bg: 'error', icon: AlertTriangle },
                  medium: { color: 'warning', bg: 'warning', icon: AlertTriangle },
                  low: { color: 'primary', bg: 'primary', icon: Brain },
                };
                const config = typeConfig[anomaly.type as keyof typeof typeConfig];
                const Icon = config.icon;

                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`fluent-card p-5 border-l-4 border-${config.color}-500`}
                  >
                    <div className="flex items-start gap-4">
                      <div
                        className={`w-10 h-10 rounded-fluent bg-${config.bg}-100 flex items-center justify-center flex-shrink-0`}
                      >
                        <Icon className={`w-5 h-5 text-${config.color}-600`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="text-body-strong text-neutral-900">{anomaly.title}</h4>
                          <span
                            className={`px-2 py-0.5 rounded-fluent-sm text-caption font-medium bg-${config.bg}-100 text-${config.color}-700`}
                          >
                            {anomaly.type.toUpperCase()} RISK
                          </span>
                        </div>
                        <p className="text-body text-neutral-700 mb-3">{anomaly.description}</p>
                        <div className="bg-neutral-50 border border-neutral-200 rounded-fluent p-3">
                          <p className="text-caption font-semibold text-neutral-900 mb-1">
                            Recommendation:
                          </p>
                          <p className="text-caption text-neutral-700">{anomaly.recommendation}</p>
                        </div>
                        <div className="mt-3 flex items-center gap-2">
                          <span className="text-caption text-neutral-600">Test Area:</span>
                          <span className="text-caption font-medium text-primary-600">
                            {anomaly.testArea}
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Sample Selection Modal */}
      <AnimatePresence>
        {showSampleModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowSampleModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-2xl w-full shadow-fluent-16"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-title-large text-neutral-900">Sample Selection</h2>
                <button
                  onClick={() => setShowSampleModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Sampling Method
                  </label>
                  <select className="fluent-input">
                    <option>Statistical Sampling</option>
                    <option>Judgmental Sampling</option>
                    <option>Stratified Sampling</option>
                    <option>Random Sampling</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Population Size
                    </label>
                    <input type="number" className="fluent-input" placeholder="1000" />
                  </div>
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Sample Size
                    </label>
                    <input type="number" className="fluent-input" placeholder="60" />
                  </div>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Confidence Level
                  </label>
                  <select className="fluent-input">
                    <option>95%</option>
                    <option>90%</option>
                    <option>99%</option>
                  </select>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Expected Error Rate
                  </label>
                  <input type="number" className="fluent-input" placeholder="2.5" />
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button onClick={() => setShowSampleModal(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button
                  onClick={() => {
                    toast.success('Sample generated successfully!');
                    setShowSampleModal(false);
                  }}
                  className="fluent-btn-primary flex-1"
                >
                  Generate Sample
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AuditTesting;
