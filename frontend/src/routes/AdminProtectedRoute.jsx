import { Navigate, Outlet } from 'react-router-dom';

export function AdminProtectedRoute() {
  const isAdminAuthenticated = !!localStorage.getItem('finrelief_admin_token');

  if (!isAdminAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return <Outlet />;
}
