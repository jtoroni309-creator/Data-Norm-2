/**
 * Document Service
 * Handles document uploads, management, and AI extraction
 */

import axios from 'axios';
import type { Document, DocumentCategory, DocumentRequirement } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export class DocumentService {
  /**
   * Upload document
   */
  public async uploadDocument(
    file: File,
    category: DocumentCategory,
    engagementId?: string
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (engagementId) {
      formData.append('engagementId', engagementId);
    }

    const response = await axios.post<Document>(`${API_BASE_URL}/documents/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
        // Emit progress event
        window.dispatchEvent(
          new CustomEvent('document-upload-progress', {
            detail: { fileName: file.name, progress: percentCompleted },
          })
        );
      },
    });

    return response.data;
  }

  /**
   * Upload multiple documents
   */
  public async uploadMultipleDocuments(
    files: File[],
    category: DocumentCategory,
    engagementId?: string
  ): Promise<Document[]> {
    const uploads = files.map((file) => this.uploadDocument(file, category, engagementId));
    return Promise.all(uploads);
  }

  /**
   * Get all documents
   */
  public async getDocuments(engagementId?: string): Promise<Document[]> {
    const params = engagementId ? { engagementId } : {};
    const response = await axios.get<Document[]>(`${API_BASE_URL}/documents`, { params });
    return response.data;
  }

  /**
   * Get document requirements
   */
  public async getDocumentRequirements(engagementId: string): Promise<DocumentRequirement[]> {
    const response = await axios.get<DocumentRequirement[]>(
      `${API_BASE_URL}/documents/requirements/${engagementId}`
    );
    return response.data;
  }

  /**
   * Delete document
   */
  public async deleteDocument(documentId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/documents/${documentId}`);
  }

  /**
   * Download document
   */
  public async downloadDocument(documentId: string): Promise<Blob> {
    const response = await axios.get(`${API_BASE_URL}/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Get document categories
   */
  public getDocumentCategories(): {
    value: DocumentCategory;
    label: string;
    description: string;
    icon: string;
  }[] {
    return [
      {
        value: 'financial_statements',
        label: 'Financial Statements',
        description: 'Balance sheet, income statement, cash flow statement',
        icon: 'FileSpreadsheet',
      },
      {
        value: 'bank_statements',
        label: 'Bank Statements',
        description: 'Monthly bank statements and reconciliations',
        icon: 'Building2',
      },
      {
        value: 'invoices',
        label: 'Invoices',
        description: 'Sales invoices and accounts receivable',
        icon: 'Receipt',
      },
      {
        value: 'receipts',
        label: 'Receipts',
        description: 'Expense receipts and supporting documentation',
        icon: 'FileText',
      },
      {
        value: 'contracts',
        label: 'Contracts',
        description: 'Agreements, leases, and legal documents',
        icon: 'FileSignature',
      },
      {
        value: 'tax_documents',
        label: 'Tax Documents',
        description: 'Tax returns, 1099s, W-2s, and tax filings',
        icon: 'Calculator',
      },
      {
        value: 'payroll',
        label: 'Payroll',
        description: 'Payroll registers, tax filings, and employee records',
        icon: 'Users',
      },
      {
        value: 'other',
        label: 'Other',
        description: 'Additional supporting documentation',
        icon: 'Folder',
      },
    ];
  }

  /**
   * Request AI document extraction
   */
  public async extractDocumentData(documentId: string): Promise<{
    documentType: string;
    confidence: number;
    extractedData: Record<string, any>;
  }> {
    const response = await axios.post(`${API_BASE_URL}/documents/${documentId}/extract`);
    return response.data;
  }

  /**
   * Get document preview URL
   */
  public getDocumentPreviewUrl(documentId: string): string {
    return `${API_BASE_URL}/documents/${documentId}/preview`;
  }
}

export const documentService = new DocumentService();
