import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '@/api/auth';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('finrelief_token'));
  const [isLoading, setIsLoading] = useState(true);

  // On mount — restore session from persisted token
  useEffect(() => {
    const restoreSession = async () => {
      const savedToken = localStorage.getItem('finrelief_token');
      if (!savedToken) {
        setIsLoading(false);
        return;
      }
      try {
        // GET /auth/me returns the UserResponse directly (no data wrapper)
        const res = await authApi.getMe();
        const userData = res.data?.data ?? res.data;
        setUser(userData);
        setToken(savedToken);
      } catch {
        // Token invalid or expired — clear everything
        localStorage.removeItem('finrelief_token');
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    restoreSession();
  }, []);

  /**
   * login(email, password)
   * POST /auth/login → { access_token, token_type, user }
   * Stores the JWT and sets the user from the response.
   */
  const login = useCallback(async (email, password) => {
    // Payload matches backend LoginRequest exactly — only email + password
    const res = await authApi.login({ email, password });
    const responseData = res.data;

    // Backend TokenResponse: { access_token, token_type, user }
    const accessToken = responseData.access_token;
    if (!accessToken) {
      throw new Error('No access token received from server');
    }

    localStorage.setItem('finrelief_token', accessToken);
    setToken(accessToken);

    // Prefer user embedded in login response; fall back to /auth/me call
    let userData = responseData.user ?? null;
    if (!userData) {
      const meRes = await authApi.getMe();
      userData = meRes.data?.data ?? meRes.data;
    }

    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('finrelief_token');
    setToken(null);
    setUser(null);
    toast.success('Logged out successfully');
  }, []);

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: !!token && !!user,
    login,
    logout,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
