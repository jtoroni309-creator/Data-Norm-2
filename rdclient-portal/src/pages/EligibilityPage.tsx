/**
 * Eligibility Questionnaire Page
 * AI-assisted eligibility questionnaire for R&D tax credit determination
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ClipboardCheck,
  Building2,
  Lightbulb,
  AlertTriangle,
  Beaker,
  Brain,
  ChevronRight,
  ChevronLeft,
  Save,
  CheckCircle,
  Loader2,
  Sparkles,
  Info,
} from 'lucide-react';
import studyService from '../services/study.service';
import toast from 'react-hot-toast';
import type { EligibilityQuestionnaire, CompanyInfo, RDActivitiesInfo, TechnicalUncertaintyInfo, ExperimentationInfo } from '../types';

type Step = 'company' | 'activities' | 'uncertainty' | 'experimentation' | 'review';

const steps: { id: Step; label: string; icon: React.ElementType }[] = [
  { id: 'company', label: 'Company Information', icon: Building2 },
  { id: 'activities', label: 'R&D Activities', icon: Lightbulb },
  { id: 'uncertainty', label: 'Technical Uncertainty', icon: AlertTriangle },
  { id: 'experimentation', label: 'Experimentation', icon: Beaker },
  { id: 'review', label: 'Review & Submit', icon: CheckCircle },
];

const industries = [
  'Software & Technology',
  'Manufacturing',
  'Engineering Services',
  'Life Sciences & Pharma',
  'Aerospace & Defense',
  'Food & Beverage',
  'Agriculture',
  'Energy',
  'Construction',
  'Financial Services',
  'Other',
];

const rdAreas = [
  'New Product Development',
  'Process Improvements',
  'Software Development',
  'Hardware Development',
  'Manufacturing Optimization',
  'Quality Improvements',
  'Cost Reduction R&D',
  'Environmental Solutions',
  'Automation Projects',
  'Materials Research',
];

const testingMethods = [
  'Prototyping',
  'Computer Simulations',
  'Laboratory Testing',
  'Field Testing',
  'Beta Testing',
  'A/B Testing',
  'Quality Assurance Testing',
  'Performance Testing',
];

export default function EligibilityPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState<Step>('company');

  // Form state
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo>({
    company_name: '',
    industry: '',
    employees_count: 0,
    years_in_business: 0,
    has_rd_department: false,
  });

  const [rdActivities, setRdActivities] = useState<RDActivitiesInfo>({
    develops_new_products: false,
    improves_existing_products: false,
    develops_new_processes: false,
    develops_software: false,
    designs_prototypes: false,
    conducts_testing: false,
    rd_activity_description: '',
    primary_rd_areas: [],
  });

  const [uncertainty, setUncertainty] = useState<TechnicalUncertaintyInfo>({
    faced_capability_uncertainty: false,
    faced_method_uncertainty: false,
    faced_design_uncertainty: false,
    uncertainty_examples: '',
    how_resolved: '',
  });

  const [experimentation, setExperimentation] = useState<ExperimentationInfo>({
    uses_systematic_approach: false,
    evaluates_alternatives: false,
    documents_experiments: false,
    conducts_testing: false,
    experimentation_description: '',
    testing_methods: [],
  });

  const [aiAnalysis, setAiAnalysis] = useState<{
    score: number;
    is_likely_eligible: boolean;
    recommendations: string[];
  } | null>(null);

  // Load existing questionnaire
  useEffect(() => {
    const loadQuestionnaire = async () => {
      try {
        const data = await studyService.getEligibilityQuestionnaire();
        if (data) {
          setCompanyInfo(data.company_info);
          setRdActivities(data.rd_activities);
          setUncertainty(data.technical_uncertainty);
          setExperimentation(data.experimentation);
        }
      } catch (error) {
        console.error('Failed to load questionnaire:', error);
      } finally {
        setLoading(false);
      }
    };

    loadQuestionnaire();
  }, []);

  // Auto-save handler
  const autoSave = useCallback(async () => {
    try {
      await studyService.saveEligibilityQuestionnaire({
        company_info: companyInfo,
        rd_activities: rdActivities,
        technical_uncertainty: uncertainty,
        experimentation,
      });
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }, [companyInfo, rdActivities, uncertainty, experimentation]);

  // Save when data changes (debounced)
  useEffect(() => {
    if (!loading) {
      const timer = setTimeout(autoSave, 2000);
      return () => clearTimeout(timer);
    }
  }, [autoSave, loading]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await studyService.saveEligibilityQuestionnaire({
        company_info: companyInfo,
        rd_activities: rdActivities,
        technical_uncertainty: uncertainty,
        experimentation,
      });
      toast.success('Progress saved');
    } catch {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const analysis = await studyService.analyzeEligibility();
      setAiAnalysis(analysis);
      toast.success('AI analysis complete');
    } catch {
      toast.error('Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);
  const canGoNext = currentStepIndex < steps.length - 1;
  const canGoPrev = currentStepIndex > 0;

  const goNext = () => {
    if (canGoNext) {
      setCurrentStep(steps[currentStepIndex + 1].id);
    }
  };

  const goPrev = () => {
    if (canGoPrev) {
      setCurrentStep(steps[currentStepIndex - 1].id);
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
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <ClipboardCheck className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Eligibility Questionnaire</h1>
            <p className="text-gray-600">
              Answer these questions to help determine your R&D tax credit eligibility
            </p>
          </div>
        </div>
      </motion.div>

      {/* Progress Steps */}
      <div className="fluent-card p-4">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = step.id === currentStep;
            const isCompleted = index < currentStepIndex;

            return (
              <button
                key={step.id}
                onClick={() => setCurrentStep(step.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all
                  ${isActive ? 'bg-primary-100 text-primary-700' : ''}
                  ${isCompleted ? 'text-green-600' : 'text-gray-500'}
                  hover:bg-gray-100`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center
                    ${isActive ? 'bg-primary-600 text-white' : ''}
                    ${isCompleted ? 'bg-green-100 text-green-600' : 'bg-gray-100'}`}
                >
                  {isCompleted ? <CheckCircle className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                </div>
                <span className="hidden md:inline text-sm font-medium">{step.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Form Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="fluent-card p-6"
        >
          {/* Company Information */}
          {currentStep === 'company' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Company Information</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="fluent-label">Company Name</label>
                  <input
                    type="text"
                    value={companyInfo.company_name}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, company_name: e.target.value })}
                    className="fluent-input"
                    placeholder="Enter company name"
                  />
                </div>

                <div>
                  <label className="fluent-label">Industry</label>
                  <select
                    value={companyInfo.industry}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, industry: e.target.value })}
                    className="fluent-select"
                  >
                    <option value="">Select industry</option>
                    {industries.map((ind) => (
                      <option key={ind} value={ind}>
                        {ind}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="fluent-label">Number of Employees</label>
                  <input
                    type="number"
                    value={companyInfo.employees_count || ''}
                    onChange={(e) =>
                      setCompanyInfo({ ...companyInfo, employees_count: parseInt(e.target.value) || 0 })
                    }
                    className="fluent-input"
                    placeholder="Total employees"
                  />
                </div>

                <div>
                  <label className="fluent-label">Years in Business</label>
                  <input
                    type="number"
                    value={companyInfo.years_in_business || ''}
                    onChange={(e) =>
                      setCompanyInfo({ ...companyInfo, years_in_business: parseInt(e.target.value) || 0 })
                    }
                    className="fluent-input"
                    placeholder="Years operating"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                <input
                  type="checkbox"
                  id="has_rd"
                  checked={companyInfo.has_rd_department}
                  onChange={(e) => setCompanyInfo({ ...companyInfo, has_rd_department: e.target.checked })}
                  className="fluent-checkbox"
                />
                <label htmlFor="has_rd" className="text-gray-700 cursor-pointer">
                  We have a dedicated R&D or engineering department
                </label>
              </div>
            </div>
          )}

          {/* R&D Activities */}
          {currentStep === 'activities' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">R&D Activities</h2>
              <p className="text-gray-600">Select all activities your company engages in:</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { key: 'develops_new_products', label: 'Develops new products or services' },
                  { key: 'improves_existing_products', label: 'Improves existing products' },
                  { key: 'develops_new_processes', label: 'Develops new processes or methods' },
                  { key: 'develops_software', label: 'Develops software or algorithms' },
                  { key: 'designs_prototypes', label: 'Designs and builds prototypes' },
                  { key: 'conducts_testing', label: 'Conducts testing and experiments' },
                ].map((activity) => (
                  <label
                    key={activity.key}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all
                      ${rdActivities[activity.key as keyof RDActivitiesInfo]
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }`}
                  >
                    <input
                      type="checkbox"
                      checked={rdActivities[activity.key as keyof RDActivitiesInfo] as boolean}
                      onChange={(e) =>
                        setRdActivities({ ...rdActivities, [activity.key]: e.target.checked })
                      }
                      className="fluent-checkbox"
                    />
                    <span className="text-gray-700">{activity.label}</span>
                  </label>
                ))}
              </div>

              <div>
                <label className="fluent-label">Primary R&D Focus Areas</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {rdAreas.map((area) => (
                    <button
                      key={area}
                      type="button"
                      onClick={() => {
                        const areas = rdActivities.primary_rd_areas.includes(area)
                          ? rdActivities.primary_rd_areas.filter((a) => a !== area)
                          : [...rdActivities.primary_rd_areas, area];
                        setRdActivities({ ...rdActivities, primary_rd_areas: areas });
                      }}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all
                        ${rdActivities.primary_rd_areas.includes(area)
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      {area}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="fluent-label">Describe Your R&D Activities</label>
                <textarea
                  value={rdActivities.rd_activity_description}
                  onChange={(e) =>
                    setRdActivities({ ...rdActivities, rd_activity_description: e.target.value })
                  }
                  className="fluent-textarea"
                  rows={4}
                  placeholder="Describe the types of R&D projects your company undertakes..."
                />
              </div>
            </div>
          )}

          {/* Technical Uncertainty */}
          {currentStep === 'uncertainty' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Technical Uncertainty</h2>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                <p className="text-sm text-blue-800">
                  Technical uncertainty exists when you don't know if something can be done,
                  how it should be done, or what the best design approach is.
                </p>
              </div>

              <div className="space-y-3">
                {[
                  {
                    key: 'faced_capability_uncertainty',
                    label: 'Capability Uncertainty',
                    desc: "We weren't certain if we could achieve our technical objectives",
                  },
                  {
                    key: 'faced_method_uncertainty',
                    label: 'Method Uncertainty',
                    desc: "We weren't certain about the best method or approach to use",
                  },
                  {
                    key: 'faced_design_uncertainty',
                    label: 'Design Uncertainty',
                    desc: "We weren't certain about the optimal design of components",
                  },
                ].map((item) => (
                  <label
                    key={item.key}
                    className={`block p-4 rounded-xl border-2 cursor-pointer transition-all
                      ${uncertainty[item.key as keyof TechnicalUncertaintyInfo]
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }`}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={uncertainty[item.key as keyof TechnicalUncertaintyInfo] as boolean}
                        onChange={(e) =>
                          setUncertainty({ ...uncertainty, [item.key]: e.target.checked })
                        }
                        className="fluent-checkbox"
                      />
                      <div>
                        <div className="font-medium text-gray-900">{item.label}</div>
                        <div className="text-sm text-gray-600">{item.desc}</div>
                      </div>
                    </div>
                  </label>
                ))}
              </div>

              <div>
                <label className="fluent-label">Examples of Technical Uncertainty</label>
                <textarea
                  value={uncertainty.uncertainty_examples}
                  onChange={(e) =>
                    setUncertainty({ ...uncertainty, uncertainty_examples: e.target.value })
                  }
                  className="fluent-textarea"
                  rows={4}
                  placeholder="Describe specific technical challenges or uncertainties you faced..."
                />
              </div>

              <div>
                <label className="fluent-label">How Were These Resolved?</label>
                <textarea
                  value={uncertainty.how_resolved}
                  onChange={(e) => setUncertainty({ ...uncertainty, how_resolved: e.target.value })}
                  className="fluent-textarea"
                  rows={3}
                  placeholder="Describe the process used to resolve technical uncertainties..."
                />
              </div>
            </div>
          )}

          {/* Process of Experimentation */}
          {currentStep === 'experimentation' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Process of Experimentation</h2>

              <div className="space-y-3">
                {[
                  {
                    key: 'uses_systematic_approach',
                    label: 'We use a systematic approach to evaluate alternatives',
                  },
                  {
                    key: 'evaluates_alternatives',
                    label: 'We evaluate multiple design alternatives before selecting one',
                  },
                  {
                    key: 'documents_experiments',
                    label: 'We document our experiments and their results',
                  },
                  {
                    key: 'conducts_testing',
                    label: 'We conduct testing to validate our designs and solutions',
                  },
                ].map((item) => (
                  <label
                    key={item.key}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all
                      ${experimentation[item.key as keyof ExperimentationInfo]
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }`}
                  >
                    <input
                      type="checkbox"
                      checked={experimentation[item.key as keyof ExperimentationInfo] as boolean}
                      onChange={(e) =>
                        setExperimentation({ ...experimentation, [item.key]: e.target.checked })
                      }
                      className="fluent-checkbox"
                    />
                    <span className="text-gray-700">{item.label}</span>
                  </label>
                ))}
              </div>

              <div>
                <label className="fluent-label">Testing Methods Used</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {testingMethods.map((method) => (
                    <button
                      key={method}
                      type="button"
                      onClick={() => {
                        const methods = experimentation.testing_methods.includes(method)
                          ? experimentation.testing_methods.filter((m) => m !== method)
                          : [...experimentation.testing_methods, method];
                        setExperimentation({ ...experimentation, testing_methods: methods });
                      }}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all
                        ${experimentation.testing_methods.includes(method)
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      {method}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="fluent-label">Describe Your Experimentation Process</label>
                <textarea
                  value={experimentation.experimentation_description}
                  onChange={(e) =>
                    setExperimentation({ ...experimentation, experimentation_description: e.target.value })
                  }
                  className="fluent-textarea"
                  rows={4}
                  placeholder="Describe how you conduct experiments and evaluate alternatives..."
                />
              </div>
            </div>
          )}

          {/* Review */}
          {currentStep === 'review' && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Review & AI Analysis</h2>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="fluent-btn-primary w-full py-4"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="w-5 h-5" />
                    Analyze Eligibility with AI
                  </>
                )}
              </button>

              {aiAnalysis && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-6 rounded-xl border-2 ${
                    aiAnalysis.is_likely_eligible
                      ? 'border-green-200 bg-green-50'
                      : 'border-orange-200 bg-orange-50'
                  }`}
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div
                      className={`w-16 h-16 rounded-full flex items-center justify-center ${
                        aiAnalysis.is_likely_eligible ? 'bg-green-100' : 'bg-orange-100'
                      }`}
                    >
                      <span
                        className={`text-2xl font-bold ${
                          aiAnalysis.is_likely_eligible ? 'text-green-600' : 'text-orange-600'
                        }`}
                      >
                        {aiAnalysis.score}%
                      </span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {aiAnalysis.is_likely_eligible ? 'Likely Eligible' : 'Needs Review'}
                      </h3>
                      <p className="text-gray-600">
                        Based on your responses, you {aiAnalysis.is_likely_eligible ? 'appear to qualify' : 'may qualify'} for R&D tax credits
                      </p>
                    </div>
                  </div>

                  {aiAnalysis.recommendations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-primary-600" />
                        AI Recommendations
                      </h4>
                      <ul className="space-y-2">
                        {aiAnalysis.recommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                            <span className="text-primary-600 mt-0.5">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={goPrev}
          disabled={!canGoPrev}
          className="fluent-btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-5 h-5" />
          Previous
        </button>

        <button onClick={handleSave} disabled={saving} className="fluent-btn-ghost">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Save Progress
        </button>

        <button
          onClick={goNext}
          disabled={!canGoNext}
          className="fluent-btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
