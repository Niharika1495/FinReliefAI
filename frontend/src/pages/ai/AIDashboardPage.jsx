import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { aiApi } from '@/api/ai';
import { Brain, FileText, Mail, FileQuestion, History, ArrowRight, Key, Sparkles } from 'lucide-react';
import { formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function AIDashboardPage() {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('finrelief_gemini_key') || '');
  const [showKeyInput, setShowKeyInput] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await aiApi.getHistory();
        const d = res.data;
        setHistory(Array.isArray(d) ? d : (d.data || []));
      } catch {
        toast.error('Failed to load AI history');
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const saveKey = () => {
    localStorage.setItem('finrelief_gemini_key', geminiKey);
    toast.success(geminiKey ? 'Gemini API key saved locally' : 'Gemini API key cleared');
    setShowKeyInput(false);
  };

  const AI_TOOLS = [
    {
      title: 'Negotiation Strategy',
      desc: 'Build customized points & talking strategies to compromise with creditors.',
      path: '/ai/negotiation-strategy',
      icon: Brain,
      color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
    },
    {
      title: 'Settlement Proposal Letter',
      desc: 'Generate formal request letters specifying target lump sum settlement options.',
      path: '/ai/settlement-letter',
      icon: FileText,
      color: 'bg-teal-100 text-teal-600 dark:bg-teal-900/20 dark:text-teal-400',
    },
    {
      title: 'Creditor Proposal Email',
      desc: 'Draft short settlement compromise emails for fast, written negotiation.',
      path: '/ai/negotiation-email',
      icon: Mail,
      color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
    },
    {
      title: 'Financial Health Explanation',
      desc: 'Interpret debt ratios and repayment limits in simple English terms.',
      path: '/ai/financial-explanation',
      icon: FileQuestion,
      color: 'bg-amber-100 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100 flex items-center gap-2">
            <Sparkles size={20} className="text-primary-500" /> AI Workspace
          </h1>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            Generate strategic negotiation communications and metrics guides powered by Gemini.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowKeyInput(!showKeyInput)}
          className="flex items-center gap-1.5"
          id="toggle-api-key-button"
        >
          <Key size={14} /> {geminiKey ? 'Update API Key' : 'Add Gemini Key'}
        </Button>
      </div>

      {/* API Key Modal/Input panel */}
      {showKeyInput && (
        <Card className="border-primary-100 dark:border-primary-850">
          <div className="space-y-3">
            <p className="text-sm font-semibold text-surface-900 dark:text-surface-100">Optional: Custom Gemini API Key</p>
            <p className="text-xs text-surface-500 dark:text-surface-400">
              Provide your own Google Gemini API key to avoid platform request limit thresholds. Your key remains stored safely in your local browser storage.
            </p>
            <div className="flex gap-2">
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="flex-1 px-3 py-2 text-sm rounded-xl border border-surface-300 dark:border-surface-650 bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                id="gemini-key-input"
              />
              <Button onClick={saveKey} id="save-gemini-key-button">Save</Button>
            </div>
          </div>
        </Card>
      )}

      {/* Tools grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {AI_TOOLS.map((tool) => {
          const Icon = tool.icon;
          return (
            <Card key={tool.path} padding="p-5" className="hover:border-primary-350 dark:hover:border-primary-750 transition-all flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl ${tool.color}`}>
                    <Icon size={20} />
                  </div>
                  <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">{tool.title}</h3>
                </div>
                <p className="text-sm text-surface-500 dark:text-surface-400">{tool.desc}</p>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-100 dark:border-surface-700/50 flex justify-end">
                <Link to={tool.path}>
                  <Button variant="outline" size="sm" className="flex items-center gap-1.5">
                    Launch <ArrowRight size={14} />
                  </Button>
                </Link>
              </div>
            </Card>
          );
        })}
      </div>

      {/* History section */}
      <Card padding="p-5">
        <CardHeader
          title="Recent AI Generations"
          action={
            <Link to="/ai/history" className="text-xs font-semibold text-primary-500 hover:underline flex items-center gap-1">
              <History size={12} /> View All History
            </Link>
          }
        />
        {isLoading ? (
          <div className="space-y-2 py-4">
            <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded w-2/3 animate-pulse" />
            <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded w-1/2 animate-pulse" />
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-sm text-surface-400 dark:text-surface-500">
            No history log entries yet. Launch one of the generators above.
          </div>
        ) : (
          <div className="space-y-3">
            {history.slice(0, 5).map((h) => (
              <Link to={`/ai/history?id=${h.id}`} key={h.id} className="block">
                <div className="flex items-center justify-between p-3 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700/30 transition-all border border-transparent hover:border-surface-100 dark:hover:border-surface-700/50">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-surface-100 dark:bg-surface-700/60 flex items-center justify-center flex-shrink-0 text-surface-500">
                      <Sparkles size={14} className="text-primary-500" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-surface-900 dark:text-surface-100 capitalize truncate">
                        {h.prompt_type?.replace(/_/g, ' ')}
                      </p>
                      <p className="text-xs text-surface-400 dark:text-surface-500 truncate">
                        {h.prompt}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-surface-400 dark:text-surface-500">
                      {formatRelativeTime(h.created_at)}
                    </span>
                    <ArrowRight size={14} className="text-surface-400" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
