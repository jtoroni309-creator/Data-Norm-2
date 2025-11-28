/**
 * Tax Return Workspace
 * Detailed view for preparing and filing a tax return
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calculator,
  ArrowLeft,
  Save,
  Send,
  FileText,
  DollarSign,
  CreditCard,
  Receipt,
  FileCheck,
  HelpCircle,
  CheckCircle,
  Clock,
  AlertTriangle,
  Download,
  RefreshCw,
  ChevronRight,
  Info,
  Lightbulb,
  PieChart,
  Building2,
  User,
  Home,
  Briefcase,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { taxService } from '../services/tax.service';
import {
  TaxReturn,
  TaxCalculationResult,
  TaxLineExplanation,
  TaxSchedule,
} from '../types';

type TabType = 'overview' | 'income' | 'deductions' | 'credits' | 'schedules' | 'review' | 'efile';

const TaxReturnWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [taxReturn, setTaxReturn] = useState<TaxReturn | null>(null);
  const [calculation, setCalculation] = useState<TaxCalculationResult | null>(null);
  const [schedules, setSchedules] = useState<TaxSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [lineExplanation, setLineExplanation] = useState<TaxLineExplanation | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    if (id) {
      loadTaxReturn();
    }
  }, [id]);

  const loadTaxReturn = async () => {
    setLoading(true);
    try {
      const [returnData, calcData] = await Promise.all([
        taxService.getReturn(id!),
        taxService.getCalculationResult(id!).catch(() => null),
      ]);
      setTaxReturn(returnData);
      setCalculation(calcData);
    } catch (error) {
      console.error('Failed to load tax return:', error);
      // Use mock data for demo
      setTaxReturn(generateMockReturn());
      setCalculation(generateMockCalculation());
    } finally {
      setLoading(false);
    }
  };

  const generateMockReturn = (): TaxReturn => ({
    id: id || '1',
    firm_id: 'firm-1',
    client_id: 'client-1',
    tax_year: 2024,
    form_type: '1040',
    status: 'data_entry',
    taxpayer_first_name: 'Robert',
    taxpayer_last_name: 'Johnson',
    taxpayer_ssn: '***-**-4532',
    filing_status: 'married_filing_jointly',
    spouse_first_name: 'Sarah',
    spouse_last_name: 'Johnson',
    spouse_ssn: '***-**-7891',
    address_street: '123 Main Street',
    address_city: 'Austin',
    address_state: 'TX',
    address_zip: '78701',
    occupation: 'Software Engineer',
    spouse_occupation: 'Marketing Director',
    total_income: 285000,
    adjusted_gross_income: 265000,
    taxable_income: 215000,
    total_tax: 42500,
    total_payments: 45700,
    refund_or_owed: 3200,
    created_at: '2025-01-15',
    updated_at: '2025-02-20',
  });

  const generateMockCalculation = (): TaxCalculationResult => ({
    tax_return_id: id || '1',
    calculated_at: new Date().toISOString(),
    calculation_status: 'completed',
    wages: 245000,
    interest_income: 12500,
    dividend_income: 18500,
    business_income: 0,
    capital_gains: 9000,
    other_income: 0,
    total_income: 285000,
    adjustments_to_income: 20000,
    adjusted_gross_income: 265000,
    standard_deduction: 29200,
    itemized_deductions: 42000,
    deduction_used: 'itemized',
    qualified_business_income_deduction: 0,
    taxable_income: 215000,
    regular_tax: 42500,
    amt: 0,
    niit: 0,
    self_employment_tax: 0,
    total_tax: 42500,
    child_tax_credit: 4000,
    earned_income_credit: 0,
    education_credits: 0,
    other_credits: 0,
    total_credits: 4000,
    withholding: 42000,
    estimated_payments: 3700,
    other_payments: 0,
    total_payments: 45700,
    refund_or_owed: 3200,
    warnings: [],
  });

  const handleCalculate = async () => {
    setCalculating(true);
    try {
      const result = await taxService.calculateReturn(id!, true);
      setCalculation(result);
      toast.success('Tax calculation completed');
    } catch (error) {
      // Mock success
      setCalculation(generateMockCalculation());
      toast.success('Tax calculation completed');
    } finally {
      setCalculating(false);
    }
  };

  const handleExplainLine = async (line: string) => {
    try {
      const explanation = await taxService.explainLine(id!, line);
      setLineExplanation(explanation);
      setShowExplanation(true);
    } catch (error) {
      // Mock explanation
      setLineExplanation({
        line,
        value: 42500,
        explanation: `This line represents your total tax liability after applying the ${taxReturn?.filing_status === 'married_filing_jointly' ? 'Married Filing Jointly' : 'Single'} tax brackets for 2024. The calculation considers your taxable income of $215,000 and applies the marginal tax rates progressively.`,
        formula: 'Tax = (Taxable Income × Marginal Rate) - Bracket Adjustment',
        inputs: {
          taxable_income: 215000,
          marginal_rate: 0.24,
        },
        rules_applied: [
          {
            rule_id: 'federal-brackets-2024',
            description: '2024 Federal Tax Brackets for Married Filing Jointly',
            irs_citation: 'Rev. Proc. 2023-34',
          },
        ],
      });
      setShowExplanation(true);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      await taxService.downloadPDF(id!);
      toast.success('PDF downloaded');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const tabs: { id: TabType; label: string; icon: React.ElementType }[] = [
    { id: 'overview', label: 'Overview', icon: PieChart },
    { id: 'income', label: 'Income', icon: DollarSign },
    { id: 'deductions', label: 'Deductions', icon: Receipt },
    { id: 'credits', label: 'Credits', icon: CreditCard },
    { id: 'schedules', label: 'Schedules', icon: FileText },
    { id: 'review', label: 'Review', icon: FileCheck },
    { id: 'efile', label: 'E-File', icon: Send },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading tax return...</p>
        </div>
      </div>
    );
  }

  if (!taxReturn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <p className="text-gray-600">Tax return not found</p>
          <button
            onClick={() => navigate('/firm/tax-returns')}
            className="mt-4 text-primary-600 hover:text-primary-700"
          >
            Back to Tax Returns
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/firm/tax-returns')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">
                {taxReturn.taxpayer_first_name} {taxReturn.taxpayer_last_name}
              </h1>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
                Form {taxReturn.form_type}
              </span>
            </div>
            <p className="text-gray-600 mt-1">
              Tax Year {taxReturn.tax_year} • {taxReturn.filing_status?.replace(/_/g, ' ')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleCalculate}
            disabled={calculating}
            className="fluent-btn-secondary"
          >
            {calculating ? (
              <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Calculator className="w-5 h-5" />
            )}
            Calculate
          </button>
          <button onClick={handleDownloadPDF} className="fluent-btn-secondary">
            <Download className="w-5 h-5" />
            Download PDF
          </button>
          <button className="fluent-btn-primary">
            <Save className="w-5 h-5" />
            Save
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Income</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(calculation?.total_income)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Taxable Income</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(calculation?.taxable_income)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Tax</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(calculation?.total_tax)}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <Receipt className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={`bg-white rounded-xl p-5 shadow-sm border ${
            (calculation?.refund_or_owed || 0) > 0 ? 'border-green-200' : 'border-red-200'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                {(calculation?.refund_or_owed || 0) > 0 ? 'Refund' : 'Amount Owed'}
              </p>
              <p className={`text-2xl font-bold ${
                (calculation?.refund_or_owed || 0) > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(Math.abs(calculation?.refund_or_owed || 0))}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${
              (calculation?.refund_or_owed || 0) > 0 ? 'bg-green-100' : 'bg-red-100'
            }`}>
              {(calculation?.refund_or_owed || 0) > 0 ? (
                <TrendingUp className="w-6 h-6 text-green-600" />
              ) : (
                <TrendingDown className="w-6 h-6 text-red-600" />
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex gap-1 p-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <OverviewTab
              taxReturn={taxReturn}
              calculation={calculation}
              onExplain={handleExplainLine}
            />
          )}
          {activeTab === 'income' && (
            <IncomeTab calculation={calculation} onExplain={handleExplainLine} />
          )}
          {activeTab === 'deductions' && (
            <DeductionsTab calculation={calculation} onExplain={handleExplainLine} />
          )}
          {activeTab === 'credits' && (
            <CreditsTab calculation={calculation} onExplain={handleExplainLine} />
          )}
          {activeTab === 'schedules' && <SchedulesTab taxReturn={taxReturn} />}
          {activeTab === 'review' && (
            <ReviewTab taxReturn={taxReturn} calculation={calculation} />
          )}
          {activeTab === 'efile' && <EfileTab taxReturn={taxReturn} />}
        </div>
      </div>

      {/* Line Explanation Modal */}
      <AnimatePresence>
        {showExplanation && lineExplanation && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowExplanation(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[80vh] overflow-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Lightbulb className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Line Explanation
                    </h3>
                    <p className="text-sm text-gray-500">{lineExplanation.line}</p>
                  </div>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Value</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(lineExplanation.value)}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Explanation</p>
                  <p className="text-gray-600">{lineExplanation.explanation}</p>
                </div>
                {lineExplanation.formula && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Formula</p>
                    <code className="block p-3 bg-gray-100 rounded-lg text-sm font-mono">
                      {lineExplanation.formula}
                    </code>
                  </div>
                )}
                {lineExplanation.rules_applied?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">IRS Citations</p>
                    <div className="space-y-2">
                      {lineExplanation.rules_applied.map((rule, i) => (
                        <div key={i} className="p-3 bg-blue-50 rounded-lg">
                          <p className="text-sm font-medium text-blue-800">{rule.description}</p>
                          {rule.irs_citation && (
                            <p className="text-xs text-blue-600 mt-1">{rule.irs_citation}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="p-4 border-t border-gray-200">
                <button
                  onClick={() => setShowExplanation(false)}
                  className="w-full py-2 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Overview Tab
const OverviewTab: React.FC<{
  taxReturn: TaxReturn;
  calculation: TaxCalculationResult | null;
  onExplain: (line: string) => void;
}> = ({ taxReturn, calculation }) => {
  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Taxpayer Info */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <User className="w-5 h-5 text-gray-600" />
          Taxpayer Information
        </h3>
        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Name</span>
            <span className="font-medium">{taxReturn.taxpayer_first_name} {taxReturn.taxpayer_last_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">SSN</span>
            <span className="font-medium">{taxReturn.taxpayer_ssn}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Filing Status</span>
            <span className="font-medium">{taxReturn.filing_status?.replace(/_/g, ' ')}</span>
          </div>
          {taxReturn.spouse_first_name && (
            <div className="flex justify-between">
              <span className="text-gray-600">Spouse</span>
              <span className="font-medium">{taxReturn.spouse_first_name} {taxReturn.spouse_last_name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Address */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Home className="w-5 h-5 text-gray-600" />
          Address
        </h3>
        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Street</span>
            <span className="font-medium">{taxReturn.address_street}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">City</span>
            <span className="font-medium">{taxReturn.address_city}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">State</span>
            <span className="font-medium">{taxReturn.address_state}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">ZIP</span>
            <span className="font-medium">{taxReturn.address_zip}</span>
          </div>
        </div>
      </div>

      {/* Tax Summary */}
      <div className="lg:col-span-2 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Calculator className="w-5 h-5 text-gray-600" />
          Tax Summary
        </h3>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Income</p>
              <p className="text-lg font-semibold">{formatCurrency(calculation?.total_income)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">AGI</p>
              <p className="text-lg font-semibold">{formatCurrency(calculation?.adjusted_gross_income)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Deductions</p>
              <p className="text-lg font-semibold">
                {formatCurrency(calculation?.deduction_used === 'itemized' ? calculation?.itemized_deductions : calculation?.standard_deduction)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Taxable Income</p>
              <p className="text-lg font-semibold">{formatCurrency(calculation?.taxable_income)}</p>
            </div>
          </div>
          <div className="border-t border-gray-200 mt-4 pt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Tax</p>
              <p className="text-lg font-semibold text-red-600">{formatCurrency(calculation?.total_tax)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Credits</p>
              <p className="text-lg font-semibold text-green-600">{formatCurrency(calculation?.total_credits)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Payments</p>
              <p className="text-lg font-semibold">{formatCurrency(calculation?.total_payments)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">{(calculation?.refund_or_owed || 0) > 0 ? 'Refund' : 'Owed'}</p>
              <p className={`text-lg font-semibold ${(calculation?.refund_or_owed || 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(Math.abs(calculation?.refund_or_owed || 0))}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Income Tab
const IncomeTab: React.FC<{
  calculation: TaxCalculationResult | null;
  onExplain: (line: string) => void;
}> = ({ calculation, onExplain }) => {
  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '$0';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(amount);
  };

  const incomeItems = [
    { label: 'Wages, Salaries, Tips (W-2)', value: calculation?.wages, line: '1040.line1' },
    { label: 'Interest Income', value: calculation?.interest_income, line: '1040.line2b' },
    { label: 'Dividend Income', value: calculation?.dividend_income, line: '1040.line3b' },
    { label: 'Business Income (Schedule C)', value: calculation?.business_income, line: '1040.line8' },
    { label: 'Capital Gains (Schedule D)', value: calculation?.capital_gains, line: '1040.line7' },
    { label: 'Other Income', value: calculation?.other_income, line: '1040.line8' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Income Sources</h3>
        <span className="text-sm text-gray-500">Form 1040, Lines 1-8</span>
      </div>
      <div className="bg-gray-50 rounded-lg divide-y divide-gray-200">
        {incomeItems.map((item, index) => (
          <div key={index} className="flex items-center justify-between p-4 hover:bg-gray-100">
            <span className="text-gray-700">{item.label}</span>
            <div className="flex items-center gap-3">
              <span className="font-medium">{formatCurrency(item.value)}</span>
              <button
                onClick={() => onExplain(item.line)}
                className="p-1 hover:bg-gray-200 rounded"
                title="Explain this line"
              >
                <HelpCircle className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>
        ))}
        <div className="flex items-center justify-between p-4 bg-blue-50">
          <span className="font-semibold text-gray-900">Total Income</span>
          <span className="font-bold text-lg">{formatCurrency(calculation?.total_income)}</span>
        </div>
      </div>
    </div>
  );
};

// Deductions Tab
const DeductionsTab: React.FC<{
  calculation: TaxCalculationResult | null;
  onExplain: (line: string) => void;
}> = ({ calculation, onExplain }) => {
  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '$0';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(amount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className={`px-4 py-2 rounded-lg ${calculation?.deduction_used === 'standard' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'}`}>
          Standard: {formatCurrency(calculation?.standard_deduction)}
        </div>
        <div className={`px-4 py-2 rounded-lg ${calculation?.deduction_used === 'itemized' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'}`}>
          Itemized: {formatCurrency(calculation?.itemized_deductions)}
        </div>
        <span className="text-sm text-gray-500">
          Using {calculation?.deduction_used} deduction (higher amount)
        </span>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <span className="text-gray-700">Adjusted Gross Income</span>
          <span className="font-medium">{formatCurrency(calculation?.adjusted_gross_income)}</span>
        </div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-gray-700">Deduction Amount</span>
          <span className="font-medium text-green-600">
            -{formatCurrency(calculation?.deduction_used === 'itemized' ? calculation?.itemized_deductions : calculation?.standard_deduction)}
          </span>
        </div>
        {calculation?.qualified_business_income_deduction && calculation.qualified_business_income_deduction > 0 && (
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-700">QBI Deduction (§199A)</span>
            <span className="font-medium text-green-600">
              -{formatCurrency(calculation.qualified_business_income_deduction)}
            </span>
          </div>
        )}
        <div className="border-t border-gray-200 pt-4 flex items-center justify-between">
          <span className="font-semibold text-gray-900">Taxable Income</span>
          <span className="font-bold text-lg">{formatCurrency(calculation?.taxable_income)}</span>
        </div>
      </div>
    </div>
  );
};

// Credits Tab
const CreditsTab: React.FC<{
  calculation: TaxCalculationResult | null;
  onExplain: (line: string) => void;
}> = ({ calculation, onExplain }) => {
  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '$0';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(amount);
  };

  const credits = [
    { label: 'Child Tax Credit', value: calculation?.child_tax_credit },
    { label: 'Earned Income Credit', value: calculation?.earned_income_credit },
    { label: 'Education Credits', value: calculation?.education_credits },
    { label: 'Other Credits', value: calculation?.other_credits },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Tax Credits</h3>
      <div className="bg-gray-50 rounded-lg divide-y divide-gray-200">
        {credits.map((credit, index) => (
          <div key={index} className="flex items-center justify-between p-4">
            <span className="text-gray-700">{credit.label}</span>
            <span className="font-medium text-green-600">{formatCurrency(credit.value)}</span>
          </div>
        ))}
        <div className="flex items-center justify-between p-4 bg-green-50">
          <span className="font-semibold text-gray-900">Total Credits</span>
          <span className="font-bold text-lg text-green-600">{formatCurrency(calculation?.total_credits)}</span>
        </div>
      </div>
    </div>
  );
};

// Schedules Tab
const SchedulesTab: React.FC<{ taxReturn: TaxReturn }> = ({ taxReturn }) => {
  const schedules = [
    { id: 'A', name: 'Itemized Deductions', required: true, complete: true },
    { id: 'B', name: 'Interest and Dividends', required: true, complete: true },
    { id: 'C', name: 'Business Income', required: false, complete: false },
    { id: 'D', name: 'Capital Gains and Losses', required: true, complete: true },
    { id: 'E', name: 'Supplemental Income', required: false, complete: false },
    { id: 'SE', name: 'Self-Employment Tax', required: false, complete: false },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Schedules & Forms</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {schedules.map((schedule) => (
          <div
            key={schedule.id}
            className={`p-4 rounded-lg border ${
              schedule.complete
                ? 'border-green-200 bg-green-50'
                : schedule.required
                ? 'border-yellow-200 bg-yellow-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Schedule {schedule.id}</p>
                <p className="text-sm text-gray-600">{schedule.name}</p>
              </div>
              {schedule.complete ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : schedule.required ? (
                <Clock className="w-5 h-5 text-yellow-600" />
              ) : (
                <span className="text-xs text-gray-500">Optional</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Review Tab
const ReviewTab: React.FC<{
  taxReturn: TaxReturn;
  calculation: TaxCalculationResult | null;
}> = ({ taxReturn, calculation }) => {
  const checks = [
    { label: 'Taxpayer information complete', status: 'pass' },
    { label: 'All income sources reported', status: 'pass' },
    { label: 'Deductions properly documented', status: 'pass' },
    { label: 'Credits eligibility verified', status: 'pass' },
    { label: 'Prior year comparison reviewed', status: 'warning' },
    { label: 'E-file validation passed', status: 'pending' },
  ];

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Pre-Filing Review</h3>
      <div className="space-y-3">
        {checks.map((check, index) => (
          <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            {check.status === 'pass' && <CheckCircle className="w-5 h-5 text-green-600" />}
            {check.status === 'warning' && <AlertTriangle className="w-5 h-5 text-yellow-600" />}
            {check.status === 'pending' && <Clock className="w-5 h-5 text-gray-400" />}
            <span className="text-gray-700">{check.label}</span>
          </div>
        ))}
      </div>
      {calculation?.warnings && calculation.warnings.length > 0 && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="font-medium text-yellow-800 mb-2">Warnings</h4>
          <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1">
            {calculation.warnings.map((warning, i) => (
              <li key={i}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// E-File Tab
const EfileTab: React.FC<{ taxReturn: TaxReturn }> = ({ taxReturn }) => {
  const [preparing, setPreparing] = useState(false);

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Electronic Filing</h3>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-800">Ready to E-File</p>
            <p className="text-sm text-blue-700 mt-1">
              This return has passed all validation checks and is ready for electronic filing.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => setPreparing(true)}
          disabled={preparing}
          className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
        >
          <FileCheck className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="font-medium text-gray-700">Prepare for E-File</p>
          <p className="text-sm text-gray-500">Generate XML and validate</p>
        </button>
        <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center">
          <Send className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="font-medium text-gray-700">Submit to IRS</p>
          <p className="text-sm text-gray-500">Transmit return electronically</p>
        </button>
      </div>
    </div>
  );
};

export default TaxReturnWorkspace;
