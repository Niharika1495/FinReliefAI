import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';
import { ArrowLeft, Brain, Copy, Download, RefreshCw, AlertTriangle, Sparkles, Check } from 'lucide-react';
import { useLoans } from '@/hooks/useLoans';
import { aiApi } from '@/api/ai';
import { renderMarkdown } from '@/utils/markdown';
import toast from 'react-hot-toast';

export default function NegotiationStrategyPage() {
  const { allLoans, isLoading: loansLoading } = useLoans();
  const [selectedLoanId, setSelectedLoanId] = useState('');
  const [hardship, setHardship] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Auto-select first loan if available
  useEffect(() => {
    if (allLoans.length > 0 && !selectedLoanId) {
      setSelectedLoanId(allLoans[0].id.toString());
    }
  }, [allLoans, selectedLoanId]);

  const handleGenerate = async () => {
    if (!selectedLoanId) {
      toast.error('Please select a target loan');
      return;
    }
    setIsGenerating(true);
    setResult(null);
    try {
      const apiKey = localStorage.getItem('finrelief_gemini_key');
      const res = await aiApi.generateNegotiationStrategy(
        parseInt(selectedLoanId),
        hardship,
        apiKey
      );
      const payload = res.data?.data || res.data;
      setResult(payload);
      toast.success('Negotiation strategy generated!');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Generation failed. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    if (!result?.strategy) return;
    navigator.clipboard.writeText(result.strategy);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!result?.strategy) return;
    const blob = new Blob([result.strategy], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `negotiation_strategy_loan_${selectedLoanId}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const loanOptions = allLoans.map((l) => ({
    value: l.id.toString(),
    label: `${l.lender_name} (${l.status} - Outstanding: $${l.outstanding_amount.toLocaleString()})`,
  }));

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Back Header */}
      <div className="flex items-center gap-3">
        <Link to="/ai">
          <Button variant="ghost" size="icon" title="Back"><ArrowLeft size={16} /></Button>
        </Link>
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100 flex items-center gap-2">
            <Brain size={20} className="text-purple-500" /> Negotiation Strategy
          </h1>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            Generate custom strategic advice for talking to your creditors.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Form */}
        <Card padding="p-5" className="lg:col-span-1 h-fit space-y-4">
          <CardHeader title="Configuration" />
          
          {loansLoading ? (
            <div className="flex justify-center py-4"><Spinner /></div>
          ) : allLoans.length === 0 ? (
            <div className="text-xs text-amber-500 flex gap-2 items-center">
              <AlertTriangle size={14} /> Add active loans before generating strategies.
            </div>
          ) : (
            <div className="space-y-4">
              <Select
                label="Target Loan"
                options={loanOptions}
                value={selectedLoanId}
                onChange={(e) => setSelectedLoanId(e.target.value)}
                placeholder="Select a loan"
                id="loan-selector"
              />

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-surface-700 dark:text-surface-300">
                  Custom Hardship (Optional)
                </label>
                <textarea
                  value={hardship}
                  onChange={(e) => setHardship(e.target.value)}
                  placeholder="Explain details of job loss, medical conditions, budget cuts..."
                  className="w-full rounded-xl border border-surface-300 dark:border-surface-600 bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500 px-3.5 py-2.5 text-sm h-32 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500"
                  id="hardship-input"
                />
              </div>

              <Button
                onClick={handleGenerate}
                isLoading={isGenerating}
                className="w-full flex items-center justify-center gap-1.5"
                id="generate-strategy-button"
              >
                <Sparkles size={14} /> Generate Strategy
              </Button>
            </div>
          )}
        </Card>

        {/* Right Output */}
        <div className="lg:col-span-2 space-y-4">
          <Card padding="p-6" className="min-h-[300px] flex flex-col justify-between">
            {isGenerating ? (
              <div className="flex-1 flex flex-col items-center justify-center py-16 gap-3">
                <Spinner size="lg" />
                <p className="text-sm text-surface-500 animate-pulse">Consulting AI model...</p>
              </div>
            ) : result ? (
              <div className="flex flex-col h-full justify-between gap-5">
                <div className="flex justify-between items-center pb-3 border-b border-surface-100 dark:border-surface-700/50 flex-wrap gap-2">
                  <Badge variant="primary">Strategy Generated</Badge>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" onClick={handleCopy} title="Copy response">
                      {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
                    </Button>
                    <Button variant="ghost" size="icon" onClick={handleDownload} title="Download response">
                      <Download size={14} />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={handleGenerate} title="Regenerate">
                      <RefreshCw size={14} />
                    </Button>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto max-h-[500px] pr-2">
                  {renderMarkdown(result?.strategy)}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center py-16 text-surface-400 dark:text-surface-500 text-center gap-2">
                <Brain size={36} className="text-surface-300 dark:text-surface-600" />
                <p className="text-sm">Enter configuration parameters and click Generate.</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
