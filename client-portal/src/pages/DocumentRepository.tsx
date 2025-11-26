/**
 * Document Repository
 * Document management with OCR, AI extraction, and organization
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Upload,
  FolderOpen,
  FileText,
  File,
  Image,
  FileSpreadsheet,
  Search,
  Filter,
  Download,
  Trash2,
  Eye,
  Brain,
  Zap,
  Clock,
  User,
  Tag,
  CheckCircle2,
  X,
  Plus,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Document {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadedBy: string;
  uploadedAt: string;
  category: string;
  workpaperRef?: string;
  ocrStatus?: 'pending' | 'completed' | 'failed';
  aiExtracted?: boolean;
  tags: string[];
}

const DocumentRepository: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  // Mock documents
  const mockDocuments: Document[] = [
    {
      id: '1',
      name: 'Trial Balance - Dec 2024.xlsx',
      type: 'spreadsheet',
      size: '2.4 MB',
      uploadedBy: 'Sarah Johnson',
      uploadedAt: '2024-11-20',
      category: 'Financial Statements',
      workpaperRef: 'A-1',
      ocrStatus: 'completed',
      aiExtracted: true,
      tags: ['Trial Balance', 'Q4', 'Financial'],
    },
    {
      id: '2',
      name: 'Bank Statements - November 2024.pdf',
      type: 'pdf',
      size: '5.1 MB',
      uploadedBy: 'John Smith',
      uploadedAt: '2024-11-19',
      category: 'Bank Statements',
      workpaperRef: 'C-1',
      ocrStatus: 'completed',
      aiExtracted: true,
      tags: ['Bank', 'November', 'Cash'],
    },
    {
      id: '3',
      name: 'Accounts Receivable Aging.xlsx',
      type: 'spreadsheet',
      size: '1.8 MB',
      uploadedBy: 'Emily Davis',
      uploadedAt: '2024-11-18',
      category: 'Receivables',
      workpaperRef: 'C-2',
      ocrStatus: 'completed',
      aiExtracted: true,
      tags: ['AR', 'Aging', 'Collections'],
    },
    {
      id: '4',
      name: 'Fixed Asset Schedule.xlsx',
      type: 'spreadsheet',
      size: '980 KB',
      uploadedBy: 'John Smith',
      uploadedAt: '2024-11-17',
      category: 'Fixed Assets',
      workpaperRef: 'D-1',
      tags: ['Fixed Assets', 'Depreciation'],
    },
    {
      id: '5',
      name: 'Revenue Invoices - Sample.pdf',
      type: 'pdf',
      size: '12.3 MB',
      uploadedBy: 'Sarah Johnson',
      uploadedAt: '2024-11-16',
      category: 'Revenue',
      workpaperRef: 'B-1',
      ocrStatus: 'completed',
      aiExtracted: true,
      tags: ['Revenue', 'Invoices', 'Sample'],
    },
  ];

  React.useEffect(() => {
    setDocuments(mockDocuments);
  }, []);

  const categories = [
    'All',
    'Financial Statements',
    'Bank Statements',
    'Receivables',
    'Payables',
    'Revenue',
    'Fixed Assets',
    'Contracts',
    'Other',
  ];

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return FileText;
      case 'spreadsheet':
        return FileSpreadsheet;
      case 'image':
        return Image;
      default:
        return File;
    }
  };

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = categoryFilter === 'all' || doc.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const handleUpload = () => {
    toast.success('Documents uploaded successfully! AI extraction in progress...');
    setUploadModalOpen(false);
  };

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <button
          onClick={() => navigate(`/firm/engagements/${id}/workspace`)}
          className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-neutral-700" />
        </button>
        <div className="flex-1">
          <h1 className="text-display text-neutral-900 mb-1">Document Repository</h1>
          <p className="text-body text-neutral-600">
            Client documents with OCR and AI extraction
          </p>
        </div>
        <button
          onClick={() => setUploadModalOpen(true)}
          className="fluent-btn-primary"
        >
          <Upload className="w-4 h-4" />
          Upload Documents
        </button>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">Total Documents</p>
            <FolderOpen className="w-4 h-4 text-primary-600" />
          </div>
          <p className="text-title-large text-primary-600 font-semibold">{documents.length}</p>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">AI Processed</p>
            <Brain className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-title-large text-purple-600 font-semibold">
            {documents.filter((d) => d.aiExtracted).length}
          </p>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">Linked to Workpapers</p>
            <FileText className="w-4 h-4 text-accent-600" />
          </div>
          <p className="text-title-large text-accent-600 font-semibold">
            {documents.filter((d) => d.workpaperRef).length}
          </p>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-caption text-neutral-600">Total Size</p>
            <FileSpreadsheet className="w-4 h-4 text-success-600" />
          </div>
          <p className="text-title-large text-success-600 font-semibold">22.6 MB</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="fluent-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents..."
              className="fluent-input pl-10"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="fluent-input w-full sm:w-64"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat === 'All' ? 'all' : cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Documents List */}
      <div className="space-y-3">
        {filteredDocuments.map((doc, index) => {
          const Icon = getFileIcon(doc.type);

          return (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="fluent-card p-5 hover:shadow-md transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-primary-100 rounded-fluent flex items-center justify-center flex-shrink-0">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-body-strong text-neutral-900 truncate mb-1">{doc.name}</h3>
                      <div className="flex items-center gap-4 text-caption text-neutral-600">
                        <div className="flex items-center gap-1">
                          <User className="w-3.5 h-3.5" />
                          <span>{doc.uploadedBy}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{new Date(doc.uploadedAt).toLocaleDateString()}</span>
                        </div>
                        <span>{doc.size}</span>
                        {doc.workpaperRef && (
                          <div className="flex items-center gap-1">
                            <FileText className="w-3.5 h-3.5" />
                            <span className="font-medium text-primary-600">{doc.workpaperRef}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {doc.aiExtracted && (
                        <div className="flex items-center gap-1 px-2 py-1 bg-purple-50 border border-purple-200 rounded-fluent">
                          <Brain className="w-3.5 h-3.5 text-purple-600" />
                          <span className="text-caption font-medium text-purple-700">AI Extracted</span>
                        </div>
                      )}
                      {doc.ocrStatus === 'completed' && (
                        <div className="flex items-center gap-1 px-2 py-1 bg-success-50 border border-success-200 rounded-fluent">
                          <CheckCircle2 className="w-3.5 h-3.5 text-success-600" />
                          <span className="text-caption font-medium text-success-700">OCR Done</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-caption px-2 py-0.5 bg-neutral-100 text-neutral-700 rounded-fluent">
                      {doc.category}
                    </span>
                    {doc.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="text-caption px-2 py-0.5 bg-primary-50 text-primary-700 rounded-fluent"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center gap-2">
                    <button className="fluent-btn-secondary text-sm">
                      <Eye className="w-3.5 h-3.5" />
                      View
                    </button>
                    <button className="fluent-btn-secondary text-sm">
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </button>
                    {doc.aiExtracted && (
                      <button className="fluent-btn-secondary text-sm">
                        <Zap className="w-3.5 h-3.5" />
                        AI Insights
                      </button>
                    )}
                    <button className="text-error-600 hover:bg-error-50 px-3 py-1.5 rounded-fluent transition-colors text-sm flex items-center gap-1.5">
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredDocuments.length === 0 && (
        <div className="fluent-card text-center py-16">
          <FolderOpen className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-title text-neutral-900 mb-2">No documents found</h3>
          <p className="text-body text-neutral-600 mb-6">Upload client documents to get started</p>
          <button onClick={() => setUploadModalOpen(true)} className="fluent-btn-primary">
            <Upload className="w-4 h-4" />
            Upload Documents
          </button>
        </div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {uploadModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setUploadModalOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-2xl w-full shadow-fluent-16"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-title-large text-neutral-900">Upload Documents</h2>
                <button
                  onClick={() => setUploadModalOpen(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="border-2 border-dashed border-neutral-300 rounded-fluent-lg p-12 text-center mb-6 hover:border-primary-400 hover:bg-primary-50 transition-all cursor-pointer">
                <Upload className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
                <p className="text-body-strong text-neutral-900 mb-2">
                  Drag and drop files here, or click to browse
                </p>
                <p className="text-caption text-neutral-600">
                  Supported formats: PDF, Excel, Word, Images (Max 50MB per file)
                </p>
              </div>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Category</label>
                  <select className="fluent-input">
                    {categories.filter((c) => c !== 'All').map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Link to Workpaper (Optional)
                  </label>
                  <input
                    type="text"
                    className="fluent-input"
                    placeholder="e.g., A-1, B-2"
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Tags (Optional)
                  </label>
                  <input
                    type="text"
                    className="fluent-input"
                    placeholder="Separate tags with commas"
                  />
                </div>

                <div className="flex items-center gap-2 p-4 bg-purple-50 border border-purple-200 rounded-fluent">
                  <Brain className="w-5 h-5 text-purple-600 flex-shrink-0" />
                  <div className="text-caption text-purple-800">
                    <strong>AI Processing:</strong> Documents will be automatically processed with OCR and data extraction for faster audit procedures.
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-6 border-t border-neutral-200">
                <button onClick={() => setUploadModalOpen(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button onClick={handleUpload} className="fluent-btn-primary flex-1">
                  Upload
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DocumentRepository;
