import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { FullPageSpinner } from '@/components/ui/Spinner';

export function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <FullPageSpinner />;
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
