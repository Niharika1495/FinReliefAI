import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/context/AuthContext';
import { ThemeProvider } from '@/context/ThemeContext';
import { AppLayout } from '@/layouts/AppLayout';
import { AuthLayout } from '@/layouts/AuthLayout';
import { ProtectedRoute } from '@/routes/ProtectedRoute';
import { PublicRoute } from '@/routes/PublicRoute';
import { AdminProtectedRoute } from '@/routes/AdminProtectedRoute';
import { FullPageSpinner } from '@/components/ui/Spinner';

// Safe lazy helper to auto-reload page if chunk loading fails due to a new deployment
function safeLazy(importFn) {
  return lazy(() =>
    importFn().catch((err) => {
      if (err.name === 'ChunkLoadError' || err.message?.includes('Failed to fetch dynamically imported module')) {
        window.location.reload();
        return { default: () => null };
      }
      throw err;
    })
  );
}

// Lazy-loaded pages
const LoginPage = safeLazy(() => import('@/pages/auth/LoginPage'));
const RegisterPage = safeLazy(() => import('@/pages/auth/RegisterPage'));
const DashboardPage = safeLazy(() => import('@/pages/dashboard/DashboardPage'));
const LoansPage = safeLazy(() => import('@/pages/loans/LoansPage'));
const LoanDetailPage = safeLazy(() => import('@/pages/loans/LoanDetailPage'));
const FinancialAnalysisPage = safeLazy(() => import('@/pages/analysis/FinancialAnalysisPage'));
const SettlementPage = safeLazy(() => import('@/pages/settlement/SettlementPage'));
const ProfilePage = safeLazy(() => import('@/pages/profile/ProfilePage'));
const NotificationsPage = safeLazy(() => import('@/pages/notifications/NotificationsPage'));
const ReportsPage = safeLazy(() => import('@/pages/reports/ReportsPage'));
const DocumentUploadPage = safeLazy(() => import('@/pages/documents/DocumentUploadPage'));

// AI Workspace pages
const AIDashboardPage = safeLazy(() => import('@/pages/ai/AIDashboardPage'));
const NegotiationStrategyPage = safeLazy(() => import('@/pages/ai/NegotiationStrategyPage'));
const SettlementLetterPage = safeLazy(() => import('@/pages/ai/SettlementLetterPage'));
const NegotiationEmailPage = safeLazy(() => import('@/pages/ai/NegotiationEmailPage'));
const FinancialExplanationPage = safeLazy(() => import('@/pages/ai/FinancialExplanationPage'));
const AIHistoryPage = safeLazy(() => import('@/pages/ai/AIHistoryPage'));

// Admin pages
const AdminLoginPage = safeLazy(() => import('@/pages/admin/AdminLoginPage'));
const AdminDashboardPage = safeLazy(() => import('@/pages/admin/AdminDashboardPage'));

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<FullPageSpinner />}>
            <Routes>
              {/* Public routes — redirect to dashboard if logged in */}
              <Route element={<PublicRoute />}>
                <Route element={<AuthLayout />}>
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                </Route>
                <Route path="/admin/login" element={<AdminLoginPage />} />
              </Route>

              {/* Protected routes — redirect to login if not authenticated */}
              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/loans" element={<LoansPage />} />
                  <Route path="/loans/:id" element={<LoanDetailPage />} />
                  <Route path="/analysis" element={<FinancialAnalysisPage />} />
                  <Route path="/settlement" element={<SettlementPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/notifications" element={<NotificationsPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/documents" element={<DocumentUploadPage />} />
                  <Route path="/ai" element={<AIDashboardPage />} />
                  <Route path="/ai/negotiation-strategy" element={<NegotiationStrategyPage />} />
                  <Route path="/ai/settlement-letter" element={<SettlementLetterPage />} />
                  <Route path="/ai/negotiation-email" element={<NegotiationEmailPage />} />
                  <Route path="/ai/financial-explanation" element={<FinancialExplanationPage />} />
                  <Route path="/ai/history" element={<AIHistoryPage />} />
                </Route>
              </Route>

              {/* Admin Protected routes */}
              <Route element={<AdminProtectedRoute />}>
                <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
              </Route>

              {/* Catch-all redirect */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>

          <Toaster
            position="top-right"
            gutter={8}
            containerStyle={{ top: 16, right: 16 }}
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--toast-bg, #ffffff)',
                color: 'var(--toast-color, #0f172a)',
                borderRadius: '12px',
                border: '1px solid rgba(0,0,0,0.06)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                fontSize: '13px',
                fontWeight: '500',
                padding: '12px 16px',
              },
              success: {
                iconTheme: { primary: '#10b981', secondary: '#fff' },
              },
              error: {
                iconTheme: { primary: '#ef4444', secondary: '#fff' },
              },
            }}
          />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
