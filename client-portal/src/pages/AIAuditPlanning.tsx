/**
 * AI-Powered Audit Planning Dashboard
 * Comprehensive AI planning that exceeds human CPA capabilities
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import * as XLSX from 'xlsx';
import {
  ArrowLeft,
  Brain,
  Shield,
  AlertTriangle,
  TrendingUp,
  FileText,
  Calculator,
  Target,
  ChevronRight,
  ChevronDown,
  Check,
  Sparkles,
  BarChart3,
  Clock,
  Zap,
  RefreshCw,
  Download,
  Eye,
  CheckCircle2,
  XCircle,
  Upload,
  FileSpreadsheet,
  Link2,
  Edit3,
  DollarSign,
  Info,
  X,
} from 'lucide-react';
import {
  auditPlanningService,
  AIRiskAnalysisResponse,
  AIMaterialityResponse,
  AIFraudDetectionResponse,
  AIAuditProgramResponse,
  AIPlanningMemoResponse,
} from '../services/audit-planning.service';
import { engagementService, Engagement } from '../services/engagement.service';
import { clientService } from '../services/client.service';
import toast from 'react-hot-toast';

interface FinancialData {
  total_assets: number;
  total_liabilities: number;
  current_assets: number;
  current_liabilities: number;
  total_revenue: number;
  net_income: number;
  pretax_income: number;
  total_equity: number;
  inventory: number;
  accounts_receivable: number;
  cost_of_goods_sold: number;
  operating_expenses: number;
  allowance_doubtful: number;
}

const emptyFinancialData: FinancialData = {
  total_assets: 0,
  total_liabilities: 0,
  current_assets: 0,
  current_liabilities: 0,
  total_revenue: 0,
  net_income: 0,
  pretax_income: 0,
  total_equity: 0,
  inventory: 0,
  accounts_receivable: 0,
  cost_of_goods_sold: 0,
  operating_expenses: 0,
  allowance_doubtful: 0,
};

type DataSourceType = 'manual' | 'upload' | 'quickbooks' | 'xero' | 'sage';

const dataSourceOptions = [
  { id: 'manual', name: 'Manual Entry', icon: Edit3, description: 'Enter financial data manually' },
  { id: 'upload', name: 'Upload File', icon: Upload, description: 'Upload Excel, CSV, or PDF trial balance' },
  { id: 'quickbooks', name: 'QuickBooks', icon: Link2, description: 'Connect to QuickBooks Online' },
  { id: 'xero', name: 'Xero', icon: Link2, description: 'Connect to Xero accounting' },
  { id: 'sage', name: 'Sage', icon: Link2, description: 'Connect to Sage Intacct' },
];

const fieldLabels: Record<keyof FinancialData, string> = {
  total_assets: 'Total Assets',
  total_liabilities: 'Total Liabilities',
  current_assets: 'Current Assets',
  current_liabilities: 'Current Liabilities',
  total_revenue: 'Total Revenue',
  net_income: 'Net Income',
  pretax_income: 'Pre-Tax Income',
  total_equity: 'Total Equity',
  inventory: 'Inventory',
  accounts_receivable: 'Accounts Receivable',
  cost_of_goods_sold: 'Cost of Goods Sold',
  operating_expenses: 'Operating Expenses',
  allowance_doubtful: 'Allowance for Doubtful Accounts',
};

const AIAuditPlanning: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // State
  const [engagement, setEngagement] = useState<Engagement | null>(null);
  const [clientName, setClientName] = useState('');
  const [industry, setIndustry] = useState('manufacturing');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'risk' | 'materiality' | 'fraud' | 'programs' | 'memo'>('risk');
  const [financialData, setFinancialData] = useState<FinancialData>(emptyFinancialData);
  const [showFinancialForm, setShowFinancialForm] = useState(true);

  // Data source state
  const [dataSource, setDataSource] = useState<DataSourceType>('manual');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);

  // AI Results
  const [riskAnalysis, setRiskAnalysis] = useState<AIRiskAnalysisResponse | null>(null);
  const [materialityResult, setMaterialityResult] = useState<AIMaterialityResponse | null>(null);
  const [fraudDetection, setFraudDetection] = useState<AIFraudDetectionResponse | null>(null);
  const [auditPrograms, setAuditPrograms] = useState<AIAuditProgramResponse[]>([]);
  const [planningMemo, setPlanningMemo] = useState<AIPlanningMemoResponse | null>(null);

  // Loading states
  const [analyzingRisk, setAnalyzingRisk] = useState(false);
  const [calculatingMateriality, setCalculatingMateriality] = useState(false);
  const [detectingFraud, setDetectingFraud] = useState(false);
  const [generatingPrograms, setGeneratingPrograms] = useState(false);
  const [generatingMemo, setGeneratingMemo] = useState(false);

  const industries = [
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'technology', label: 'Technology' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'retail', label: 'Retail' },
    { value: 'financial_services', label: 'Financial Services' },
    { value: 'default', label: 'Other' },
  ];

  useEffect(() => {
    if (id) {
      loadEngagement(id);
    }
  }, [id]);

  const loadEngagement = async (engagementId: string) => {
    try {
      setLoading(true);
      const eng = await engagementService.getEngagement(engagementId);
      setEngagement(eng);

      // Try to load client name
      if (eng.client_id) {
        try {
          const client = await clientService.getClient(eng.client_id);
          setClientName(client.name || eng.client_id);
        } catch {
          setClientName(eng.client_id);
        }
      }
    } catch (error) {
      console.error('Failed to load engagement:', error);
      toast.error('Failed to load engagement');
      navigate('/firm/audits');
    } finally {
      setLoading(false);
    }
  };

  // File upload handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // xlsx
      'application/vnd.ms-excel', // xls
      'text/csv',
      'application/pdf',
    ];

    if (!validTypes.includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      toast.error('Please upload an Excel, CSV, or PDF file');
      return;
    }

    setUploadedFile(file);
    setIsProcessingFile(true);
    setUploadProgress(0);

    try {
      // Simulate file processing with progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadProgress(i);
      }

      // Parse the file to extract financial data
      const extractedData = await parseFinancialFile(file);
      setFinancialData(extractedData);
      setDataLoaded(true);
      toast.success(`Financial data extracted from ${file.name}`);
    } catch (error) {
      console.error('File processing error:', error);
      toast.error('Failed to process file. Please check the format.');
    } finally {
      setIsProcessingFile(false);
    }
  };

  const parseFinancialFile = async (file: File): Promise<FinancialData> => {
    // For CSV files, parse directly
    if (file.name.endsWith('.csv')) {
      const text = await file.text();
      return parseCSVData(text);
    }

    // For Excel files, use xlsx library to parse
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const data = e.target?.result;
            const workbook = XLSX.read(data, { type: 'binary' });

            // Get the first sheet
            const sheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[sheetName];

            // Convert to JSON - array of rows
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as (string | number)[][];

            // Parse the Excel data to extract financial values
            const extractedData = parseExcelData(jsonData);
            resolve(extractedData);
          } catch (error) {
            console.error('Excel parsing error:', error);
            reject(error);
          }
        };
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsBinaryString(file);
      });
    }

    // For PDF files, we'd need backend processing - show a message
    if (file.name.endsWith('.pdf')) {
      toast.error('PDF parsing requires backend processing. Please use Excel or CSV format.');
      return emptyFinancialData;
    }

    return emptyFinancialData;
  };

  // Parse Excel data (array of rows) into FinancialData
  const parseExcelData = (rows: (string | number)[][]): FinancialData => {
    const data: FinancialData = { ...emptyFinancialData };

    // Extended field mappings for balance sheets and trial balances
    const fieldMappings: Record<string, keyof FinancialData> = {
      // Total Assets variations
      'total assets': 'total_assets',
      'assets total': 'total_assets',
      'total asset': 'total_assets',
      'assets': 'total_assets',
      'sum of assets': 'total_assets',

      // Total Liabilities variations
      'total liabilities': 'total_liabilities',
      'liabilities total': 'total_liabilities',
      'total liability': 'total_liabilities',
      'liabilities': 'total_liabilities',
      'sum of liabilities': 'total_liabilities',

      // Current Assets variations
      'current assets': 'current_assets',
      'total current assets': 'current_assets',
      'current assets total': 'current_assets',

      // Current Liabilities variations
      'current liabilities': 'current_liabilities',
      'total current liabilities': 'current_liabilities',
      'current liabilities total': 'current_liabilities',

      // Revenue variations
      'revenue': 'total_revenue',
      'total revenue': 'total_revenue',
      'revenues': 'total_revenue',
      'net revenue': 'total_revenue',
      'net revenues': 'total_revenue',
      'sales': 'total_revenue',
      'net sales': 'total_revenue',
      'total sales': 'total_revenue',
      'gross sales': 'total_revenue',
      'service revenue': 'total_revenue',
      'operating revenue': 'total_revenue',

      // Net Income variations
      'net income': 'net_income',
      'net profit': 'net_income',
      'net earnings': 'net_income',
      'net income (loss)': 'net_income',
      'profit (loss)': 'net_income',
      'profit': 'net_income',
      'earnings': 'net_income',
      'bottom line': 'net_income',

      // Pre-tax Income variations
      'pretax income': 'pretax_income',
      'pre-tax income': 'pretax_income',
      'income before tax': 'pretax_income',
      'income before taxes': 'pretax_income',
      'earnings before tax': 'pretax_income',
      'ebt': 'pretax_income',
      'income before income tax': 'pretax_income',
      'profit before tax': 'pretax_income',

      // Equity variations
      'equity': 'total_equity',
      'total equity': 'total_equity',
      'stockholders equity': 'total_equity',
      "stockholders' equity": 'total_equity',
      'shareholders equity': 'total_equity',
      "shareholders' equity": 'total_equity',
      'owners equity': 'total_equity',
      "owner's equity": 'total_equity',
      'net worth': 'total_equity',
      'total stockholders equity': 'total_equity',
      'total shareholders equity': 'total_equity',
      'capital': 'total_equity',

      // Inventory variations
      'inventory': 'inventory',
      'inventories': 'inventory',
      'merchandise inventory': 'inventory',
      'finished goods': 'inventory',
      'raw materials': 'inventory',
      'work in progress': 'inventory',
      'stock': 'inventory',

      // Accounts Receivable variations
      'accounts receivable': 'accounts_receivable',
      'receivables': 'accounts_receivable',
      'trade receivables': 'accounts_receivable',
      'a/r': 'accounts_receivable',
      'ar': 'accounts_receivable',
      'net receivables': 'accounts_receivable',
      'accounts receivable net': 'accounts_receivable',
      'trade accounts receivable': 'accounts_receivable',
      'customer receivables': 'accounts_receivable',

      // COGS variations
      'cost of goods sold': 'cost_of_goods_sold',
      'cogs': 'cost_of_goods_sold',
      'cost of sales': 'cost_of_goods_sold',
      'cost of revenue': 'cost_of_goods_sold',
      'cost of products sold': 'cost_of_goods_sold',
      'cost of services': 'cost_of_goods_sold',
      'direct costs': 'cost_of_goods_sold',

      // Operating Expenses variations
      'operating expenses': 'operating_expenses',
      'opex': 'operating_expenses',
      'total operating expenses': 'operating_expenses',
      'operating costs': 'operating_expenses',
      'sg&a': 'operating_expenses',
      'sga': 'operating_expenses',
      'selling general administrative': 'operating_expenses',
      'general and administrative': 'operating_expenses',

      // Allowance for Doubtful Accounts variations
      'allowance for doubtful accounts': 'allowance_doubtful',
      'allowance for bad debts': 'allowance_doubtful',
      'allowance doubtful': 'allowance_doubtful',
      'bad debt reserve': 'allowance_doubtful',
      'provision for bad debts': 'allowance_doubtful',
    };

    // Helper to clean and parse numeric values
    const parseNumericValue = (val: string | number | undefined): number => {
      if (val === undefined || val === null || val === '') return 0;
      if (typeof val === 'number') return Math.abs(val);

      // Remove currency symbols, commas, parentheses (for negatives), spaces
      const cleaned = String(val)
        .replace(/[$€£¥,\s]/g, '')
        .replace(/\(([^)]+)\)/g, '-$1') // Convert (123) to -123
        .trim();

      const num = parseFloat(cleaned);
      return isNaN(num) ? 0 : Math.abs(num);
    };

    // Process each row looking for label-value pairs
    for (const row of rows) {
      if (!row || row.length < 2) continue;

      // Try different column arrangements
      // Format 1: [Label, Value] or [Label, ..., Value]
      // Format 2: [AccountNumber, Label, Value]
      // Format 3: [Label, Debit, Credit]

      for (let colIdx = 0; colIdx < row.length - 1; colIdx++) {
        const cell = row[colIdx];
        if (typeof cell !== 'string') continue;

        const label = cell.toLowerCase().trim();
        if (!label) continue;

        // Check if this label matches any field mapping
        for (const [pattern, field] of Object.entries(fieldMappings)) {
          if (label === pattern || label.includes(pattern)) {
            // Look for a numeric value in subsequent columns
            for (let valIdx = colIdx + 1; valIdx < row.length; valIdx++) {
              const value = parseNumericValue(row[valIdx]);
              if (value > 0) {
                // Only update if we haven't found a value for this field yet,
                // or if this value is from a more specific match
                if (data[field] === 0 || label === pattern) {
                  data[field] = value;
                }
                break;
              }
            }
            break;
          }
        }
      }
    }

    return data;
  };

  const parseCSVData = (csvText: string): FinancialData => {
    const lines = csvText.trim().split('\n');
    const data: FinancialData = { ...emptyFinancialData };

    // Extended field mappings for CSV balance sheets and trial balances
    const fieldMappings: Record<string, keyof FinancialData> = {
      // Total Assets variations
      'total assets': 'total_assets',
      'assets total': 'total_assets',
      'total asset': 'total_assets',
      'sum of assets': 'total_assets',

      // Total Liabilities variations
      'total liabilities': 'total_liabilities',
      'liabilities total': 'total_liabilities',
      'total liability': 'total_liabilities',
      'sum of liabilities': 'total_liabilities',

      // Current Assets variations
      'current assets': 'current_assets',
      'total current assets': 'current_assets',
      'current assets total': 'current_assets',

      // Current Liabilities variations
      'current liabilities': 'current_liabilities',
      'total current liabilities': 'current_liabilities',
      'current liabilities total': 'current_liabilities',

      // Revenue variations
      'revenue': 'total_revenue',
      'total revenue': 'total_revenue',
      'revenues': 'total_revenue',
      'net revenue': 'total_revenue',
      'net revenues': 'total_revenue',
      'sales': 'total_revenue',
      'net sales': 'total_revenue',
      'total sales': 'total_revenue',
      'gross sales': 'total_revenue',
      'service revenue': 'total_revenue',
      'operating revenue': 'total_revenue',

      // Net Income variations
      'net income': 'net_income',
      'net profit': 'net_income',
      'net earnings': 'net_income',
      'net income (loss)': 'net_income',
      'profit (loss)': 'net_income',
      'profit': 'net_income',
      'earnings': 'net_income',

      // Pre-tax Income variations
      'pretax income': 'pretax_income',
      'pre-tax income': 'pretax_income',
      'income before tax': 'pretax_income',
      'income before taxes': 'pretax_income',
      'earnings before tax': 'pretax_income',
      'ebt': 'pretax_income',
      'income before income tax': 'pretax_income',
      'profit before tax': 'pretax_income',

      // Equity variations
      'equity': 'total_equity',
      'total equity': 'total_equity',
      'stockholders equity': 'total_equity',
      "stockholders' equity": 'total_equity',
      'shareholders equity': 'total_equity',
      "shareholders' equity": 'total_equity',
      'owners equity': 'total_equity',
      "owner's equity": 'total_equity',
      'net worth': 'total_equity',
      'total stockholders equity': 'total_equity',
      'total shareholders equity': 'total_equity',
      'capital': 'total_equity',

      // Inventory variations
      'inventory': 'inventory',
      'inventories': 'inventory',
      'merchandise inventory': 'inventory',
      'finished goods': 'inventory',
      'raw materials': 'inventory',
      'work in progress': 'inventory',
      'stock': 'inventory',

      // Accounts Receivable variations
      'accounts receivable': 'accounts_receivable',
      'receivables': 'accounts_receivable',
      'trade receivables': 'accounts_receivable',
      'a/r': 'accounts_receivable',
      'ar': 'accounts_receivable',
      'net receivables': 'accounts_receivable',
      'accounts receivable net': 'accounts_receivable',
      'trade accounts receivable': 'accounts_receivable',
      'customer receivables': 'accounts_receivable',

      // COGS variations
      'cost of goods sold': 'cost_of_goods_sold',
      'cogs': 'cost_of_goods_sold',
      'cost of sales': 'cost_of_goods_sold',
      'cost of revenue': 'cost_of_goods_sold',
      'cost of products sold': 'cost_of_goods_sold',
      'cost of services': 'cost_of_goods_sold',
      'direct costs': 'cost_of_goods_sold',

      // Operating Expenses variations
      'operating expenses': 'operating_expenses',
      'opex': 'operating_expenses',
      'total operating expenses': 'operating_expenses',
      'operating costs': 'operating_expenses',
      'sg&a': 'operating_expenses',
      'sga': 'operating_expenses',
      'selling general administrative': 'operating_expenses',
      'general and administrative': 'operating_expenses',

      // Allowance for Doubtful Accounts variations
      'allowance for doubtful accounts': 'allowance_doubtful',
      'allowance for bad debts': 'allowance_doubtful',
      'allowance doubtful': 'allowance_doubtful',
      'bad debt reserve': 'allowance_doubtful',
      'provision for bad debts': 'allowance_doubtful',
    };

    // Helper to parse numeric values from CSV cells
    const parseNumericValue = (val: string | undefined): number => {
      if (!val) return 0;
      // Remove currency symbols, commas, parentheses, spaces
      const cleaned = val
        .replace(/[$€£¥,\s]/g, '')
        .replace(/\(([^)]+)\)/g, '-$1')
        .trim();
      const num = parseFloat(cleaned);
      return isNaN(num) ? 0 : Math.abs(num);
    };

    lines.forEach(line => {
      // Handle quoted CSV values and various delimiters
      const parts = line.split(/[,\t;]/).map(p => p.replace(/^["']|["']$/g, '').trim());

      if (parts.length >= 2) {
        const label = parts[0].toLowerCase();

        // Find the best matching field
        for (const [pattern, field] of Object.entries(fieldMappings)) {
          if (label === pattern || label.includes(pattern)) {
            // Look for numeric value in any subsequent column
            for (let i = 1; i < parts.length; i++) {
              const value = parseNumericValue(parts[i]);
              if (value > 0) {
                // Prefer exact matches over partial matches
                if (data[field] === 0 || label === pattern) {
                  data[field] = value;
                }
                break;
              }
            }
            break;
          }
        }
      }
    });

    return data;
  };

  const handleConnectAccounting = (provider: DataSourceType) => {
    // In production, this would initiate OAuth flow
    toast.error(`${provider.charAt(0).toUpperCase() + provider.slice(1)} integration coming soon! Please use manual entry or file upload for now.`);
  };

  const formatInputCurrency = (value: number): string => {
    if (value === 0) return '';
    return value.toLocaleString('en-US');
  };

  const parseInputCurrency = (value: string): number => {
    return parseFloat(value.replace(/,/g, '')) || 0;
  };

  const handleFinancialInputChange = (field: keyof FinancialData, value: string) => {
    const numericValue = parseInputCurrency(value);
    setFinancialData(prev => ({ ...prev, [field]: numericValue }));
    setDataLoaded(true);
  };

  const clearUploadedFile = () => {
    setUploadedFile(null);
    setUploadProgress(0);
    setFinancialData(emptyFinancialData);
    setDataLoaded(false);
  };

  const isDataValid = (): boolean => {
    return financialData.total_assets > 0 && financialData.total_revenue > 0;
  };

  const handleAnalyzeRisk = async () => {
    if (!id || !engagement) return;

    setAnalyzingRisk(true);
    try {
      const result = await auditPlanningService.analyzeRiskWithAI({
        engagement_id: id,
        client_name: clientName || engagement.name,
        industry,
        financial_data: financialData,
        prior_year_data: undefined,
        known_issues: [],
      });
      setRiskAnalysis(result);
      toast.success('AI Risk Analysis Complete');
      setShowFinancialForm(false);
    } catch (error: any) {
      console.error('Risk analysis failed:', error);
      toast.error(error.response?.data?.detail || 'Risk analysis failed');
    } finally {
      setAnalyzingRisk(false);
    }
  };

  const handleCalculateMateriality = async () => {
    setCalculatingMateriality(true);
    try {
      const result = await auditPlanningService.calculateMaterialityWithAI({
        financial_data: financialData,
        industry,
        entity_type: 'private',
        risk_factors: riskAnalysis?.recommended_focus_areas?.map(f => f.area) || [],
        user_count: 0,
      });
      setMaterialityResult(result);
      toast.success('AI Materiality Calculation Complete');
    } catch (error: any) {
      console.error('Materiality calculation failed:', error);
      toast.error(error.response?.data?.detail || 'Materiality calculation failed');
    } finally {
      setCalculatingMateriality(false);
    }
  };

  const handleDetectFraud = async () => {
    if (!id) return;

    setDetectingFraud(true);
    try {
      const result = await auditPlanningService.detectFraudWithAI({
        engagement_id: id,
        financial_data: financialData,
      });
      setFraudDetection(result);
      toast.success('AI Fraud Detection Complete');
    } catch (error: any) {
      console.error('Fraud detection failed:', error);
      toast.error(error.response?.data?.detail || 'Fraud detection failed');
    } finally {
      setDetectingFraud(false);
    }
  };

  const handleGeneratePrograms = async () => {
    if (!id || !riskAnalysis || !materialityResult) {
      toast.error('Please complete risk analysis and materiality calculation first');
      return;
    }

    setGeneratingPrograms(true);
    try {
      const areas = ['revenue', 'receivables', 'inventory', 'payables'];
      const programs: AIAuditProgramResponse[] = [];

      for (const area of areas) {
        const result = await auditPlanningService.generateAuditProgramWithAI({
          engagement_id: id,
          risk_assessment: riskAnalysis,
          audit_area: area,
          account_balance: getAccountBalance(area),
          materiality: materialityResult.overall_materiality,
          prior_year_findings: [],
        });
        programs.push(result);
      }

      setAuditPrograms(programs);
      toast.success(`Generated ${programs.length} AI-powered audit programs`);
    } catch (error: any) {
      console.error('Program generation failed:', error);
      toast.error(error.response?.data?.detail || 'Program generation failed');
    } finally {
      setGeneratingPrograms(false);
    }
  };

  const handleGenerateMemo = async () => {
    if (!id || !engagement || !riskAnalysis || !materialityResult || !fraudDetection) {
      toast.error('Please complete all analyses first');
      return;
    }

    setGeneratingMemo(true);
    try {
      const result = await auditPlanningService.generatePlanningMemoWithAI({
        engagement_id: id,
        client_name: clientName || engagement.name,
        risk_assessment: riskAnalysis,
        materiality: materialityResult,
        fraud_assessment: fraudDetection,
        audit_programs: auditPrograms,
      });
      setPlanningMemo(result);
      toast.success('Planning Memo Generated');
    } catch (error: any) {
      console.error('Memo generation failed:', error);
      toast.error(error.response?.data?.detail || 'Memo generation failed');
    } finally {
      setGeneratingMemo(false);
    }
  };

  const getAccountBalance = (area: string): number => {
    switch (area) {
      case 'revenue': return financialData.total_revenue;
      case 'receivables': return financialData.accounts_receivable;
      case 'inventory': return financialData.inventory;
      case 'payables': return financialData.total_liabilities * 0.3;
      default: return 1000000;
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getRiskColor = (level: string): string => {
    switch (level?.toLowerCase()) {
      case 'significant': return 'error';
      case 'high': return 'error';
      case 'moderate': return 'warning';
      case 'low': return 'success';
      default: return 'neutral';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading AI Planning...</p>
        </div>
      </div>
    );
  }

  if (!engagement) return null;

  const tabs = [
    { id: 'risk', label: 'Risk Analysis', icon: Shield, completed: !!riskAnalysis },
    { id: 'materiality', label: 'Materiality', icon: Calculator, completed: !!materialityResult },
    { id: 'fraud', label: 'Fraud Detection', icon: AlertTriangle, completed: !!fraudDetection },
    { id: 'programs', label: 'Audit Programs', icon: FileText, completed: auditPrograms.length > 0 },
    { id: 'memo', label: 'Planning Memo', icon: FileText, completed: !!planningMemo },
  ];

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <button
          onClick={() => navigate(`/firm/engagements/${id}`)}
          className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-neutral-700" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <Brain className="w-6 h-6 text-primary-600" />
            <h1 className="text-display text-neutral-900">AI-Powered Audit Planning</h1>
            <span className="px-2 py-0.5 bg-primary-100 text-primary-700 text-caption font-medium rounded-full">
              Superior to Human CPA
            </span>
          </div>
          <p className="text-body text-neutral-600">{engagement.name} - {clientName}</p>
        </div>
      </motion.div>

      {/* Progress Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-4"
      >
        <div className="flex items-center justify-between gap-2 overflow-x-auto">
          {tabs.map((tab, index) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const isCompleted = tab.completed;

            return (
              <React.Fragment key={tab.id}>
                <button
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-fluent transition-all min-w-fit ${
                    isActive
                      ? 'bg-primary-500 text-white'
                      : isCompleted
                      ? 'bg-success-100 text-success-700 hover:bg-success-200'
                      : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    isActive ? 'bg-white/20' : isCompleted ? 'bg-success-500 text-white' : 'bg-neutral-200'
                  }`}>
                    {isCompleted && !isActive ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Icon className="w-4 h-4" />
                    )}
                  </div>
                  <span className="text-body-strong whitespace-nowrap">{tab.label}</span>
                </button>
                {index < tabs.length - 1 && (
                  <ChevronRight className="w-5 h-5 text-neutral-400 flex-shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Financial Data Input */}
          <AnimatePresence mode="wait">
            {showFinancialForm && activeTab === 'risk' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="fluent-card p-6"
              >
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-title text-neutral-900">Financial Data Input</h2>
                    <p className="text-caption text-neutral-600">
                      Import financial data to power AI analysis
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {dataLoaded && (
                      <span className="flex items-center gap-1 px-2 py-1 bg-success-100 text-success-700 text-caption rounded">
                        <CheckCircle2 className="w-3 h-3" />
                        Data Loaded
                      </span>
                    )}
                    <button
                      onClick={() => setShowFinancialForm(false)}
                      className="text-caption text-neutral-500 hover:text-neutral-700"
                    >
                      Collapse
                    </button>
                  </div>
                </div>

                {/* Data Source Selector */}
                <div className="mb-6">
                  <label className="block text-body-strong text-neutral-700 mb-3">
                    Choose Data Source
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {dataSourceOptions.map((option) => {
                      const Icon = option.icon;
                      const isSelected = dataSource === option.id;
                      return (
                        <button
                          key={option.id}
                          onClick={() => {
                            setDataSource(option.id as DataSourceType);
                            if (option.id !== 'manual' && option.id !== 'upload') {
                              handleConnectAccounting(option.id as DataSourceType);
                            }
                          }}
                          className={`flex flex-col items-center gap-2 p-4 rounded-fluent border-2 transition-all ${
                            isSelected
                              ? 'border-primary-500 bg-primary-50'
                              : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
                          }`}
                        >
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            isSelected ? 'bg-primary-500 text-white' : 'bg-neutral-100 text-neutral-600'
                          }`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <span className={`text-caption font-medium ${
                            isSelected ? 'text-primary-700' : 'text-neutral-700'
                          }`}>
                            {option.name}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* File Upload Section */}
                {dataSource === 'upload' && (
                  <div className="mb-6">
                    <div
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      className={`border-2 border-dashed rounded-fluent p-8 text-center transition-all ${
                        isDragging
                          ? 'border-primary-500 bg-primary-50'
                          : uploadedFile
                          ? 'border-success-500 bg-success-50'
                          : 'border-neutral-300 hover:border-primary-400 hover:bg-neutral-50'
                      }`}
                    >
                      {isProcessingFile ? (
                        <div className="space-y-3">
                          <RefreshCw className="w-8 h-8 text-primary-500 mx-auto animate-spin" />
                          <p className="text-body text-neutral-700">Processing {uploadedFile?.name}...</p>
                          <div className="w-48 h-2 bg-neutral-200 rounded-full mx-auto overflow-hidden">
                            <div
                              className="h-full bg-primary-500 transition-all duration-300"
                              style={{ width: `${uploadProgress}%` }}
                            />
                          </div>
                          <p className="text-caption text-neutral-500">{uploadProgress}% complete</p>
                        </div>
                      ) : uploadedFile ? (
                        <div className="space-y-3">
                          <div className="w-12 h-12 rounded-full bg-success-100 flex items-center justify-center mx-auto">
                            <FileSpreadsheet className="w-6 h-6 text-success-600" />
                          </div>
                          <div>
                            <p className="text-body-strong text-neutral-900">{uploadedFile.name}</p>
                            <p className="text-caption text-neutral-500">
                              {(uploadedFile.size / 1024).toFixed(1)} KB - Financial data extracted
                            </p>
                          </div>
                          <button
                            onClick={clearUploadedFile}
                            className="inline-flex items-center gap-1 text-caption text-error-600 hover:text-error-700"
                          >
                            <X className="w-3 h-3" />
                            Remove file
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center mx-auto">
                            <Upload className="w-6 h-6 text-neutral-500" />
                          </div>
                          <div>
                            <p className="text-body-strong text-neutral-900">
                              Drag & drop your trial balance
                            </p>
                            <p className="text-caption text-neutral-500">
                              or click to browse - Excel, CSV, or PDF
                            </p>
                          </div>
                          <input
                            type="file"
                            accept=".xlsx,.xls,.csv,.pdf"
                            onChange={handleFileSelect}
                            className="hidden"
                            id="file-upload"
                          />
                          <label
                            htmlFor="file-upload"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-fluent cursor-pointer hover:bg-primary-600 transition-colors"
                          >
                            <FileSpreadsheet className="w-4 h-4" />
                            Select File
                          </label>
                        </div>
                      )}
                    </div>
                    <div className="mt-2 flex items-center gap-2 text-caption text-neutral-500">
                      <Info className="w-3 h-3" />
                      Supports QuickBooks export, Excel trial balance, or any CSV with financial data
                    </div>
                  </div>
                )}

                {/* Industry Selection */}
                <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Industry Classification
                    </label>
                    <select
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      className="fluent-input w-full"
                    >
                      {industries.map((ind) => (
                        <option key={ind.value} value={ind.value}>{ind.label}</option>
                      ))}
                    </select>
                    <p className="text-caption text-neutral-500 mt-1">
                      Used for industry-specific benchmarks and risk factors
                    </p>
                  </div>
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Client Name
                    </label>
                    <input
                      type="text"
                      value={clientName}
                      onChange={(e) => setClientName(e.target.value)}
                      placeholder="Enter client name"
                      className="fluent-input w-full"
                    />
                  </div>
                </div>

                {/* Manual Entry Fields */}
                {(dataSource === 'manual' || dataLoaded) && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-body-strong text-neutral-900">
                        {dataSource === 'upload' ? 'Extracted Financial Data' : 'Enter Financial Data'}
                      </h3>
                      {dataSource === 'upload' && (
                        <span className="text-caption text-neutral-500">
                          Edit values if needed
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {(Object.entries(financialData) as [keyof FinancialData, number][]).map(([key, value]) => (
                        <div key={key} className="relative">
                          <label className="block text-caption text-neutral-600 mb-1">
                            {fieldLabels[key]}
                          </label>
                          <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
                              <DollarSign className="w-4 h-4" />
                            </span>
                            <input
                              type="text"
                              value={formatInputCurrency(value)}
                              onChange={(e) => handleFinancialInputChange(key, e.target.value)}
                              placeholder="0"
                              className="fluent-input w-full pl-9 text-right font-mono"
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Data Summary */}
                    {dataLoaded && (
                      <div className="mt-4 p-4 bg-neutral-50 rounded-fluent">
                        <h4 className="text-caption font-medium text-neutral-700 mb-2">Quick Summary</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-neutral-500">Total Assets:</span>
                            <span className="ml-2 font-medium">{formatCurrency(financialData.total_assets)}</span>
                          </div>
                          <div>
                            <span className="text-neutral-500">Revenue:</span>
                            <span className="ml-2 font-medium">{formatCurrency(financialData.total_revenue)}</span>
                          </div>
                          <div>
                            <span className="text-neutral-500">Net Income:</span>
                            <span className="ml-2 font-medium">{formatCurrency(financialData.net_income)}</span>
                          </div>
                          <div>
                            <span className="text-neutral-500">Equity:</span>
                            <span className="ml-2 font-medium">{formatCurrency(financialData.total_equity)}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Validation Warning */}
                {!isDataValid() && dataSource === 'manual' && (
                  <div className="mt-4 p-3 bg-warning-50 border border-warning-200 rounded-fluent flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-warning-600 mt-0.5" />
                    <div>
                      <p className="text-caption font-medium text-warning-800">
                        Missing Required Data
                      </p>
                      <p className="text-caption text-warning-700">
                        Please enter Total Assets and Total Revenue at minimum to run AI analysis.
                      </p>
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Risk Analysis Tab */}
          {activeTab === 'risk' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div className="fluent-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-title text-neutral-900">AI Risk Analysis</h2>
                    <p className="text-body text-neutral-600">
                      Pattern recognition across industry benchmarks with fraud indicator detection
                    </p>
                  </div>
                  <button
                    onClick={handleAnalyzeRisk}
                    disabled={analyzingRisk || !isDataValid()}
                    className="fluent-btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {analyzingRisk ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4" />
                        {riskAnalysis ? 'Re-analyze' : 'Analyze Risk'}
                      </>
                    )}
                  </button>
                </div>

                {riskAnalysis && (
                  <div className="space-y-6">
                    {/* Risk Score */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-neutral-50 rounded-fluent">
                        <p className="text-caption text-neutral-600 mb-1">Overall Risk Score</p>
                        <p className="text-2xl font-bold text-neutral-900">{riskAnalysis.overall_risk_score}/100</p>
                      </div>
                      <div className="p-4 bg-neutral-50 rounded-fluent">
                        <p className="text-caption text-neutral-600 mb-1">Risk Level</p>
                        <span className={`inline-flex px-3 py-1 rounded-full text-body-strong bg-${getRiskColor(riskAnalysis.risk_level)}-100 text-${getRiskColor(riskAnalysis.risk_level)}-700`}>
                          {riskAnalysis.risk_level?.toUpperCase()}
                        </span>
                      </div>
                      <div className="p-4 bg-neutral-50 rounded-fluent">
                        <p className="text-caption text-neutral-600 mb-1">Fraud Risk</p>
                        <span className={`inline-flex px-3 py-1 rounded-full text-body-strong bg-${getRiskColor(riskAnalysis.fraud_risk_assessment?.fraud_risk_level)}-100 text-${getRiskColor(riskAnalysis.fraud_risk_assessment?.fraud_risk_level)}-700`}>
                          {riskAnalysis.fraud_risk_assessment?.fraud_risk_level?.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {/* AI Insights */}
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-primary-500" />
                        AI-Generated Insights
                      </h3>
                      <div className="space-y-2">
                        {riskAnalysis.ai_insights?.map((insight, index) => (
                          <div
                            key={index}
                            className={`p-3 rounded-fluent border-l-4 border-${getRiskColor(insight.severity)}-500 bg-${getRiskColor(insight.severity)}-50`}
                          >
                            <p className="text-body-strong text-neutral-900">{insight.insight}</p>
                            <p className="text-caption text-neutral-600 mt-1">{insight.action}</p>
                            <p className="text-caption text-neutral-500 mt-1">Ref: {insight.pcaob_reference}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Significant Accounts */}
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3">Significant Accounts</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-neutral-100">
                            <tr>
                              <th className="text-left p-3">Account</th>
                              <th className="text-right p-3">Balance</th>
                              <th className="text-center p-3">x Materiality</th>
                              <th className="text-center p-3">Testing Required</th>
                            </tr>
                          </thead>
                          <tbody>
                            {riskAnalysis.significant_accounts?.map((account, index) => (
                              <tr key={index} className="border-b">
                                <td className="p-3">{account.account}</td>
                                <td className="p-3 text-right">{formatCurrency(account.balance)}</td>
                                <td className="p-3 text-center">{account.times_materiality}x</td>
                                <td className="p-3 text-center">
                                  {account.requires_testing ? (
                                    <CheckCircle2 className="w-5 h-5 text-success-500 mx-auto" />
                                  ) : (
                                    <XCircle className="w-5 h-5 text-neutral-300 mx-auto" />
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Focus Areas */}
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3">Recommended Focus Areas</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {riskAnalysis.recommended_focus_areas?.map((area, index) => (
                          <div key={index} className="p-3 bg-neutral-50 rounded-fluent">
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-body-strong text-neutral-900">{area.area}</p>
                              <span className={`text-caption px-2 py-0.5 rounded bg-${getRiskColor(area.priority)}-100 text-${getRiskColor(area.priority)}-700`}>
                                {area.priority}
                              </span>
                            </div>
                            <p className="text-caption text-neutral-600">{area.reason}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Materiality Tab */}
          {activeTab === 'materiality' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI Materiality Calculation</h2>
                  <p className="text-body text-neutral-600">
                    Intelligent benchmark selection with risk factor adjustments
                  </p>
                </div>
                <button
                  onClick={handleCalculateMateriality}
                  disabled={calculatingMateriality}
                  className="fluent-btn-primary"
                >
                  {calculatingMateriality ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Calculating...
                    </>
                  ) : (
                    <>
                      <Calculator className="w-4 h-4" />
                      {materialityResult ? 'Recalculate' : 'Calculate Materiality'}
                    </>
                  )}
                </button>
              </div>

              {materialityResult && (
                <div className="space-y-6">
                  {/* Main Materiality Values */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-primary-50 rounded-fluent border border-primary-200">
                      <p className="text-caption text-primary-600 mb-1">Overall Materiality</p>
                      <p className="text-2xl font-bold text-primary-900">{formatCurrency(materialityResult.overall_materiality)}</p>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Performance Materiality</p>
                      <p className="text-xl font-bold text-neutral-900">{formatCurrency(materialityResult.performance_materiality)}</p>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Trivial Threshold</p>
                      <p className="text-xl font-bold text-neutral-900">{formatCurrency(materialityResult.trivial_threshold)}</p>
                    </div>
                  </div>

                  {/* AI Reasoning */}
                  <div className="p-4 bg-primary-50 rounded-fluent border border-primary-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-5 h-5 text-primary-600" />
                      <h3 className="text-body-strong text-primary-900">AI Reasoning</h3>
                    </div>
                    <p className="text-body text-primary-800">{materialityResult.ai_reasoning}</p>
                    <p className="text-caption text-primary-600 mt-2">
                      Benchmark: {materialityResult.selected_benchmark} |
                      Risk Adjustment: {(materialityResult.risk_adjustment_factor * 100).toFixed(0)}%
                    </p>
                  </div>

                  {/* All Benchmarks */}
                  <div>
                    <h3 className="text-body-strong text-neutral-900 mb-3">All Benchmarks Analyzed</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(materialityResult.all_benchmarks || {}).map(([key, value]) => (
                        <div
                          key={key}
                          className={`p-3 rounded-fluent ${
                            key === materialityResult.selected_benchmark
                              ? 'bg-primary-100 border-2 border-primary-500'
                              : 'bg-neutral-50'
                          }`}
                        >
                          <p className="text-caption text-neutral-600">{key.replace(/_/g, ' ')}</p>
                          <p className="text-body-strong text-neutral-900">{formatCurrency(value)}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* PCAOB Compliance */}
                  <div className="p-3 bg-success-50 rounded-fluent border border-success-200">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-5 h-5 text-success-600" />
                      <h3 className="text-body-strong text-success-900">PCAOB AS 2105 Compliance</h3>
                    </div>
                    <ul className="text-caption text-success-800 space-y-1">
                      {materialityResult.pcaob_compliance_notes?.map((note, index) => (
                        <li key={index}>- {note}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Fraud Detection Tab */}
          {activeTab === 'fraud' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI Fraud Detection</h2>
                  <p className="text-body text-neutral-600">
                    Benford's Law analysis, pattern recognition, and anomaly detection
                  </p>
                </div>
                <button
                  onClick={handleDetectFraud}
                  disabled={detectingFraud}
                  className="fluent-btn-primary"
                >
                  {detectingFraud ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Detecting...
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4" />
                      {fraudDetection ? 'Re-analyze' : 'Detect Fraud Patterns'}
                    </>
                  )}
                </button>
              </div>

              {fraudDetection && (
                <div className="space-y-6">
                  {/* Fraud Risk Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Fraud Risk Score</p>
                      <p className="text-2xl font-bold text-neutral-900">{fraudDetection.fraud_risk_score}/100</p>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Risk Level</p>
                      <span className={`inline-flex px-3 py-1 rounded-full text-body-strong bg-${getRiskColor(fraudDetection.fraud_risk_level)}-100 text-${getRiskColor(fraudDetection.fraud_risk_level)}-700`}>
                        {fraudDetection.fraud_risk_level?.toUpperCase()}
                      </span>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Indicators Found</p>
                      <p className="text-2xl font-bold text-neutral-900">{fraudDetection.indicators_found}</p>
                    </div>
                  </div>

                  {/* Fraud Indicators */}
                  {fraudDetection.fraud_indicators?.length > 0 && (
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3">Fraud Indicators Detected</h3>
                      <div className="space-y-2">
                        {fraudDetection.fraud_indicators.map((indicator, index) => (
                          <div
                            key={index}
                            className={`p-3 rounded-fluent border-l-4 border-${getRiskColor(indicator.severity)}-500 bg-${getRiskColor(indicator.severity)}-50`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-body-strong text-neutral-900">{indicator.type.replace(/_/g, ' ').toUpperCase()}</p>
                              <span className={`text-caption px-2 py-0.5 rounded bg-${getRiskColor(indicator.severity)}-200 text-${getRiskColor(indicator.severity)}-800`}>
                                {indicator.severity}
                              </span>
                            </div>
                            <p className="text-body text-neutral-700">{indicator.description}</p>
                            {indicator.audit_implication && (
                              <p className="text-caption text-neutral-600 mt-1">
                                Implication: {indicator.audit_implication}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Required Procedures */}
                  <div>
                    <h3 className="text-body-strong text-neutral-900 mb-3">Required Fraud Procedures (AS 2401)</h3>
                    <ul className="space-y-2">
                      {fraudDetection.required_procedures?.map((proc, index) => (
                        <li key={index} className="flex items-start gap-2 text-body text-neutral-700">
                          <CheckCircle2 className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                          {proc}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* AS 2401 Compliance */}
                  <div className="p-3 bg-success-50 rounded-fluent border border-success-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-5 h-5 text-success-600" />
                      <h3 className="text-body-strong text-success-900">PCAOB AS 2401 Compliance</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-caption">
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.fraud_triangle_assessed ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>Fraud Triangle Assessed</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.journal_entry_testing_planned ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>JE Testing Planned</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.management_override_considered ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>Management Override Considered</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.revenue_recognition_evaluated ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>Revenue Recognition Evaluated</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Audit Programs Tab */}
          {activeTab === 'programs' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI-Generated Audit Programs</h2>
                  <p className="text-body text-neutral-600">
                    Risk-responsive procedures with optimized sample sizes
                  </p>
                </div>
                <button
                  onClick={handleGeneratePrograms}
                  disabled={generatingPrograms || !riskAnalysis || !materialityResult}
                  className="fluent-btn-primary"
                >
                  {generatingPrograms ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      Generate Programs
                    </>
                  )}
                </button>
              </div>

              {!riskAnalysis || !materialityResult ? (
                <div className="text-center py-8 text-neutral-500">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-warning-400" />
                  <p className="text-body">Complete Risk Analysis and Materiality calculation first</p>
                </div>
              ) : auditPrograms.length > 0 ? (
                <div className="space-y-4">
                  {auditPrograms.map((program, index) => (
                    <details key={index} className="group">
                      <summary className="flex items-center justify-between p-4 bg-neutral-50 rounded-fluent cursor-pointer hover:bg-neutral-100">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-primary-600" />
                          </div>
                          <div>
                            <p className="text-body-strong text-neutral-900">{program.audit_area.charAt(0).toUpperCase() + program.audit_area.slice(1)}</p>
                            <p className="text-caption text-neutral-600">
                              {program.procedures?.length || 0} procedures | {program.risk_level} risk
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-caption text-neutral-600">Est. Hours</p>
                            <p className="text-body-strong text-neutral-900">{program.estimated_hours?.total_estimated_hours || 0}h</p>
                          </div>
                          <div className="text-right">
                            <p className="text-caption text-success-600">AI Savings</p>
                            <p className="text-body-strong text-success-700">{program.estimated_hours?.efficiency_gain_percentage || 0}%</p>
                          </div>
                          <ChevronDown className="w-5 h-5 text-neutral-400 group-open:rotate-180 transition-transform" />
                        </div>
                      </summary>
                      <div className="p-4 border border-neutral-200 border-t-0 rounded-b-fluent">
                        <div className="mb-4 p-3 bg-primary-50 rounded-fluent">
                          <p className="text-caption text-primary-800 whitespace-pre-line">{program.program_summary}</p>
                        </div>
                        <div className="space-y-2">
                          {program.procedures?.map((proc, pIndex) => (
                            <div key={pIndex} className="p-3 bg-neutral-50 rounded-fluent">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <p className="text-body-strong text-neutral-900">{proc.name}</p>
                                  <p className="text-caption text-neutral-600 mt-1">{proc.description}</p>
                                  {proc.ai_capability && (
                                    <div className="mt-2 flex items-center gap-4 text-caption">
                                      <span className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded">AI-Enhanced</span>
                                      <span className="text-success-600">Time saved: {proc.human_time_saved}</span>
                                      <span className="text-primary-600">Accuracy: +{proc.accuracy_improvement}</span>
                                    </div>
                                  )}
                                </div>
                                <span className={`text-caption px-2 py-1 rounded bg-${proc.nature === 'substantive' ? 'blue' : 'purple'}-100 text-${proc.nature === 'substantive' ? 'blue' : 'purple'}-700`}>
                                  {proc.nature}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </details>
                  ))}
                </div>
              ) : null}
            </motion.div>
          )}

          {/* Planning Memo Tab */}
          {activeTab === 'memo' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI-Generated Planning Memo</h2>
                  <p className="text-body text-neutral-600">
                    PCAOB-compliant documentation ready for partner review
                  </p>
                </div>
                <div className="flex gap-2">
                  {planningMemo && (
                    <button className="fluent-btn-secondary">
                      <Download className="w-4 h-4" />
                      Export
                    </button>
                  )}
                  <button
                    onClick={handleGenerateMemo}
                    disabled={generatingMemo || !riskAnalysis || !materialityResult || !fraudDetection}
                    className="fluent-btn-primary"
                  >
                    {generatingMemo ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4" />
                        Generate Memo
                      </>
                    )}
                  </button>
                </div>
              </div>

              {!riskAnalysis || !materialityResult || !fraudDetection ? (
                <div className="text-center py-8 text-neutral-500">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-warning-400" />
                  <p className="text-body">Complete all analyses first (Risk, Materiality, Fraud)</p>
                </div>
              ) : planningMemo ? (
                <div className="space-y-4">
                  <div className="p-3 bg-warning-50 rounded-fluent border border-warning-200">
                    <div className="flex items-center gap-2">
                      <Eye className="w-5 h-5 text-warning-600" />
                      <span className="text-body-strong text-warning-900">Requires Partner Review</span>
                    </div>
                  </div>

                  <div className="prose prose-sm max-w-none">
                    <pre className="bg-neutral-50 p-4 rounded-fluent overflow-x-auto whitespace-pre-wrap text-sm font-mono">
                      {planningMemo.content}
                    </pre>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {planningMemo.pcaob_references?.map((ref, index) => (
                      <span key={index} className="px-2 py-1 bg-neutral-100 text-neutral-700 text-caption rounded">
                        {ref}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* AI Capabilities */}
          <div className="fluent-card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-primary-500" />
              <h3 className="text-body-strong text-neutral-900">AI Advantages</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center flex-shrink-0">
                  <Clock className="w-4 h-4 text-success-600" />
                </div>
                <div>
                  <p className="text-body-strong text-neutral-900">70% Faster</p>
                  <p className="text-caption text-neutral-600">Than traditional risk assessment</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <Target className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <p className="text-body-strong text-neutral-900">100% Coverage</p>
                  <p className="text-caption text-neutral-600">Benford's Law on all transactions</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-warning-100 flex items-center justify-center flex-shrink-0">
                  <Zap className="w-4 h-4 text-warning-600" />
                </div>
                <div>
                  <p className="text-body-strong text-neutral-900">500+ Benchmarks</p>
                  <p className="text-caption text-neutral-600">Industry-specific comparisons</p>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Summary */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Planning Progress</h3>
            <div className="space-y-3">
              {[
                { label: 'Risk Analysis', done: !!riskAnalysis },
                { label: 'Materiality', done: !!materialityResult },
                { label: 'Fraud Detection', done: !!fraudDetection },
                { label: 'Audit Programs', done: auditPrograms.length > 0 },
                { label: 'Planning Memo', done: !!planningMemo },
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-body text-neutral-700">{item.label}</span>
                  {item.done ? (
                    <CheckCircle2 className="w-5 h-5 text-success-500" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-neutral-300" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* PCAOB Compliance */}
          <div className="fluent-card p-5 bg-success-50 border border-success-200">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-5 h-5 text-success-600" />
              <h3 className="text-body-strong text-success-900">PCAOB Compliant</h3>
            </div>
            <ul className="text-caption text-success-800 space-y-1">
              <li>AS 2101 - Audit Planning</li>
              <li>AS 2105 - Materiality</li>
              <li>AS 2110 - Risk Assessment</li>
              <li>AS 2301 - Risk Response</li>
              <li>AS 2401 - Fraud Consideration</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAuditPlanning;
