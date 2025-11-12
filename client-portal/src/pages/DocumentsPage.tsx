import React, { useState } from 'react';
import {
  Upload,
  FileText,
  Image,
  FileSpreadsheet,
  File,
  CheckCircle,
  Clock,
  AlertCircle,
  Download,
  Trash2,
} from 'lucide-react';
import { documentService } from '../services/document.service';

interface Document {
  id: string;
  fileName: string;
  fileSize: number;
  category: string;
  status: 'uploaded' | 'processing' | 'approved' | 'rejected';
  uploadedAt: string;
}

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('financial_statements');

  const categories = [
    { value: 'financial_statements', label: 'Financial Statements' },
    { value: 'bank_statements', label: 'Bank Statements' },
    { value: 'invoices', label: 'Invoices' },
    { value: 'receipts', label: 'Receipts' },
    { value: 'contracts', label: 'Contracts' },
    { value: 'tax_documents', label: 'Tax Documents' },
    { value: 'payroll', label: 'Payroll Records' },
    { value: 'other', label: 'Other' },
  ];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);

    try {
      for (const file of Array.from(files)) {
        await documentService.uploadDocument(file, selectedCategory, 'engagement-123');

        // Add to local state
        setDocuments((prev) => [
          {
            id: Math.random().toString(),
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
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext || '')) return <Image className="w-8 h-8 text-blue-500" />;
    if (['xlsx', 'xls', 'csv'].includes(ext || '')) return <FileSpreadsheet className="w-8 h-8 text-green-500" />;
    if (['pdf'].includes(ext || '')) return <FileText className="w-8 h-8 text-red-500" />;
    return <File className="w-8 h-8 text-gray-500" />;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'uploaded':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3" />
            Uploaded
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3" />
            Processing
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <AlertCircle className="w-3 h-3" />
            Rejected
          </span>
        );
      default:
        return null;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Document Upload</h1>
          <p className="text-gray-600 mt-2">
            Upload your financial documents securely for audit review
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {uploading ? 'Uploading...' : 'Drop files here or click to browse'}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Supports PDF, Excel, Word, Images (max 50MB per file)
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.xlsx,.xls,.docx,.doc,.jpg,.jpeg,.png,.csv"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
            >
              Select Files
            </label>
          </div>
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Uploaded Documents</h2>
          </div>

          {documents.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p>No documents uploaded yet</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {documents.map((doc) => (
                <div key={doc.id} className="px-6 py-4 hover:bg-gray-50 flex items-center gap-4">
                  {getFileIcon(doc.fileName)}
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{doc.fileName}</h3>
                    <p className="text-sm text-gray-600">
                      {categories.find((c) => c.value === doc.category)?.label} • {formatFileSize(doc.fileSize)}
                    </p>
                  </div>
                  {getStatusBadge(doc.status)}
                  <div className="flex gap-2">
                    <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                      <Download className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
