import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import type { UserRole } from '../../types';

interface Props {
  children: React.ReactNode;
  roles?: UserRole[];
}

export default function ProtectedRoute({ children, roles }: Props) {
  const { user } = useAuth();

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/loans" replace />;
  }

  return <>{children}</>;
}
