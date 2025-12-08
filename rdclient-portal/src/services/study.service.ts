/**
 * R&D Study Service
 * API client for R&D study data management
 */

import api from './api';
import type {
  RDStudyInfo,
  EligibilityQuestionnaire,
  RDProject,
  RDEmployee,
  TaxReturn,
  RDDocument,
  TeamInvitation,
  CreateTeamInvitation,
  AIAssistanceRequest,
  AIAssistanceResponse,
  FourPartTest,
} from '../types';

class StudyService {
  // ========================================
  // Study Information
  // ========================================

  /**
   * Get the current user's study information
   */
  async getStudyInfo(): Promise<RDStudyInfo> {
    return api.get<RDStudyInfo>('/rdclient/study');
  }

  /**
   * Get study progress summary
   */
  async getStudyProgress(): Promise<RDStudyInfo['progress']> {
    return api.get<RDStudyInfo['progress']>('/rdclient/study/progress');
  }

  // ========================================
  // Eligibility Questionnaire
  // ========================================

  /**
   * Get eligibility questionnaire
   */
  async getEligibilityQuestionnaire(): Promise<EligibilityQuestionnaire | null> {
    try {
      return await api.get<EligibilityQuestionnaire>('/rdclient/study/eligibility');
    } catch {
      return null;
    }
  }

  /**
   * Save eligibility questionnaire (auto-save)
   */
  async saveEligibilityQuestionnaire(data: Partial<EligibilityQuestionnaire>): Promise<EligibilityQuestionnaire> {
    return api.patch<EligibilityQuestionnaire>('/rdclient/study/eligibility', data);
  }

  /**
   * Submit eligibility questionnaire for AI analysis
   */
  async submitEligibilityQuestionnaire(data: EligibilityQuestionnaire): Promise<{
    questionnaire: EligibilityQuestionnaire;
    ai_analysis: {
      eligibility_score: number;
      recommendations: string[];
      potential_credits_range: { min: number; max: number };
    };
  }> {
    return api.post('/rdclient/study/eligibility/submit', data);
  }

  // ========================================
  // Projects
  // ========================================

  /**
   * Get all projects for the study
   */
  async getProjects(): Promise<RDProject[]> {
    return api.get<RDProject[]>('/rdclient/study/projects');
  }

  /**
   * Get a specific project
   */
  async getProject(projectId: string): Promise<RDProject> {
    return api.get<RDProject>(`/rdclient/study/projects/${projectId}`);
  }

  /**
   * Create a new project
   */
  async createProject(data: Partial<RDProject>): Promise<RDProject> {
    return api.post<RDProject>('/rdclient/study/projects', data);
  }

  /**
   * Update a project
   */
  async updateProject(projectId: string, data: Partial<RDProject>): Promise<RDProject> {
    return api.patch<RDProject>(`/rdclient/study/projects/${projectId}`, data);
  }

  /**
   * Update project's four-part test
   */
  async updateProjectFourPartTest(projectId: string, fourPartTest: FourPartTest): Promise<RDProject> {
    return api.patch<RDProject>(`/rdclient/study/projects/${projectId}/four-part-test`, fourPartTest);
  }

  /**
   * Delete a project
   */
  async deleteProject(projectId: string): Promise<void> {
    await api.delete(`/rdclient/study/projects/${projectId}`);
  }

  // ========================================
  // Employees
  // ========================================

  /**
   * Get all employees for the study
   */
  async getEmployees(): Promise<RDEmployee[]> {
    return api.get<RDEmployee[]>('/rdclient/study/employees');
  }

  /**
   * Create a new employee
   */
  async createEmployee(data: Partial<RDEmployee>): Promise<RDEmployee> {
    return api.post<RDEmployee>('/rdclient/study/employees', data);
  }

  /**
   * Update an employee
   */
  async updateEmployee(employeeId: string, data: Partial<RDEmployee>): Promise<RDEmployee> {
    return api.patch<RDEmployee>(`/rdclient/study/employees/${employeeId}`, data);
  }

  /**
   * Delete an employee
   */
  async deleteEmployee(employeeId: string): Promise<void> {
    await api.delete(`/rdclient/study/employees/${employeeId}`);
  }

  /**
   * Bulk import employees from spreadsheet
   */
  async importEmployees(file: File): Promise<{ imported: number; errors: string[] }> {
    return api.uploadFile('/rdclient/study/employees/import', file);
  }

  // ========================================
  // Tax Returns
  // ========================================

  /**
   * Get uploaded tax returns
   */
  async getTaxReturns(): Promise<TaxReturn[]> {
    return api.get<TaxReturn[]>('/rdclient/study/tax-returns');
  }

  /**
   * Upload a tax return
   */
  async uploadTaxReturn(file: File, taxYear: number): Promise<TaxReturn> {
    return api.uploadFile<TaxReturn>('/rdclient/study/tax-returns', file, {
      tax_year: taxYear.toString(),
    });
  }

  /**
   * Delete a tax return
   */
  async deleteTaxReturn(taxReturnId: string): Promise<void> {
    await api.delete(`/rdclient/study/tax-returns/${taxReturnId}`);
  }

  // ========================================
  // Documents
  // ========================================

  /**
   * Get all documents for the study
   */
  async getDocuments(): Promise<RDDocument[]> {
    return api.get<RDDocument[]>('/rdclient/study/documents');
  }

  /**
   * Upload a document
   */
  async uploadDocument(file: File, category: string, description?: string): Promise<RDDocument> {
    return api.uploadFile<RDDocument>('/rdclient/study/documents', file, {
      category,
      description: description || '',
    });
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/rdclient/study/documents/${documentId}`);
  }

  // ========================================
  // Team Management
  // ========================================

  /**
   * Get team invitations
   */
  async getTeamInvitations(): Promise<TeamInvitation[]> {
    return api.get<TeamInvitation[]>('/rdclient/study/team/invitations');
  }

  /**
   * Invite a team member
   */
  async inviteTeamMember(data: CreateTeamInvitation): Promise<TeamInvitation> {
    return api.post<TeamInvitation>('/rdclient/study/team/invite', data);
  }

  /**
   * Resend an invitation
   */
  async resendInvitation(invitationId: string): Promise<TeamInvitation> {
    return api.post<TeamInvitation>(`/rdclient/study/team/invitations/${invitationId}/resend`);
  }

  /**
   * Cancel an invitation
   */
  async cancelInvitation(invitationId: string): Promise<void> {
    await api.delete(`/rdclient/study/team/invitations/${invitationId}`);
  }

  // ========================================
  // AI Assistance
  // ========================================

  /**
   * Get AI assistance for various tasks
   */
  async getAIAssistance(request: AIAssistanceRequest): Promise<AIAssistanceResponse> {
    return api.post<AIAssistanceResponse>('/rdclient/ai/assist', request);
  }

  /**
   * Generate AI-enhanced project description
   */
  async generateProjectDescription(projectId: string, userInput?: string): Promise<{
    description: string;
    four_part_test_suggestions: Partial<FourPartTest>;
    confidence_score: number;
  }> {
    return api.post(`/rdclient/ai/projects/${projectId}/enhance`, { user_input: userInput });
  }

  /**
   * Analyze eligibility and get AI recommendations
   */
  async analyzeEligibility(): Promise<{
    score: number;
    is_likely_eligible: boolean;
    recommendations: string[];
    areas_of_strength: string[];
    areas_needing_improvement: string[];
  }> {
    return api.post('/rdclient/ai/analyze-eligibility');
  }

  // ========================================
  // Submission
  // ========================================

  /**
   * Submit all data for CPA review
   */
  async submitForReview(): Promise<{
    success: boolean;
    message: string;
    submission_id: string;
  }> {
    return api.post('/rdclient/study/submit');
  }

  /**
   * Check if all required data is complete
   */
  async validateCompletion(): Promise<{
    is_complete: boolean;
    missing_items: string[];
    warnings: string[];
  }> {
    return api.get('/rdclient/study/validate');
  }
}

export const studyService = new StudyService();
export default studyService;
