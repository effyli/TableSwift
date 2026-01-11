import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoutes: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading || isAuthenticated) {
    return <Outlet />;
  }

  return <Navigate to='/login' />;
};
