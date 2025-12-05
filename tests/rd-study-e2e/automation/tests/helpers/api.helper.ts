import { APIRequestContext, expect } from '@playwright/test';

export interface RDStudyCreateRequest {
  firm_id: string;
  client_id: string;
  name: string;
  tax_year: number;
  entity_type: string;
  entity_name: string;
  ein: string;
  fiscal_year_start: string;
  fiscal_year_end: string;
  states: string[];
  primary_state: string;
}

export interface QREData {
  category: string;
  gross_amount: number;
  qualified_percentage: number;
  state_allocation: Record<string, number>;
  project_id?: string;
  employee_id?: string;
}

export interface CalculationResult {
  federal_regular_credit: number;
  federal_asc_credit: number;
  recommended_method: string;
  final_federal_credit: number;
  state_credits: Record<string, {
    credit: number;
    rate: number;
    qre_allocated: number;
  }>;
  total_credits: number;
}

export class RDStudyAPIHelper {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(private request: APIRequestContext, baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Authenticate and get JWT token
   */
  async authenticate(email: string, password: string): Promise<string> {
    const response = await this.request.post(`${this.baseUrl}/auth/login`, {
      data: { email, password },
    });

    if (response.status() !== 200) {
      throw new Error(`Authentication failed: ${response.status()}`);
    }

    const data = await response.json();
    this.authToken = data.access_token;
    return this.authToken;
  }

  /**
   * Get auth headers
   */
  private getAuthHeaders(): Record<string, string> {
    if (!this.authToken) {
      throw new Error('Not authenticated. Call authenticate() first.');
    }
    return {
      'Authorization': `Bearer ${this.authToken}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Create a new R&D study
   */
  async createStudy(studyData: RDStudyCreateRequest): Promise<{ id: string; study: any }> {
    const response = await this.request.post(`${this.baseUrl}/rd-studies`, {
      headers: this.getAuthHeaders(),
      data: studyData,
    });

    expect(response.status()).toBe(201);
    const study = await response.json();
    return { id: study.id, study };
  }

  /**
   * Add project to study
   */
  async addProject(studyId: string, projectData: any): Promise<{ id: string; project: any }> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/projects`,
      {
        headers: this.getAuthHeaders(),
        data: projectData,
      }
    );

    expect(response.status()).toBe(201);
    const project = await response.json();
    return { id: project.id, project };
  }

  /**
   * Add employee to study
   */
  async addEmployee(studyId: string, employeeData: any): Promise<{ id: string; employee: any }> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/employees`,
      {
        headers: this.getAuthHeaders(),
        data: employeeData,
      }
    );

    expect(response.status()).toBe(201);
    const employee = await response.json();
    return { id: employee.id, employee };
  }

  /**
   * Add QRE record
   */
  async addQRE(studyId: string, qreData: QREData): Promise<{ id: string; qre: any }> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/qres`,
      {
        headers: this.getAuthHeaders(),
        data: qreData,
      }
    );

    expect(response.status()).toBe(201);
    const qre = await response.json();
    return { id: qre.id, qre };
  }

  /**
   * Upload document to study
   */
  async uploadDocument(
    studyId: string,
    filePath: string,
    documentType: string
  ): Promise<{ id: string; document: any }> {
    const fs = require('fs');
    const path = require('path');

    const fileBuffer = fs.readFileSync(filePath);
    const fileName = path.basename(filePath);

    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/documents`,
      {
        headers: {
          'Authorization': `Bearer ${this.authToken}`,
        },
        multipart: {
          file: {
            name: fileName,
            mimeType: 'application/octet-stream',
            buffer: fileBuffer,
          },
          document_type: documentType,
        },
      }
    );

    expect(response.status()).toBe(201);
    const document = await response.json();
    return { id: document.id, document };
  }

  /**
   * Trigger AI qualification analysis for project
   */
  async runProjectQualification(studyId: string, projectId: string): Promise<any> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/projects/${projectId}/qualify`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    return await response.json();
  }

  /**
   * Generate 4-part test narratives using AI
   */
  async generateNarratives(studyId: string, projectId: string): Promise<any> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/projects/${projectId}/generate-narratives`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    return await response.json();
  }

  /**
   * Calculate credits (federal + state)
   */
  async calculateCredits(
    studyId: string,
    options: {
      historical_data: any;
      section_280c: boolean;
      states: string[];
    }
  ): Promise<CalculationResult> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/calculate`,
      {
        headers: this.getAuthHeaders(),
        data: options,
      }
    );

    expect(response.status()).toBe(200);
    return await response.json();
  }

  /**
   * Generate Excel workbook
   */
  async generateExcelWorkbook(studyId: string): Promise<{ url: string; fileId: string }> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/generate/excel`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    const result = await response.json();
    return { url: result.download_url, fileId: result.file_id };
  }

  /**
   * Generate PDF study report
   */
  async generatePDFReport(studyId: string): Promise<{ url: string; fileId: string }> {
    const response = await this.request.post(
      `${this.baseUrl}/rd-studies/${studyId}/generate/pdf`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    const result = await response.json();
    return { url: result.download_url, fileId: result.file_id };
  }

  /**
   * Download file
   */
  async downloadFile(fileId: string): Promise<Buffer> {
    const response = await this.request.get(
      `${this.baseUrl}/files/${fileId}/download`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    return await response.body();
  }

  /**
   * Get study summary
   */
  async getStudySummary(studyId: string): Promise<any> {
    const response = await this.request.get(
      `${this.baseUrl}/rd-studies/${studyId}/summary`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    return await response.json();
  }

  /**
   * Get state credit details
   */
  async getStateCreditDetails(studyId: string, stateCode: string): Promise<any> {
    const response = await this.request.get(
      `${this.baseUrl}/rd-studies/${studyId}/state-credits/${stateCode}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    expect(response.status()).toBe(200);
    return await response.json();
  }
}
