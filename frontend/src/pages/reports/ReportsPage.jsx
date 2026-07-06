import React, { useState } from 'react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { reportsApi } from '@/api/reports';
import { FileDown, FileText, CheckCircle, HelpCircle, FileSpreadsheet, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ReportsPage() {
  const [downloading, setDownloading] = useState({}); // { 'reportType-format': boolean }

  const handleDownload = async (reportType, format) => {
    const key = `${reportType}-${format}`;
    setDownloading((prev) => ({ ...prev, [key]: true }));
    const loadingToast = toast.loading(`Compiling and downloading ${reportType.toUpperCase()} ${format.toUpperCase()} report...`);
    
    try {
      let res;
      if (format === 'pdf') {
        res = await reportsApi.downloadPdf(reportType);
      } else {
        res = await reportsApi.downloadCsv(reportType);
      }
      
      const blob = new Blob([res.data], {
        type: format === 'pdf' ? 'application/pdf' : 'text/csv;charset=utf-8;'
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `finrelief_${reportType}_report.${format}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success(`${reportType.replace('_', ' ').toUpperCase()} report downloaded successfully!`, { id: loadingToast });
    } catch (err) {
      toast.error(`Failed to generate ${reportType} report.`, { id: loadingToast });
    } finally {
      setDownloading((prev) => ({ ...prev, [key]: false }));
    }
  };

  const REPORT_CARDS = [
    {
      type: 'financial',
      title: 'Financial Health Report',
      desc: 'Includes detailed analysis metrics, DTI/EMI ratios, risk classification score grids, and full plain-English budget advice list.',
      formats: ['pdf', 'csv'],
    },
    {
      type: 'dashboard',
      title: 'Dashboard Metrics Summary',
      desc: 'Export current portfolio aggregates, active loan counts, outstanding averages, and settlement eligibility counts.',
      formats: ['pdf', 'csv'],
    },
    {
      type: 'loan',
      title: 'Loan Liabilities Ledger',
      desc: 'Complete listing of active and inactive loans including lender details, EMI, interest percentages, tenure, and status codes.',
      formats: ['pdf', 'csv'],
    },
    {
      type: 'settlement',
      title: 'Settlement Recommendations Plan',
      desc: 'Summary of settlement targets, eligible savings metrics, payout times, priority scores, and negotiator difficulties list.',
      formats: ['pdf', 'csv'],
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Reports & Exports</h1>
        <p className="text-sm text-surface-500 dark:text-surface-400">
          Compile and download beautifully formatted summaries in PDF or tabular raw data in CSV.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {REPORT_CARDS.map((report) => (
          <Card key={report.type} padding="p-5" className="flex flex-col justify-between hover:border-primary-350 transition-all">
            <div className="space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-xl bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center text-primary-600 dark:text-primary-400">
                  <FileText size={18} />
                </div>
                <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">{report.title}</h3>
              </div>
              <p className="text-sm text-surface-500 dark:text-surface-400 leading-relaxed">{report.desc}</p>
            </div>
            
            <div className="flex gap-2.5 mt-5 pt-4 border-t border-surface-100 dark:border-surface-700/50">
              {report.formats.map((format) => {
                const key = `${report.type}-${format}`;
                const isDown = downloading[key];
                const Icon = format === 'pdf' ? FileDown : FileSpreadsheet;
                return (
                  <Button
                    key={format}
                    variant={format === 'pdf' ? 'primary' : 'outline'}
                    size="sm"
                    className="flex-1 flex items-center justify-center gap-1.5"
                    onClick={() => handleDownload(report.type, format)}
                    disabled={isDown}
                    id={`download-${report.type}-${format}`}
                  >
                    {isDown ? <RefreshCw size={13} className="animate-spin" /> : <Icon size={13} />}
                    <span>Download {format.toUpperCase()}</span>
                  </Button>
                );
              })}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
