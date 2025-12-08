/**
 * Documents Page
 * Upload and manage supporting documents for R&D study
 */

import { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  File,
  FileText,
  Image,
  Trash2,
  Download,
  Eye,
  CheckCircle,
  AlertCircle,
  Loader2,
  FolderOpen,
  Filter,
} from 'lucide-react';
import studyService from '../services/study.service';
import toast from 'react-hot-toast';
import type { RDDocument, DocumentCategory } from '../types';

const categories: { value: DocumentCategory; label: string; icon: React.ElementType }[] = [
  { value: 'project_documentation', label: 'Project Documentation', icon: FileText },
  { value: 'payroll', label: 'Payroll Records', icon: File },
  { value: 'timesheet', label: 'Timesheets', icon: File },
  { value: 'contracts', label: 'Contracts', icon: File },
  { value: 'invoices', label: 'Invoices', icon: File },
  { value: 'other', label: 'Other', icon: File },
];

export default function DocumentsPage() {
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState<RDDocument[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<DocumentCategory | 'all'>('all');
  const [uploadCategory, setUploadCategory] = useState<DocumentCategory>('project_documentation');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await studyService.getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setUploading(true);
      const results = await Promise.allSettled(
        acceptedFiles.map((file) => studyService.uploadDocument(file, uploadCategory))
      );

      const successful = results.filter((r) => r.status === 'fulfilled').length;
      const failed = results.filter((r) => r.status === 'rejected').length;

      if (successful > 0) {
        toast.success(`${successful} file(s) uploaded successfully`);
        loadDocuments();
      }
      if (failed > 0) {
        toast.error(`${failed} file(s) failed to upload`);
      }

      setUploading(false);
    },
    [uploadCategory]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
      'image/*': ['.jpg', '.jpeg', '.png'],
    },
    disabled: uploading,
  });

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await studyService.deleteDocument(documentId);
      setDocuments(documents.filter((d) => d.id !== documentId));
      toast.success('Document deleted');
    } catch {
      toast.error('Failed to delete document');
    }
  };

  const filteredDocuments =
    selectedCategory === 'all'
      ? documents
      : documents.filter((d) => d.category === selectedCategory);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return <FileText className="w-5 h-5 text-red-500" />;
    if (fileType.includes('image')) return <Image className="w-5 h-5 text-blue-500" />;
    if (fileType.includes('spreadsheet') || fileType.includes('excel'))
      return <File className="w-5 h-5 text-green-500" />;
    return <File className="w-5 h-5 text-gray-500" />;
  };

  const getStatusBadge = (status: RDDocument['upload_status']) => {
    switch (status) {
      case 'processed':
        return (
          <span className="flex items-center gap-1 text-green-600 bg-green-100 px-2 py-0.5 rounded-full text-xs">
            <CheckCircle className="w-3 h-3" />
            Processed
          </span>
        );
      case 'processing':
        return (
          <span className="flex items-center gap-1 text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full text-xs">
            <Loader2 className="w-3 h-3 animate-spin" />
            Processing
          </span>
        );
      case 'error':
        return (
          <span className="flex items-center gap-1 text-red-600 bg-red-100 px-2 py-0.5 rounded-full text-xs">
            <AlertCircle className="w-3 h-3" />
            Error
          </span>
        );
      default:
        return null;
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
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <Upload className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
            <p className="text-gray-600">Upload supporting documentation for your R&D activities</p>
          </div>
        </div>
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fluent-card p-6"
      >
        <div className="mb-4">
          <label className="fluent-label">Document Category</label>
          <select
            value={uploadCategory}
            onChange={(e) => setUploadCategory(e.target.value as DocumentCategory)}
            className="fluent-select max-w-xs"
          >
            {categories.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
            ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}
            ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <div className="flex flex-col items-center">
              <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
              <p className="text-gray-600">Uploading documents...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload
                className={`w-12 h-12 mb-4 ${isDragActive ? 'text-primary-600' : 'text-gray-400'}`}
              />
              <p className="text-gray-900 font-medium mb-1">
                {isDragActive ? 'Drop files here' : 'Drag and drop files here'}
              </p>
              <p className="text-sm text-gray-500">
                or click to browse (PDF, Excel, CSV, images)
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Filter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="fluent-card p-4"
      >
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all
                ${selectedCategory === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              All ({documents.length})
            </button>
            {categories.map((cat) => {
              const count = documents.filter((d) => d.category === cat.value).length;
              return (
                <button
                  key={cat.value}
                  onClick={() => setSelectedCategory(cat.value)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all
                    ${selectedCategory === cat.value
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {cat.label} ({count})
                </button>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Documents List */}
      {filteredDocuments.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fluent-card p-12 text-center"
        >
          <FolderOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Documents</h3>
          <p className="text-gray-600">
            {selectedCategory === 'all'
              ? 'Upload your first document to get started'
              : 'No documents in this category'}
          </p>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="fluent-card overflow-hidden"
        >
          <div className="divide-y divide-gray-100">
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                    {getFileIcon(doc.file_type)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{doc.name}</p>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>•</span>
                      <span>
                        {categories.find((c) => c.value === doc.category)?.label || doc.category}
                      </span>
                      <span>•</span>
                      <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(doc.upload_status)}
                  <button className="p-2 hover:bg-gray-100 rounded-lg" title="View">
                    <Eye className="w-4 h-4 text-gray-600" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg" title="Download">
                    <Download className="w-4 h-4 text-gray-600" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 hover:bg-red-50 rounded-lg"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
