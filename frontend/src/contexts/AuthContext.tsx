import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { User, UserRole } from '../types';

const MOCK_USERS: Record<UserRole, User> = {
  officer: { id: 'officer-1', name: 'Jane Smith', role: 'officer' },
  underwriter: { id: 'underwriter-1', name: 'Sarah Johnson', role: 'underwriter' },
  admin: { id: 'admin-1', name: 'Alex Admin', role: 'admin' },
};

interface AuthContextType {
  user: User;
  switchRole: (role: UserRole) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>(() => {
    const stored = localStorage.getItem('lms_mock_user');
    if (stored) {
      try {
        return JSON.parse(stored) as User;
      } catch {
        // fall through
      }
    }
    const defaultUser = MOCK_USERS.officer;
    localStorage.setItem('lms_mock_user', JSON.stringify(defaultUser));
    return defaultUser;
  });

  const switchRole = useCallback((role: UserRole) => {
    const newUser = MOCK_USERS[role];
    setUser(newUser);
    localStorage.setItem('lms_mock_user', JSON.stringify(newUser));
  }, []);

  return (
    <AuthContext.Provider value={{ user, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
