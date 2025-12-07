import { Page, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface UploadResult {
  fileName: string;
  fileHash: string;
  uploadStatus: 'success' | 'failed' | 'pending';
  documentType: string;
  entityName: string;
  serverFileId?: string;
}

export interface DocumentRequest {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'uploaded' | 'approved' | 'rejected';
  entityName: string;
}

const SYNTHETIC_DATA_PATH = path.join(__dirname, '../../../synthetic-data');

export const DOCUMENT_MAPPINGS = {
  trialBalance: {
    parent: 'Parent/trial_balance.csv',
    subA: 'SubA_US/trial_balance.csv',
    subB: 'SubB_EUR/trial_balance.csv',
    subC: 'SubC_USD/trial_balance.csv',
  },
  fixedAssets: {
    parent: 'Parent/fixed_assets_register.csv',
    subA: 'SubA_US/fixed_assets_register.csv',
    subB: 'SubB_EUR/fixed_assets_register.csv',
    subC: 'SubC_USD/fixed_assets_register.csv',
  },
  leases: 'Consolidation/lease_schedule_asc842.csv',
  leaseMaturity: 'Consolidation/lease_maturity_schedule.csv',
  consolidationWorksheet: 'Consolidation/consolidation_worksheet.csv',
  eliminations: 'Consolidation/elimination_entries.csv',
  fxTranslation: 'Consolidation/fx_translation_schedule.csv',
  goodwillImpairment: 'Consolidation/goodwill_impairment_test.md',
  nciSchedule: 'Consolidation/nci_schedule.csv',
  bankConfirmations: 'SupportDocs/bank_confirmations.md',
  arAging: 'SupportDocs/ar_aging_schedule.csv',
  inventoryCount: 'SupportDocs/inventory_count_sheets.csv',
  debtAgreements: 'SupportDocs/debt_agreements.md',
  leaseContracts: 'SupportDocs/lease_contracts_summary.md',
  legalLetter: 'SupportDocs/legal_letter.md',
  managementRepLetter: 'SupportDocs/management_rep_letter.md',
  boardMinutes: 'SupportDocs/board_minutes_extract.md',
  taxProvision: 'SupportDocs/tax_provision_workpaper.csv',
  revenueRecognition: 'SupportDocs/revenue_recognition_policy.md',
  relatedParties: 'SupportDocs/related_parties.csv',
};

export class UploadHelper {
  constructor(private page: Page) {}

  /**
   * Calculate file hash for integrity verification
   */
  calculateFileHash(filePath: string): string {
    const fullPath = path.join(SYNTHETIC_DATA_PATH, filePath);
    if (!fs.existsSync(fullPath)) {
      throw new Error(`File not found: ${fullPath}`);
    }
    const fileBuffer = fs.readFileSync(fullPath);
    return crypto.createHash('sha256').update(fileBuffer).digest('hex');
  }

  /**
   * Get all document requests from client portal
   */
  async getDocumentRequests(): Promise<DocumentRequest[]> {
    const requests: DocumentRequest[] = [];

    // Wait for document request list to load
    await this.page.waitForSelector(
      '.document-request, [data-testid="document-request"], .request-item, table tbody tr',
      { timeout: 10000 }
    );

    const requestElements = await this.page.locator(
      '.document-request, [data-testid="document-request"], .request-item, table tbody tr'
    ).all();

    for (const element of requestElements) {
      const name = await element.locator('.request-name, td:first-child, .name').textContent() || '';
      const status = await element.locator('.request-status, .status, td:last-child').textContent() || 'pending';
      const id = await element.getAttribute('data-id') || await element.getAttribute('id') || '';

      requests.push({
        id,
        name: name.trim(),
        description: '',
        status: status.toLowerCase().includes('pending') ? 'pending' :
                status.toLowerCase().includes('uploaded') ? 'uploaded' :
                status.toLowerCase().includes('approved') ? 'approved' : 'rejected',
        entityName: '',
      });
    }

    return requests;
  }

  /**
   * Upload a single document
   */
  async uploadDocument(
    documentType: string,
    filePath: string,
    entityName: string = 'Parent'
  ): Promise<UploadResult> {
    const fullPath = path.join(SYNTHETIC_DATA_PATH, filePath);
    const fileName = path.basename(filePath);
    const fileHash = this.calculateFileHash(filePath);

    // Find the upload area for this document type
    const uploadArea = await this.page.locator(
      `[data-document-type="${documentType}"], .upload-area, input[type="file"]`
    ).first();

    // Handle file input
    const fileInput = await this.page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(fullPath);

    // Wait for upload to complete
    await this.page.waitForSelector(
      '.upload-success, .upload-complete, [data-testid="upload-success"]',
      { timeout: 30000 }
    ).catch(() => null);

    // Check upload status
    const successIndicator = await this.page.locator(
      '.upload-success, .success-message, [data-status="success"]'
    ).first();

    const uploadStatus = await successIndicator.isVisible() ? 'success' : 'failed';

    return {
      fileName,
      fileHash,
      uploadStatus,
      documentType,
      entityName,
    };
  }

  /**
   * Upload all trial balances
   */
  async uploadTrialBalances(): Promise<UploadResult[]> {
    const results: UploadResult[] = [];

    const entities = [
      { name: 'Parent', path: DOCUMENT_MAPPINGS.trialBalance.parent },
      { name: 'Sub A', path: DOCUMENT_MAPPINGS.trialBalance.subA },
      { name: 'Sub B', path: DOCUMENT_MAPPINGS.trialBalance.subB },
      { name: 'Sub C', path: DOCUMENT_MAPPINGS.trialBalance.subC },
    ];

    for (const entity of entities) {
      const result = await this.uploadDocument('trial_balance', entity.path, entity.name);
      results.push(result);
    }

    return results;
  }

  /**
   * Upload all fixed assets registers
   */
  async uploadFixedAssets(): Promise<UploadResult[]> {
    const results: UploadResult[] = [];

    const entities = [
      { name: 'Parent', path: DOCUMENT_MAPPINGS.fixedAssets.parent },
      { name: 'Sub A', path: DOCUMENT_MAPPINGS.fixedAssets.subA },
      { name: 'Sub B', path: DOCUMENT_MAPPINGS.fixedAssets.subB },
      { name: 'Sub C', path: DOCUMENT_MAPPINGS.fixedAssets.subC },
    ];

    for (const entity of entities) {
      const result = await this.uploadDocument('fixed_assets', entity.path, entity.name);
      results.push(result);
    }

    return results;
  }

  /**
   * Upload consolidation schedules
   */
  async uploadConsolidationSchedules(): Promise<UploadResult[]> {
    const results: UploadResult[] = [];

    const consolidationDocs = [
      { type: 'lease_schedule', path: DOCUMENT_MAPPINGS.leases },
      { type: 'consolidation_worksheet', path: DOCUMENT_MAPPINGS.consolidationWorksheet },
      { type: 'eliminations', path: DOCUMENT_MAPPINGS.eliminations },
      { type: 'fx_translation', path: DOCUMENT_MAPPINGS.fxTranslation },
      { type: 'nci_schedule', path: DOCUMENT_MAPPINGS.nciSchedule },
    ];

    for (const doc of consolidationDocs) {
      const result = await this.uploadDocument(doc.type, doc.path, 'Consolidated');
      results.push(result);
    }

    return results;
  }

  /**
   * Upload all support documents
   */
  async uploadSupportDocuments(): Promise<UploadResult[]> {
    const results: UploadResult[] = [];

    const supportDocs = [
      { type: 'bank_confirmations', path: DOCUMENT_MAPPINGS.bankConfirmations },
      { type: 'ar_aging', path: DOCUMENT_MAPPINGS.arAging },
      { type: 'inventory_count', path: DOCUMENT_MAPPINGS.inventoryCount },
      { type: 'debt_agreements', path: DOCUMENT_MAPPINGS.debtAgreements },
      { type: 'lease_contracts', path: DOCUMENT_MAPPINGS.leaseContracts },
      { type: 'legal_letter', path: DOCUMENT_MAPPINGS.legalLetter },
      { type: 'management_rep', path: DOCUMENT_MAPPINGS.managementRepLetter },
      { type: 'board_minutes', path: DOCUMENT_MAPPINGS.boardMinutes },
      { type: 'tax_provision', path: DOCUMENT_MAPPINGS.taxProvision },
      { type: 'revenue_recognition', path: DOCUMENT_MAPPINGS.revenueRecognition },
      { type: 'related_parties', path: DOCUMENT_MAPPINGS.relatedParties },
    ];

    for (const doc of supportDocs) {
      const result = await this.uploadDocument(doc.type, doc.path, 'Support');
      results.push(result);
    }

    return results;
  }

  /**
   * Submit all uploaded documents for CPA review
   */
  async submitForReview(): Promise<boolean> {
    const submitButton = await this.page.locator(
      'button:has-text("Submit"), button:has-text("Submit for Review"), button:has-text("Complete Upload")'
    ).first();

    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Wait for confirmation
      await this.page.waitForSelector(
        '.submit-success, [data-testid="submit-success"], .confirmation-message',
        { timeout: 30000 }
      );

      return true;
    }

    return false;
  }

  /**
   * Verify file was received correctly (CPA side)
   */
  async verifyFileReceived(fileName: string, expectedHash: string): Promise<boolean> {
    // Look for the file in the documents list
    const fileElement = await this.page.locator(
      `[data-filename="${fileName}"], .document-row:has-text("${fileName}")`
    ).first();

    if (!await fileElement.isVisible()) {
      return false;
    }

    // Check for validation status
    const statusElement = await fileElement.locator('.status, .validation-status');
    const status = await statusElement.textContent() || '';

    return status.toLowerCase().includes('validated') ||
           status.toLowerCase().includes('received') ||
           status.toLowerCase().includes('success');
  }
}
