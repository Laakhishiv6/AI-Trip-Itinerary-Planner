import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';

interface StoredUser extends User {
  password: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('voyonata_user');
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem('voyonata_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    const users: StoredUser[] = JSON.parse(localStorage.getItem('voyonata_users') || '[]');
    const found = users.find(u => u.email === email && u.password === password);
    if (!found) return false;

    const userData: User = { name: found.name, email: found.email };
    setUser(userData);
    localStorage.setItem('voyonata_user', JSON.stringify(userData));
    return true;
  };

  const signup = async (name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    const users: StoredUser[] = JSON.parse(localStorage.getItem('voyonata_users') || '[]');
    if (users.find(u => u.email === email)) {
      return { success: false, error: 'An account with this email already exists.' };
    }

    users.push({ name, email, password });
    localStorage.setItem('voyonata_users', JSON.stringify(users));

    const userData: User = { name, email };
    setUser(userData);
    localStorage.setItem('voyonata_user', JSON.stringify(userData));
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('voyonata_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
