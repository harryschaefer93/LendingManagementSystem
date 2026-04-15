import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import { useAuth } from '../../contexts/AuthContext';
import type { UserRole } from '../../types';
import ErrorBoundary from '../common/ErrorBoundary';

export default function AppLayout({ children }: { children: ReactNode }) {
  const { user, switchRole } = useAuth();

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-area">
        <header className="header">
          <div className="role-switcher">
            <label>Role:</label>
            <select value={user.role} onChange={(e) => switchRole(e.target.value as UserRole)}>
              <option value="officer">Loan Officer</option>
              <option value="underwriter">Underwriter</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div className="user-info">
            {user.name} ({user.role})
          </div>
        </header>
        <main className="content">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
