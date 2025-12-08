/**
 * Tax Returns Page
 * Upload and manage prior year tax returns (2 years required)
 */

import { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  Upload,
  Trash2,
  CheckCircle,
  AlertCircle,
  Loader2,
  Download,
  Eye,
  Calendar,
  Info,
  File,
} from 'lucide-react';
import studyService from '../services/study.service';
import toast from 'react-hot-toast';
import type { TaxReturn } from '../types';

export default function TaxReturnsPage() {
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [taxReturns, setTaxReturns] = useState<TaxReturn[]>([]);
  const currentYear = new Date().getFullYear();
  const requiredYears = [currentYear - 1, currentYear - 2];

  useEffect(() => {
    loadTaxReturns();
  }, []);

  const loadTaxReturns = async () => {
    try {
      const data = await studyService.getTaxReturns();
      setTaxReturns(data);
    } catch (error) {
      console.error('Failed to load tax returns:', error);
      toast.error('Failed to load tax returns');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[], year: number) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);

    try {
      const uploaded = await studyService.uploadTaxReturn(file, year);
      setTaxReturns([...taxReturns, uploaded]);
      toast.success(`${year} tax return uploaded successfully`);
    } catch {
      toast.error('Failed to upload tax return');
    } finally {
      setUploading(false);
    }
  }, [taxReturns]);

  const handleDelete = async (taxReturnId: string) => {
    if (!confirm('Are you sure you want to delete this tax return?')) return;

    try {
      await studyService.deleteTaxReturn(taxReturnId);
      setTaxReturns(taxReturns.filter((t) => t.id !== taxReturnId));
      toast.success('Tax return deleted');
    } catch {
      toast.error('Failed to delete tax return');
    }
  };

  const getStatusBadge = (status: TaxReturn['upload_status']) => {
    switch (status) {
      case 'processed':
        return (
          <span className="flex items-center gap-1 text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs font-medium">
            <CheckCircle className="w-3 h-3" />
            Processed
          </span>
        );
      case 'processing':
        return (
          <span className="flex items-center gap-1 text-blue-600 bg-blue-100 px-2 py-1 rounded-full text-xs font-medium">
            <Loader2 className="w-3 h-3 animate-spin" />
            Processing
          </span>
        );
      case 'error':
        return (
          <span className="flex items-center gap-1 text-red-600 bg-red-100 px-2 py-1 rounded-full text-xs font-medium">
            <AlertCircle className="w-3 h-3" />
            Error
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-gray-600 bg-gray-100 px-2 py-1 rounded-full text-xs font-medium">
            <Upload className="w-3 h-3" />
            Pending
          </span>
        );
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Tax Returns</h1>
            <p className="text-gray-600">Upload your company's prior 2 years of tax returns</p>
          </div>
        </div>
      </motion.div>

      {/* Info Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="fluent-card p-4 bg-blue-50 border-blue-200"
      >
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900">Why do we need tax returns?</p>
            <p className="text-sm text-blue-800 mt-1">
              Prior year tax returns help calculate base amounts for the R&D credit and verify
              qualified research expenses. We need the prior 2 years to determine the correct
              credit calculation method.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Required Years Upload Sections */}
      <div className="space-y-4">
        {requiredYears.map((year, index) => {
          const existingReturn = taxReturns.find((t) => t.tax_year === year);

          return (
            <motion.div
              key={year}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * (index + 2) }}
              className="fluent-card overflow-hidden"
            >
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  <h3 className="font-semibold text-gray-900">{year} Tax Return</h3>
                  {!existingReturn && (
                    <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">
                      Required
                    </span>
                  )}
                </div>
                {existingReturn && getStatusBadge(existingReturn.upload_status)}
              </div>

              {existingReturn ? (
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                        <File className="w-5 h-5 text-red-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{existingReturn.file_name}</p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(existingReturn.file_size)} • Uploaded{' '}
                          {new Date(existingReturn.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="p-2 hover:bg-gray-100 rounded-lg" title="View">
                        <Eye className="w-4 h-4 text-gray-600" />
                      </button>
                      <button className="p-2 hover:bg-gray-100 rounded-lg" title="Download">
                        <Download className="w-4 h-4 text-gray-600" />
                      </button>
                      <button
                        onClick={() => handleDelete(existingReturn.id)}
                        className="p-2 hover:bg-red-50 rounded-lg"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>

                  {/* Extracted Data Preview */}
                  {existingReturn.processing_result && (
                    <div className="mt-4 p-4 bg-green-50 rounded-xl">
                      <p className="text-sm font-medium text-green-800 mb-2">AI Extracted Data:</p>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        {existingReturn.processing_result.extracted_data.gross_receipts && (
                          <div>
                            <span className="text-gray-600">Gross Receipts:</span>{' '}
                            <span className="font-medium text-gray-900">
                              ${existingReturn.processing_result.extracted_data.gross_receipts.toLocaleString()}
                            </span>
                          </div>
                        )}
                        {existingReturn.processing_result.extracted_data.wages_reported && (
                          <div>
                            <span className="text-gray-600">Wages Reported:</span>{' '}
                            <span className="font-medium text-gray-900">
                              ${existingReturn.processing_result.extracted_data.wages_reported.toLocaleString()}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <TaxReturnDropzone year={year} onDrop={onDrop} uploading={uploading} />
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Completion Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className={`fluent-card p-4 ${
          taxReturns.length >= 2
            ? 'bg-green-50 border-green-200'
            : 'bg-orange-50 border-orange-200'
        }`}
      >
        <div className="flex items-center gap-3">
          {taxReturns.length >= 2 ? (
            <>
              <CheckCircle className="w-6 h-6 text-green-600" />
              <div>
                <p className="font-medium text-green-800">Tax Returns Complete</p>
                <p className="text-sm text-green-700">
                  All required tax returns have been uploaded
                </p>
              </div>
            </>
          ) : (
            <>
              <AlertCircle className="w-6 h-6 text-orange-600" />
              <div>
                <p className="font-medium text-orange-800">Missing Tax Returns</p>
                <p className="text-sm text-orange-700">
                  Please upload {2 - taxReturns.length} more tax return(s) to complete this section
                </p>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}

// Dropzone component for tax return upload
function TaxReturnDropzone({
  year,
  onDrop,
  uploading,
}: {
  year: number;
  onDrop: (files: File[], year: number) => void;
  uploading: boolean;
}) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => onDrop(files, year),
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div
      {...getRootProps()}
      className={`p-8 m-4 border-2 border-dashed rounded-xl text-center cursor-pointer transition-all
        ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}
        ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div className="flex flex-col items-center">
          <Loader2 className="w-10 h-10 text-primary-600 animate-spin mb-3" />
          <p className="text-gray-600">Uploading tax return...</p>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <Upload className={`w-10 h-10 mb-3 ${isDragActive ? 'text-primary-600' : 'text-gray-400'}`} />
          <p className="text-gray-900 font-medium mb-1">
            {isDragActive ? 'Drop the file here' : `Upload ${year} Tax Return`}
          </p>
          <p className="text-sm text-gray-500">
            Drag and drop or click to select (PDF or image)
          </p>
        </div>
      )}
    </div>
  );
}
