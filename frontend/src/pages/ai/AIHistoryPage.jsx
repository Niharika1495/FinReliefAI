import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Select } from '@/components/ui/Select';
import { SearchBar } from '@/components/ui/SearchBar';
import { Spinner } from '@/components/ui/Spinner';
import { ArrowLeft, History, Calendar, Brain, Copy, Download, Search, Check, FileText } from 'lucide-react';
import { aiApi } from '@/api/ai';
import { renderMarkdown } from '@/utils/markdown';
import { formatDate } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function AIHistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await aiApi.getHistory();
        const d = res.data;
        const list = Array.isArray(d) ? d : (d.data || []);
        setHistory(list);

        // Check if there is an ID in search query
        const queryId = searchParams.get('id');
        if (queryId) {
          setSelectedId(parseInt(queryId));
        } else if (list.length > 0) {
          setSelectedId(list[0].id);
        }
      } catch {
        toast.error('Failed to load AI history');
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, [searchParams]);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!selectedId) return;
      setDetailLoading(true);
      try {
        const res = await aiApi.getHistoryDetail(selectedId);
        const d = res.data;
        setSelectedItem(d.data || d);
      } catch {
        toast.error('Failed to load details');
      } finally {
        setDetailLoading(false);
      }
    };
    fetchDetail();
  }, [selectedId]);

  const handleCopy = () => {
    if (!selectedItem?.response) return;
    navigator.clipboard.writeText(selectedItem.response);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!selectedItem?.response) return;
    const blob = new Blob([selectedItem.response], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `ai_response_${selectedItem.prompt_type}_${selectedItem.id}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filter history
  const filtered = history.filter((item) => {
    const matchesSearch = item.prompt?.toLowerCase().includes(search.toLowerCase()) || 
                          item.prompt_type?.toLowerCase().includes(search.toLowerCase());
    const matchesType = !filterType || item.prompt_type === filterType;
    return matchesSearch && matchesType;
  });

  const promptTypes = [
    { value: 'negotiation_strategy', label: 'Negotiation Strategy' },
    { value: 'settlement_letter', label: 'Settlement Letter' },
    { value: 'negotiation_email', label: 'Negotiation Email' },
    { value: 'financial_explanation', label: 'Financial Explanation' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back Header */}
      <div className="flex items-center gap-3">
        <Link to="/ai">
          <Button variant="ghost" size="icon" title="Back"><ArrowLeft size={16} /></Button>
        </Link>
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100 flex items-center gap-2">
            <History size={20} className="text-primary-500" /> AI Generation History
          </h1>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            Access past template correspondence and strategizing guides.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex flex-col gap-2.5">
            <SearchBar
              value={search}
              onChange={setSearch}
              placeholder="Search history prompts..."
            />
            <Select
              options={promptTypes}
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              placeholder="All AI Types"
            />
          </div>

          <Card padding="p-2" className="overflow-y-auto max-h-[600px] space-y-1">
            {isLoading ? (
              <div className="flex justify-center py-8"><Spinner /></div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-8 text-sm text-surface-400">
                No logs found.
              </div>
            ) : (
              filtered.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setSelectedId(item.id);
                    setSearchParams({ id: item.id.toString() });
                  }}
                  className={`w-full text-left p-3 rounded-xl transition-all flex flex-col gap-1.5 border border-transparent ${
                    selectedId === item.id
                      ? 'bg-primary-50 dark:bg-primary-950/30 border-primary-100 dark:border-primary-900/40 text-primary-900 dark:text-primary-100'
                      : 'hover:bg-surface-50 dark:hover:bg-surface-800/50'
                  }`}
                >
                  <div className="flex justify-between items-center w-full gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider block opacity-75 truncate capitalize">
                      {item.prompt_type?.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] text-surface-400 dark:text-surface-500 flex-shrink-0 flex items-center gap-1">
                      <Calendar size={10} /> {formatDate(item.created_at)}
                    </span>
                  </div>
                  <p className="text-xs text-surface-500 dark:text-surface-400 line-clamp-2">
                    {item.prompt}
                  </p>
                </button>
              ))
            )}
          </Card>
        </div>

        {/* Right Detail Preview */}
        <div className="lg:col-span-2">
          <Card padding="p-6" className="min-h-[450px] flex flex-col justify-between">
            {detailLoading ? (
              <div className="flex-1 flex flex-col items-center justify-center py-20 gap-3">
                <Spinner size="lg" />
                <p className="text-sm text-surface-500">Retrieving details...</p>
              </div>
            ) : selectedItem ? (
              <div className="flex flex-col h-full justify-between gap-6">
                {/* Detail Header */}
                <div className="flex justify-between items-center pb-4 border-b border-surface-100 dark:border-surface-700/50 flex-wrap gap-2">
                  <div>
                    <h2 className="text-base font-bold text-surface-900 dark:text-surface-100 capitalize">
                      {selectedItem.prompt_type?.replace(/_/g, ' ')}
                    </h2>
                    <span className="text-xs text-surface-400 flex items-center gap-1 mt-0.5">
                      <Calendar size={12} /> Stored on {formatDate(selectedItem.created_at)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" onClick={handleCopy} title="Copy response">
                      {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
                    </Button>
                    <Button variant="ghost" size="icon" onClick={handleDownload} title="Download response">
                      <Download size={14} />
                    </Button>
                  </div>
                </div>

                {/* Prompt block */}
                <div className="bg-surface-50 dark:bg-surface-850 p-3.5 rounded-xl border border-surface-150 dark:border-surface-750">
                  <span className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider block mb-1">Generated Prompt</span>
                  <p className="text-xs text-surface-700 dark:text-surface-300 leading-relaxed font-mono">
                    {selectedItem.prompt}
                  </p>
                </div>

                {/* Markdown content */}
                <div className="flex-1 overflow-y-auto max-h-[420px] pr-2">
                  <span className="text-[10px] text-surface-400 font-semibold uppercase tracking-wider block mb-3 border-b pb-1">Response Payload</span>
                  {selectedItem.prompt_type === 'negotiation_email' && selectedItem.response?.includes('subject') ? (
                    // Display formatted email layout if it was parsed
                    <div className="space-y-4">
                      <div className="bg-surface-50 dark:bg-surface-850 p-3 rounded-lg text-sm font-semibold">
                        {selectedItem.response}
                      </div>
                    </div>
                  ) : (
                    renderMarkdown(selectedItem.response)
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center py-20 text-surface-400 text-center gap-2">
                <History size={40} className="text-surface-300 dark:text-surface-650" />
                <p className="text-sm">Select an item from history to view details.</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
