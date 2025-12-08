/**
 * R&D Client Portal Type Definitions
 */

// User & Authentication Types
export interface RDClientUser {
  id: string;
  email: string;
  full_name: string;
  company_name: string;
  phone?: string;
  role: 'primary' | 'team_member';
  study_id: string;
  firm_id: string;
  firm_name: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthState {
  user: RDClientUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  token: string; // Invitation token
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user: RDClientUser;
}

// Study Types
export interface RDStudyInfo {
  id: string;
  name: string;
  company_name: string;
  tax_year: number;
  status: RDStudyStatus;
  firm_name: string;
  firm_logo?: string;
  deadline?: string;
  created_at: string;
  progress: StudyProgress;
}

export type RDStudyStatus =
  | 'draft'
  | 'data_collection'
  | 'qualification'
  | 'qre_analysis'
  | 'calculation'
  | 'review'
  | 'cpa_review'
  | 'approved'
  | 'finalized';

export interface StudyProgress {
  eligibility_complete: boolean;
  projects_added: number;
  employees_added: number;
  tax_returns_uploaded: boolean;
  documents_uploaded: number;
  overall_percentage: number;
}

// Eligibility Questionnaire Types
export interface EligibilityQuestionnaire {
  id: string;
  study_id: string;
  company_info: CompanyInfo;
  rd_activities: RDActivitiesInfo;
  technical_uncertainty: TechnicalUncertaintyInfo;
  experimentation: ExperimentationInfo;
  completed: boolean;
  ai_eligibility_score?: number;
  ai_recommendations?: string[];
  created_at: string;
  updated_at: string;
}

export interface CompanyInfo {
  company_name: string;
  ein?: string;
  industry: string;
  industry_naics?: string;
  employees_count: number;
  years_in_business: number;
  annual_revenue?: number;
  has_rd_department: boolean;
  rd_budget?: number;
}

export interface RDActivitiesInfo {
  develops_new_products: boolean;
  improves_existing_products: boolean;
  develops_new_processes: boolean;
  develops_software: boolean;
  designs_prototypes: boolean;
  conducts_testing: boolean;
  rd_activity_description: string;
  primary_rd_areas: string[];
}

export interface TechnicalUncertaintyInfo {
  faced_capability_uncertainty: boolean;
  faced_method_uncertainty: boolean;
  faced_design_uncertainty: boolean;
  uncertainty_examples: string;
  how_resolved: string;
}

export interface ExperimentationInfo {
  uses_systematic_approach: boolean;
  evaluates_alternatives: boolean;
  documents_experiments: boolean;
  conducts_testing: boolean;
  experimentation_description: string;
  testing_methods: string[];
}

// Project Types
export interface RDProject {
  id: string;
  study_id: string;
  name: string;
  code?: string;
  description: string;
  business_component: string;
  department?: string;
  start_date: string;
  end_date?: string;
  is_ongoing: boolean;
  employees_assigned: string[];
  four_part_test: FourPartTest;
  qualification_status: 'pending' | 'qualified' | 'not_qualified' | 'needs_review';
  ai_qualification_score?: number;
  ai_suggestions?: string[];
  created_at: string;
  updated_at: string;
}

export interface FourPartTest {
  permitted_purpose: PermittedPurpose;
  technological_nature: TechnologicalNature;
  elimination_uncertainty: EliminationUncertainty;
  process_experimentation: ProcessExperimentation;
}

export interface PermittedPurpose {
  answer: string;
  new_functionality: boolean;
  improved_performance: boolean;
  improved_reliability: boolean;
  improved_quality: boolean;
  examples: string;
}

export interface TechnologicalNature {
  answer: string;
  uses_engineering: boolean;
  uses_physics: boolean;
  uses_biology: boolean;
  uses_chemistry: boolean;
  uses_computer_science: boolean;
  specific_technologies: string;
}

export interface EliminationUncertainty {
  answer: string;
  capability_uncertain: boolean;
  method_uncertain: boolean;
  design_uncertain: boolean;
  uncertainty_examples: string;
}

export interface ProcessExperimentation {
  answer: string;
  systematic_approach: boolean;
  tested_alternatives: boolean;
  documented_results: boolean;
  experimentation_examples: string;
}

// Employee Types
export interface RDEmployee {
  id: string;
  study_id: string;
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
  projects_assigned: string[];
  state?: string;
  created_at: string;
  updated_at: string;
}

// Tax Return Types
export interface TaxReturn {
  id: string;
  study_id: string;
  tax_year: number;
  file_name: string;
  file_type: 'pdf' | 'image';
  file_size: number;
  upload_status: 'pending' | 'processing' | 'processed' | 'error';
  processing_result?: TaxReturnProcessingResult;
  uploaded_at: string;
  uploaded_by: string;
}

export interface TaxReturnProcessingResult {
  extracted_data: {
    gross_receipts?: number;
    total_assets?: number;
    wages_reported?: number;
    rd_credit_claimed?: number;
  };
  validation_warnings?: string[];
  ai_verified: boolean;
}

// Document Types
export interface RDDocument {
  id: string;
  study_id: string;
  name: string;
  category: DocumentCategory;
  file_type: string;
  file_size: number;
  upload_status: 'pending' | 'processing' | 'processed' | 'error';
  uploaded_at: string;
  uploaded_by: string;
  description?: string;
}

export type DocumentCategory =
  | 'payroll'
  | 'timesheet'
  | 'project_documentation'
  | 'contracts'
  | 'invoices'
  | 'tax_return'
  | 'other';

// Team Invitation Types
export interface TeamInvitation {
  id: string;
  study_id: string;
  email: string;
  name: string;
  role: 'team_member';
  status: 'pending' | 'accepted' | 'expired';
  invited_by: string;
  invited_at: string;
  expires_at: string;
  accepted_at?: string;
}

export interface CreateTeamInvitation {
  email: string;
  name: string;
}

// AI Assistance Types
export interface AIAssistanceRequest {
  type: 'project_description' | 'four_part_test' | 'eligibility' | 'general';
  context: Record<string, unknown>;
  user_input?: string;
}

export interface AIAssistanceResponse {
  suggestions: string[];
  improved_text?: string;
  confidence_score: number;
  reasoning?: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}
