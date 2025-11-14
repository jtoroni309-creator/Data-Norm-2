'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Upload,
  File,
  FileText,
  FileSpreadsheet,
  Image,
  Download,
  Eye,
  Trash2,
  RefreshCw,
  Search,
  Filter,
  FolderOpen,
  Calendar,
  User,
  Tag,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface DocumentManagementProps {
  engagementId: string;
}

interface Document {
  id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  category: string;
  uploaded_by: string;
  uploaded_at: string;
  tags: string[];
  description?: string;
  url?: string;
}

export function DocumentManagement({ engagementId }: DocumentManagementProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null);

  const queryClient = useQueryClient();

  // Fetch documents
  const { data: documents = [], isLoading, refetch } = useQuery({
    queryKey: ['documents', engagementId, selectedCategory],
    queryFn: async () => {
      const params = selectedCategory !== 'all' ? `?category=${selectedCategory}` : '';
      const response = await api.get(`/engagements/${engagementId}/documents${params}`);
      return response.data;
    },
  });

  // Upload document mutation
  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      return api.post(`/engagements/${engagementId}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    onSuccess: () => {
      toast.success('Document uploaded successfully');
      queryClient.invalidateQueries({ queryKey: ['documents', engagementId] });
      setUploadDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    },
  });

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId: string) => {
      return api.delete(`/engagements/${engagementId}/documents/${documentId}`);
    },
    onSuccess: () => {
      toast.success('Document deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['documents', engagementId] });
    },
    onError: () => {
      toast.error('Failed to delete document');
    },
  });

  // Download document mutation
  const downloadMutation = useMutation({
    mutationFn: async (documentId: string) => {
      return api.get(`/engagements/${engagementId}/documents/${documentId}/download`, {
        responseType: 'blob',
      });
    },
    onSuccess: (response, documentId) => {
      const document = documents.find((d: Document) => d.id === documentId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document?.file_name || 'document');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Document downloaded successfully');
    },
    onError: () => {
      toast.error('Failed to download document');
    },
  });

  const categories = [
    { id: 'all', label: 'All Documents', icon: FolderOpen, count: documents.length },
    {
      id: 'financial_statements',
      label: 'Financial Statements',
      icon: FileSpreadsheet,
      count: documents.filter((d: Document) => d.category === 'financial_statements').length,
    },
    {
      id: 'workpapers',
      label: 'Workpapers',
      icon: FileText,
      count: documents.filter((d: Document) => d.category === 'workpapers').length,
    },
    {
      id: 'client_provided',
      label: 'Client Provided',
      icon: Upload,
      count: documents.filter((d: Document) => d.category === 'client_provided').length,
    },
    {
      id: 'confirmations',
      label: 'Confirmations',
      icon: File,
      count: documents.filter((d: Document) => d.category === 'confirmations').length,
    },
    {
      id: 'reports',
      label: 'Reports',
      icon: FileText,
      count: documents.filter((d: Document) => d.category === 'reports').length,
    },
  ];

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return FileText;
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return FileSpreadsheet;
    if (fileType.includes('image')) return Image;
    return File;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const filteredDocuments = documents.filter((doc: Document) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        doc.file_name.toLowerCase().includes(query) ||
        doc.description?.toLowerCase().includes(query) ||
        doc.tags?.some((tag) => tag.toLowerCase().includes(query))
      );
    }
    return true;
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });
    formData.append('category', selectedCategory === 'all' ? 'client_provided' : selectedCategory);

    uploadMutation.mutate(formData);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Document Management</h2>
          <p className="text-gray-600 mt-1">
            Centralized repository for all engagement documents
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => refetch()}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <label>
            <input
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploadMutation.isPending}
            />
            <Button
              as="span"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2 cursor-pointer"
              disabled={uploadMutation.isPending}
            >
              <Upload className="w-4 h-4" />
              {uploadMutation.isPending ? 'Uploading...' : 'Upload Documents'}
            </Button>
          </label>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">{documents.length}</p>
            </div>
            <FolderOpen className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Size</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatFileSize(documents.reduce((sum: number, d: Document) => sum + d.file_size, 0))}
              </p>
            </div>
            <FileText className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">This Month</p>
              <p className="text-2xl font-bold text-gray-900">
                {documents.filter((d: Document) => {
                  const uploaded = new Date(d.uploaded_at);
                  const now = new Date();
                  return uploaded.getMonth() === now.getMonth() && uploaded.getFullYear() === now.getFullYear();
                }).length}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Categories</p>
              <p className="text-2xl font-bold text-gray-900">{categories.length - 1}</p>
            </div>
            <Tag className="w-8 h-8 text-orange-600" />
          </div>
        </Card>
      </div>

      {/* Categories and Search */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Categories */}
        <Card className="md:w-64 p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Categories
          </h3>
          <div className="space-y-1">
            {categories.map((category) => {
              const Icon = category.icon;
              const isSelected = selectedCategory === category.id;

              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${
                    isSelected
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{category.label}</span>
                  </div>
                  <Badge
                    variant="outline"
                    className={`text-xs ${isSelected ? 'border-white text-white' : ''}`}
                  >
                    {category.count}
                  </Badge>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Documents List */}
        <Card className="flex-1">
          {/* Search */}
          <div className="p-4 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Documents */}
          {filteredDocuments.length === 0 ? (
            <div className="p-12 text-center">
              <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500 font-medium">No documents found</p>
              <p className="text-sm text-gray-400 mt-1">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Upload documents to get started'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredDocuments.map((document: Document) => {
                const FileIcon = getFileIcon(document.file_type);

                return (
                  <div key={document.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-blue-100 rounded-lg">
                        <FileIcon className="w-6 h-6 text-blue-600" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-gray-900 truncate mb-1">
                              {document.file_name}
                            </h4>
                            {document.description && (
                              <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                                {document.description}
                              </p>
                            )}
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                {document.uploaded_by}
                              </span>
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(document.uploaded_at).toLocaleDateString()}
                              </span>
                              <span>{formatFileSize(document.file_size)}</span>
                            </div>
                            {document.tags && document.tags.length > 0 && (
                              <div className="flex items-center gap-2 mt-2">
                                {document.tags.map((tag, idx) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setPreviewDocument(document)}
                              className="flex items-center gap-2"
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => downloadMutation.mutate(document.id)}
                              disabled={downloadMutation.isPending}
                              className="flex items-center gap-2"
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deleteMutation.mutate(document.id)}
                              disabled={deleteMutation.isPending}
                              className="flex items-center gap-2 text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>

      {/* Preview Modal */}
      {previewDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{previewDocument.file_name}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {formatFileSize(previewDocument.file_size)} • {previewDocument.category}
                </p>
              </div>
              <button
                onClick={() => setPreviewDocument(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                ×
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1 bg-gray-50">
              <p className="text-gray-500 text-center py-12">
                Preview not available. Click download to view the file.
              </p>
            </div>
            <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
              <Button variant="outline" onClick={() => setPreviewDocument(null)}>
                Close
              </Button>
              <Button
                onClick={() => downloadMutation.mutate(previewDocument.id)}
                disabled={downloadMutation.isPending}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
