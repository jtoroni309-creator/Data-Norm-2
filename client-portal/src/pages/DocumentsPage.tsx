import React, { useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AlertCircle,
  CheckCircle,
  Download,
  File,
  FileSpreadsheet,
  FileText,
  Image,
  Shield,
  Trash2,
  Upload,
} from 'lucide-react';
import { documentService } from '../services/document.service';
import type { DocumentCategory } from '@/types';

interface EngagementDocument {
  id: string;
  fileName: string;
  fileSize: number;
  category: string;
  status: 'uploaded' | 'processing' | 'approved' | 'rejected';
  uploadedAt: string;
}

const categoryPills: Array<{
  value: DocumentCategory;
  label: string;
  accent: string;
}> = [
  { value: 'financial_statements', label: 'Financial Statements', accent: 'bg-primary-50 text-primary-600' },
  { value: 'bank_statements', label: 'Bank Statements', accent: 'bg-success-50 text-success-600' },
  { value: 'invoices', label: 'Invoices', accent: 'bg-accent-50 text-accent-600' },
  { value: 'receipts', label: 'Receipts', accent: 'bg-rose-50 text-rose-600' },
  { value: 'payroll', label: 'Payroll Records', accent: 'bg-warning-50 text-warning-700' },
  { value: 'tax_documents', label: 'Tax Documents', accent: 'bg-neutral-100 text-neutral-700' },
  { value: 'contracts', label: 'Contracts', accent: 'bg-purple-50 text-purple-600' },
  { value: 'other', label: 'Other', accent: 'bg-neutral-50 text-neutral-600' },
];

const statusBadges: Record<EngagementDocument['status'], string> = {
  uploaded: 'bg-primary-50 text-primary-600',
  processing: 'bg-warning-50 text-warning-700',
  approved: 'bg-success-50 text-success-600',
  rejected: 'bg-error-50 text-error-600',
};

const createDocumentId = () => `doc-${Date.now()}-${Math.random().toString(16).slice(2)}`;

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<EngagementDocument[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<DocumentCategory>('financial_statements');

  const stats = useMemo(() => {
    const uploaded = documents.filter((doc) => doc.status === 'approved').length;
    const pending = documents.filter((doc) => doc.status !== 'approved').length;
    const totalSize = documents.reduce((acc, doc) => acc + doc.fileSize, 0);
    return {
      approved: uploaded,
      pending,
      totalSize,
    };
  }, [documents]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);

    try {
      for (const file of Array.from(files)) {
        await documentService.uploadDocument(file, selectedCategory, 'engagement-123');
        setDocuments((prev) => [
          {
            id: createDocumentId(),
            fileName: file.name,
            fileSize: file.size,
            category: selectedCategory,
            status: 'uploaded',
            uploadedAt: new Date().toISOString(),
          },
          ...prev,
        ]);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (['jpg', 'jpeg', 'png'].includes(ext || '')) return <Image className="h-10 w-10 text-primary-500" />;
    if (['xlsx', 'xls', 'csv'].includes(ext || '')) return <FileSpreadsheet className="h-10 w-10 text-success-500" />;
    if (['pdf', 'doc', 'docx'].includes(ext || '')) return <FileText className="h-10 w-10 text-accent-500" />;
    return <File className="h-10 w-10 text-neutral-400" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#eef5ff,_#f8fafc_45%,_#f4f6fb)] px-6 py-10">
      <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-8">
        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-[32px] border border-white/70 bg-gradient-to-br from-[#0f5ed5] via-[#2563eb] to-[#4f46e5] p-8 text-white shadow-[0_30px_80px_rgba(15,94,213,0.25)]"
        >
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-white/70">Secure workspace</p>
              <h1 className="mt-2 text-3xl font-semibold">Document exchange hub</h1>
              <p className="mt-1 text-white/80">
                SOC 2 Type II certified data room • AES-256 encryption • WORM retention
              </p>
            </div>
            <div className="rounded-2xl bg-white/10 px-4 py-3 text-center backdrop-blur">
              <p className="text-sm uppercase tracking-[0.3em] text-white/70">SLA</p>
              <p className="text-2xl font-semibold">4h reviewer turn</p>
            </div>
          </div>
        </motion.section>

        {/* Stats */}
        <section className="grid gap-5 md:grid-cols-3">
          {[
            { label: 'Approved documents', value: stats.approved, meta: 'Ready for auditor download' },
            { label: 'Pending actions', value: stats.pending, meta: 'Awaiting review or upload' },
            { label: 'Data volume', value: formatFileSize(stats.totalSize), meta: 'Encrypted at rest' },
          ].map((card) => (
            <div
              key={card.label}
              className="rounded-3xl border border-white/80 bg-white/95 p-6 shadow-[0_15px_60px_rgba(15,23,42,0.05)] backdrop-blur"
            >
              <p className="text-sm font-medium text-neutral-500">{card.label}</p>
              <p className="mt-2 text-3xl font-semibold text-neutral-900">{card.value}</p>
              <p className="text-sm text-neutral-500">{card.meta}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
          {/* Upload + List */}
          <div className="space-y-6">
            <div className="rounded-[28px] border border-dashed border-primary-200 bg-white/70 p-8 shadow-[0_20px_60px_rgba(37,99,235,0.08)]">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-primary-100 pb-6">
                <div>
                  <p className="text-sm font-semibold text-primary-600">Select category</p>
                  <p className="text-2xl font-semibold text-neutral-900">What are you uploading?</p>
                </div>
                <span className="rounded-full bg-primary-50 px-4 py-2 text-sm font-semibold text-primary-600">
                  Encrypted in transit
                </span>
              </div>
              <div className="mt-6 flex flex-wrap gap-3">
                {categoryPills.map((category) => (
                  <button
                    key={category.value}
                    onClick={() => setSelectedCategory(category.value)}
                    className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${
                      selectedCategory === category.value
                        ? `${category.accent} border border-transparent`
                        : 'bg-neutral-50 text-neutral-600 border border-neutral-100'
                    }`}
                  >
                    {category.label}
                  </button>
                ))}
              </div>
              <label
                htmlFor="document-upload"
                className="mt-8 flex cursor-pointer flex-col items-center justify-center rounded-[24px] border border-dashed border-neutral-300 bg-gradient-to-b from-white to-neutral-50 px-6 py-10 text-center transition hover:border-primary-300"
              >
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50 text-primary-600">
                  <Upload className="h-7 w-7" />
                </div>
                <p className="mt-4 text-xl font-semibold text-neutral-900">
                  {uploading ? 'Uploading files...' : 'Drag files here or browse'}
                </p>
                <p className="text-sm text-neutral-500">PDF, Excel, Word, CSV, Images • up to 50MB each</p>
                <input
                  id="document-upload"
                  type="file"
                  multiple
                  className="hidden"
                  disabled={uploading}
                  accept=".pdf,.xlsx,.xls,.doc,.docx,.csv,.jpg,.jpeg,.png"
                  onChange={handleFileUpload}
                />
                <span className="mt-3 rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-600">
                  Auto virus scan &amp; AI tagging enabled
                </span>
              </label>
            </div>

            <div className="rounded-[28px] border border-white/80 bg-white/95 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.04)]">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold text-neutral-900">Recent uploads</h2>
                <span className="text-sm text-neutral-500">Sorted by newest first</span>
              </div>

              {documents.length === 0 ? (
                <div className="mt-10 flex flex-col items-center gap-4 text-center text-neutral-500">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-neutral-50">
                    <FileText className="h-8 w-8 text-neutral-400" />
                  </div>
                  <p className="text-lg font-medium text-neutral-600">
                    Your secure binder is waiting for documents
                  </p>
                  <p className="text-sm text-neutral-500">
                    Upload financials, controls evidence, tax packages, and more
                  </p>
                </div>
              ) : (
                <div className="mt-6 space-y-4">
                  <AnimatePresence initial={false}>
                    {documents.map((doc) => (
                      <motion.div
                        key={doc.id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -6 }}
                        className="flex flex-wrap items-center gap-4 rounded-2xl border border-neutral-100 bg-neutral-50/60 px-5 py-4"
                      >
                        <div className="flex items-center gap-4">
                          {getFileIcon(doc.fileName)}
                          <div>
                            <p className="text-lg font-semibold text-neutral-900">{doc.fileName}</p>
                            <p className="text-sm text-neutral-500">
                              {categoryPills.find((c) => c.value === doc.category)?.label} •{' '}
                              {formatFileSize(doc.fileSize)}
                            </p>
                          </div>
                        </div>
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadges[doc.status]}`}
                        >
                          {doc.status === 'uploaded' && 'Uploaded'}
                          {doc.status === 'processing' && 'Processing'}
                          {doc.status === 'approved' && 'Approved'}
                          {doc.status === 'rejected' && 'Needs attention'}
                        </span>
                        <div className="ml-auto flex items-center gap-2">
                          <button className="rounded-2xl border border-neutral-200 p-2 text-neutral-600 transition hover:bg-neutral-100">
                            <Download className="h-5 w-5" />
                          </button>
                          <button className="rounded-2xl border border-neutral-200 p-2 text-neutral-600 transition hover:bg-neutral-100">
                            <Trash2 className="h-5 w-5" />
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </div>

          {/* Guidance */}
          <div className="space-y-6">
            <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-primary-500" />
                <div>
                  <p className="text-sm font-semibold text-primary-500">Best practice</p>
                  <p className="text-xl font-semibold text-neutral-900">Submission checklist</p>
                </div>
              </div>
              <ul className="mt-4 space-y-3 text-sm text-neutral-600">
                <li className="flex items-start gap-3 rounded-2xl bg-neutral-50 p-4">
                  <CheckCircle className="mt-0.5 h-4 w-4 text-success-600" />
                  Export reports directly from source systems to preserve metadata.
                </li>
                <li className="flex items-start gap-3 rounded-2xl bg-neutral-50 p-4">
                  <CheckCircle className="mt-0.5 h-4 w-4 text-success-600" />
                  Combine related support (PBC listing, walkthrough notes) into a single upload.
                </li>
                <li className="flex items-start gap-3 rounded-2xl bg-neutral-50 p-4">
                  <CheckCircle className="mt-0.5 h-4 w-4 text-success-600" />
                  Use descriptive naming: `FY24_Q4_BankRec_MainOperating.pdf`.
                </li>
              </ul>
            </div>

            <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Need help?</p>
                  <p className="text-2xl font-semibold text-neutral-900">Concierge document desk</p>
                </div>
                <span className="rounded-full bg-neutral-100 px-4 py-2 text-xs font-semibold text-neutral-600">
                  15 min average response
                </span>
              </div>
              <div className="mt-4 space-y-3 text-sm text-neutral-600">
                <p>• Schedule white-glove onboarding for ERP exports</p>
                <p>• Let us bulk ingest zipped folders up to 10GB</p>
                <p>• Secure portal for third-party confirmations</p>
              </div>
              <button className="mt-6 w-full rounded-2xl bg-neutral-900 py-3 text-sm font-semibold text-white transition hover:bg-neutral-800">
                Message file concierge
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
