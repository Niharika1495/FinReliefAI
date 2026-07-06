import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { ArrowLeft, FileQuestion, Copy, Download, RefreshCw, Sparkles, Check } from 'lucide-react';
import { aiApi } from '@/api/ai';
import { renderMarkdown } from '@/utils/markdown';
import toast from 'react-hot-toast';

export default function FinancialExplanationPage() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setResult(null);
    try {
      const apiKey = localStorage.getItem('finrelief_gemini_key');
      const res = await aiApi.generateFinancialExplanation(apiKey);
      const payload = res.data?.data || res.data;
      setResult(payload);
      toast.success('Financial explanation generated!');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Generation failed. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    if (!result?.explanation) return;
    navigator.clipboard.writeText(result.explanation);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!result?.explanation) return;
    const blob = new Blob([result.explanation], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `financial_health_explanation.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Back Header */}
      <div className="flex items-center gap-3">
        <Link to="/ai">
          <Button variant="ghost" size="icon" title="Back"><ArrowLeft size={16} /></Button>
        </Link>
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100 flex items-center gap-2">
            <FileQuestion size={20} className="text-amber-550" /> Financial Explanation
          </h1>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            AI explanation of your debt levels, ratios, and risk score in plain English.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Form */}
        <Card padding="p-5" className="lg:col-span-1 h-fit space-y-4">
          <CardHeader title="Generate Explanation" />
          <p className="text-xs text-surface-500 dark:text-surface-400 leading-relaxed">
            The AI engine reads your active loan records, monthly income, expenses, and calculated debt-to-income (DTI) metrics to construct a comprehensive breakdown of your options.
          </p>
          <Button
            onClick={handleGenerate}
            isLoading={isGenerating}
            className="w-full flex items-center justify-center gap-1.5"
            id="generate-explanation-button"
          >
            <Sparkles size={14} /> Interpret Metrics
          </Button>
        </Card>

        {/* Right Output */}
        <div className="lg:col-span-2 space-y-4">
          <Card padding="p-6" className="min-h-[300px] flex flex-col justify-between">
            {isGenerating ? (
              <div className="flex-1 flex flex-col items-center justify-center py-16 gap-3">
                <Spinner size="lg" />
                <p className="text-sm text-surface-500 animate-pulse">Analyzing portfolio metrics...</p>
              </div>
            ) : result ? (
              <div className="flex flex-col h-full justify-between gap-5">
                <div className="flex justify-between items-center pb-3 border-b border-surface-100 dark:border-surface-700/50 flex-wrap gap-2">
                  <Badge variant="warning">Interpretation Compiled</Badge>
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
                  {renderMarkdown(result?.explanation)}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center py-16 text-surface-400 dark:text-surface-500 text-center gap-2">
                <FileQuestion size={36} className="text-surface-300 dark:text-surface-600" />
                <p className="text-sm">Click Interpret Metrics to compile your overview.</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
