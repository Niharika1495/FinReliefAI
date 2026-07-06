import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { SearchBar } from '@/components/ui/SearchBar';
import { adminApi } from '@/api/admin';
import {
  Users, CreditCard, Brain, ShieldAlert, Cpu, HardDrive,
  Activity, Clock, LogOut, RefreshCw, Search, Database, List
} from 'lucide-react';
import { formatCurrency, formatDate } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function AdminDashboardPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'users' | 'loans' | 'logs'
  const [metrics, setMetrics] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [loansList, setLoansList] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await adminApi.getDashboard();
      const payload = res.data?.data || res.data;
      setMetrics(payload);
    } catch {
      toast.error('Failed to load system metrics');
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      const res = await adminApi.getUsers();
      const payload = res.data?.data || res.data;
      setUsersList(Array.isArray(payload) ? payload : []);
    } catch {
      toast.error('Failed to load users');
    }
  }, []);

  const fetchLoans = useCallback(async () => {
    try {
      const res = await adminApi.getLoans();
      const payload = res.data?.data || res.data;
      setLoansList(Array.isArray(payload) ? payload : []);
    } catch {
      toast.error('Failed to load loans');
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    try {
      const res = await adminApi.getAuditLogs();
      const payload = res.data?.data || res.data;
      setAuditLogs(Array.isArray(payload) ? payload : []);
    } catch {
      toast.error('Failed to load audit logs');
    }
  }, []);

  const loadAll = useCallback(async () => {
    setIsLoading(true);
    await Promise.all([
      fetchMetrics(),
      fetchUsers(),
      fetchLoans(),
      fetchAuditLogs(),
    ]);
    setIsLoading(false);
  }, [fetchMetrics, fetchUsers, fetchLoans, fetchAuditLogs]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAll();
    setRefreshing(false);
    toast.success('Admin console refreshed');
  };

  const handleLogout = () => {
    localStorage.removeItem('finrelief_admin_token');
    toast.success('Logged out from admin console');
    navigate('/admin/login');
  };

  // Filter lists based on active tab search
  const filteredUsers = usersList.filter((u) =>
    u.name?.toLowerCase().includes(search.toLowerCase()) ||
    u.email?.toLowerCase().includes(search.toLowerCase())
  );

  const filteredLoans = loansList.filter((l) =>
    l.lender_name?.toLowerCase().includes(search.toLowerCase()) ||
    l.loan_type?.toLowerCase().includes(search.toLowerCase())
  );

  const filteredLogs = auditLogs.filter((log) =>
    log.action?.toLowerCase().includes(search.toLowerCase()) ||
    log.endpoint?.toLowerCase().includes(search.toLowerCase()) ||
    log.ip_address?.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-surface-50 dark:bg-[#09101d] gap-4">
        <Spinner size="xl" />
        <p className="text-sm text-surface-500 animate-pulse">Initializing admin telemetry panel...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-[#09101d] text-surface-900 dark:text-surface-50">
      {/* Header bar */}
      <header className="bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-700/60 sticky top-0 z-30 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-red-500/10 flex items-center justify-center text-red-500">
            <ShieldAlert size={20} />
          </div>
          <div>
            <h1 className="text-base font-bold leading-tight">Admin System Workbench</h1>
            <p className="text-[10px] text-surface-400 uppercase tracking-wider font-semibold">Production Node console</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} /> Refresh
          </Button>
          <Button variant="danger" size="sm" onClick={handleLogout}>
            <LogOut size={14} /> Log Out
          </Button>
        </div>
      </header>

      {/* Main Workbench body */}
      <div className="max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
        {/* Navigation tabs */}
        <div className="flex border-b border-surface-200 dark:border-surface-700">
          {[
            { id: 'overview', label: 'Dashboard Overview' },
            { id: 'users', label: 'Users Management' },
            { id: 'loans', label: 'Loans Auditing' },
            { id: 'logs', label: 'Audit Mutation Logs' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => { setActiveTab(tab.id); setSearch(''); }}
              className={`px-5 py-3 text-sm font-semibold border-b-2 transition-all -mb-px ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-surface-500 hover:text-surface-850 dark:hover:text-surface-150'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: OVERVIEW & TELEMETRY */}
        {activeTab === 'overview' && metrics && (
          <div className="space-y-6">
            {/* KPI Counts */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card padding="p-5" className="flex items-center gap-4">
                <div className="p-3 bg-purple-100 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-xl">
                  <Users size={22} />
                </div>
                <div>
                  <p className="text-xs text-surface-400">Total Users</p>
                  <p className="text-xl font-bold">{metrics.total_users}</p>
                </div>
              </Card>
              <Card padding="p-5" className="flex items-center gap-4">
                <div className="p-3 bg-teal-100 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400 rounded-xl">
                  <CreditCard size={22} />
                </div>
                <div>
                  <p className="text-xs text-surface-400">Active Liabilities</p>
                  <p className="text-xl font-bold">{metrics.total_active_loans}</p>
                </div>
              </Card>
              <Card padding="p-5" className="flex items-center gap-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl">
                  <Brain size={22} />
                </div>
                <div>
                  <p className="text-xs text-surface-400">Total AI queries</p>
                  <p className="text-xl font-bold">{metrics.total_ai_queries}</p>
                </div>
              </Card>
            </div>

            {/* Health Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* CPU */}
              <Card padding="p-5" className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold flex items-center gap-1.5"><Cpu size={14} /> CPU Load</span>
                  <Badge variant={metrics.system_health?.cpu_usage_percent < 75 ? 'success' : 'danger'}>
                    {metrics.system_health?.cpu_usage_percent}%
                  </Badge>
                </div>
                <div className="w-full bg-surface-100 dark:bg-surface-800 h-2 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-500" style={{ width: `${metrics.system_health?.cpu_usage_percent}%` }} />
                </div>
              </Card>

              {/* Memory */}
              <Card padding="p-5" className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold flex items-center gap-1.5"><Activity size={14} /> Memory</span>
                  <Badge variant={metrics.system_health?.memory_usage_percent < 80 ? 'success' : 'danger'}>
                    {metrics.system_health?.memory_usage_percent}%
                  </Badge>
                </div>
                <div className="w-full bg-surface-100 dark:bg-surface-800 h-2 rounded-full overflow-hidden">
                  <div className="h-full bg-teal-500" style={{ width: `${metrics.system_health?.memory_usage_percent}%` }} />
                </div>
              </Card>

              {/* Disk */}
              <Card padding="p-5" className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold flex items-center gap-1.5"><HardDrive size={14} /> Disk Storage</span>
                  <Badge variant={metrics.system_health?.disk_usage_percent < 85 ? 'success' : 'danger'}>
                    {metrics.system_health?.disk_usage_percent}%
                  </Badge>
                </div>
                <div className="w-full bg-surface-100 dark:bg-surface-800 h-2 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500" style={{ width: `${metrics.system_health?.disk_usage_percent}%` }} />
                </div>
              </Card>

              {/* Database */}
              <Card padding="p-5" className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold flex items-center gap-1.5"><Database size={14} /> DB Latency</span>
                  <Badge variant={metrics.system_health?.db_latency_ms >= 0 ? 'success' : 'danger'}>
                    {metrics.system_health?.db_latency_ms >= 0 ? `${metrics.system_health.db_latency_ms.toFixed(1)} ms` : 'Offline'}
                  </Badge>
                </div>
                <div className="text-[10px] text-surface-450 dark:text-surface-550">
                  SQL engine status: <span className="font-semibold text-emerald-500">Connected</span>
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* TAB 2: USERS LIST */}
        {activeTab === 'users' && (
          <Card padding="p-5" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">Registered Users ({filteredUsers.length})</h3>
              <SearchBar value={search} onChange={setSearch} placeholder="Search users by name, email..." className="w-64" />
            </div>
            
            {filteredUsers.length === 0 ? (
              <div className="text-center py-8 text-sm text-surface-400">No users found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Income</th>
                      <th>Expenses</th>
                      <th>Joined</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((u) => (
                      <tr key={u.id}>
                        <td>#{u.id}</td>
                        <td className="font-medium">{u.name}</td>
                        <td>{u.email}</td>
                        <td>{formatCurrency(u.monthly_income)}</td>
                        <td>{formatCurrency(u.monthly_expenses)}</td>
                        <td className="text-xs text-surface-400">{formatDate(u.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        )}

        {/* TAB 3: LOANS LIST */}
        {activeTab === 'loans' && (
          <Card padding="p-5" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">System Loans Ledger ({filteredLoans.length})</h3>
              <SearchBar value={search} onChange={setSearch} placeholder="Search lender, type..." className="w-64" />
            </div>

            {filteredLoans.length === 0 ? (
              <div className="text-center py-8 text-sm text-surface-400">No loans found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>User ID</th>
                      <th>Lender</th>
                      <th>Type</th>
                      <th>Outstanding</th>
                      <th>EMI</th>
                      <th>Interest</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLoans.map((l) => (
                      <tr key={l.id}>
                        <td>User #{l.user_id}</td>
                        <td className="font-medium">{l.lender_name}</td>
                        <td>{l.loan_type}</td>
                        <td className="font-semibold">{formatCurrency(l.outstanding_amount)}</td>
                        <td>{formatCurrency(l.emi)}</td>
                        <td>{l.interest_rate}%</td>
                        <td>
                          <Badge variant={l.loan_status === 'ACTIVE' ? 'success' : 'default'}>
                            {l.loan_status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        )}

        {/* TAB 4: AUDIT LOGS */}
        {activeTab === 'logs' && (
          <Card padding="p-5" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">Audit History ({filteredLogs.length})</h3>
              <SearchBar value={search} onChange={setSearch} placeholder="Search action, IP..." className="w-64" />
            </div>

            {filteredLogs.length === 0 ? (
              <div className="text-center py-8 text-sm text-surface-400">No audit logs found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>User</th>
                      <th>Action</th>
                      <th>IP Address</th>
                      <th>Endpoint</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLogs.map((log) => (
                      <tr key={log.id}>
                        <td className="text-xs text-surface-400">{new Date(log.timestamp).toLocaleString()}</td>
                        <td>{log.user_id ? `User #${log.user_id}` : 'Admin'}</td>
                        <td className="font-medium text-surface-800 dark:text-surface-200">{log.action}</td>
                        <td className="text-xs font-mono">{log.ip_address || '—'}</td>
                        <td className="text-xs font-mono">{log.endpoint || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}
