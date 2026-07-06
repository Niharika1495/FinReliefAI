import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { documentsApi } from '@/api/documents';
import { Upload, FileText, CheckCircle2, AlertTriangle, Trash2, Calendar, DollarSign, Activity, Percent } from 'lucide-react';
import { formatCurrency, formatPercent, formatDate } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function DocumentUploadPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [parsedResult, setParsedResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const fetchDocuments = async () => {
    try {
      const res = await documentsApi.getDocuments();
      const d = res.data;
      setDocuments(Array.isArray(d) ? d : (d.data || []));
    } catch {
      toast.error('Failed to load document upload history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocuments(); }, []);

  const handleUpload = async (file) => {
    if (!file) return;
    
    // Limits: 10MB
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size exceeds the 10MB limit');
      return;
    }

    // Formats: pdf, png, jpg, jpeg
    const allowed = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      toast.error('Only PDF, PNG, and JPEG formats are supported');
      return;
    }

    setUploading(true);
    setProgress(0);
    setParsedResult(null);

    try {
      const res = await documentsApi.upload(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percent);
      });
      
      const payload = res.data?.data || res.data;
      setParsedResult(payload);
      toast.success('Document uploaded and parsed successfully!');
      fetchDocuments();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to process document');
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleUpload(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      <div>
        <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Document Upload & OCR</h1>
        <p className="text-sm text-surface-500 dark:text-surface-400">
          Upload PDF or image statements to automatically parse creditor liability details using OCR.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Column */}
        <div className="lg:col-span-1 space-y-4">
          <Card padding="p-5" className="h-fit">
            <CardHeader title="Upload Statement" />
            
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
                dragActive
                  ? 'border-primary-500 bg-primary-50/20 dark:bg-primary-950/10'
                  : 'border-surface-200 dark:border-surface-700 hover:border-primary-400'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={handleFileChange}
                accept=".pdf,.png,.jpg,.jpeg"
              />
              <Upload size={32} className="text-surface-400 mb-3" />
              <p className="text-sm font-semibold text-surface-800 dark:text-surface-200">
                Drag & drop files here
              </p>
              <p className="text-xs text-surface-400 dark:text-surface-500 mt-1.5">
                or click to browse from files
              </p>
              <p className="text-[10px] text-surface-400 dark:text-surface-500 mt-3">
                PDF, PNG, JPG up to 10MB
              </p>
            </div>

            {uploading && (
              <div className="mt-4 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-surface-500 dark:text-surface-400">Uploading statement...</span>
                  <span className="font-semibold text-primary-500">{progress}%</span>
                </div>
                <div className="w-full bg-surface-100 dark:bg-surface-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-teal-500 transition-all duration-200"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}
          </Card>

          {/* Guidelines info */}
          <Card padding="p-5" className="bg-surface-50 dark:bg-surface-850">
            <h4 className="text-xs font-bold text-surface-700 dark:text-surface-300 uppercase tracking-wider mb-2">OCR Information</h4>
            <ul className="text-xs text-surface-500 dark:text-surface-400 space-y-1.5 list-disc pl-4 leading-relaxed">
              <li>Statements must be readable credit card bills, auto loans, or personal debt notices.</li>
              <li>Includes a fallback mock extractor for test files (e.g. filenames containing "mock" or "test").</li>
              <li>Calculates liability lines automatically after mapping key parameters.</li>
            </ul>
          </Card>
        </div>

        {/* OCR Result Column */}
        <div className="lg:col-span-2 space-y-4">
          {parsedResult ? (
            <Card padding="p-6" className="border-emerald-150 dark:border-emerald-900/30">
              <div className="flex items-center gap-2 pb-4 border-b border-surface-100 dark:border-surface-700/50 mb-4 justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="text-emerald-500" size={18} />
                  <h3 className="text-base font-bold text-surface-900 dark:text-surface-100">OCR Extraction Completed</h3>
                </div>
                <Badge variant="teal">{parsedResult.file_type}</Badge>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-surface-50 dark:bg-surface-750 p-3 rounded-xl">
                  <p className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider">Lender Name</p>
                  <p className="text-sm font-semibold text-surface-800 dark:text-surface-200 mt-0.5">
                    {parsedResult.extracted_lender || 'Not parsed'}
                  </p>
                </div>
                <div className="bg-surface-50 dark:bg-surface-750 p-3 rounded-xl">
                  <p className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider">Outstanding Amount</p>
                  <p className="text-sm font-semibold text-surface-850 dark:text-surface-150 mt-0.5">
                    {formatCurrency(parsedResult.extracted_amount)}
                  </p>
                </div>
                <div className="bg-surface-50 dark:bg-surface-750 p-3 rounded-xl">
                  <p className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider">Monthly EMI</p>
                  <p className="text-sm font-semibold text-surface-800 dark:text-surface-200 mt-0.5">
                    {formatCurrency(parsedResult.extracted_emi)}
                  </p>
                </div>
                <div className="bg-surface-50 dark:bg-surface-750 p-3 rounded-xl">
                  <p className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider">Interest Rate</p>
                  <p className="text-sm font-semibold text-surface-800 dark:text-surface-200 mt-0.5">
                    {formatPercent(parsedResult.extracted_interest_rate)}
                  </p>
                </div>
                <div className="bg-surface-50 dark:bg-surface-750 p-3 rounded-xl">
                  <p className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider">Due Date</p>
                  <p className="text-sm font-semibold text-surface-800 dark:text-surface-200 mt-0.5">
                    {parsedResult.extracted_due_date || '—'}
                  </p>
                </div>
                <div className="bg-surface-50 dark:bg-surface-750 p-3 rounded-xl">
                  <p className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider">Loan Type</p>
                  <p className="text-sm font-semibold text-surface-800 dark:text-surface-200 mt-0.5">
                    {parsedResult.extracted_loan_type || '—'}
                  </p>
                </div>
              </div>
            </Card>
          ) : null}

          {/* Upload History list */}
          <Card padding="p-5">
            <CardHeader title="Upload History" />
            {loading ? (
              <div className="flex justify-center py-8"><Spinner /></div>
            ) : documents.length === 0 ? (
              <div className="text-center py-8 text-sm text-surface-400">
                No uploaded documents found.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Filename</th>
                      <th>Lender</th>
                      <th>Amount</th>
                      <th>Type</th>
                      <th>Uploaded</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.id}>
                        <td className="font-medium text-surface-850 dark:text-surface-150">
                          {doc.filename}
                        </td>
                        <td className="text-surface-600 dark:text-surface-400">
                          {doc.extracted_lender || '—'}
                        </td>
                        <td className="font-semibold text-surface-850 dark:text-surface-150">
                          {formatCurrency(doc.extracted_amount)}
                        </td>
                        <td>
                          <Badge variant="teal">{doc.file_type}</Badge>
                        </td>
                        <td className="text-xs text-surface-400">
                          {formatDate(doc.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
