import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthContextType, AuthState, LoginCredentials } from '../types/auth';
import { authService } from '../services/auth.service';
import { userService } from '../services/user.service';

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  loading: true,
};

export const AuthContext = createContext<AuthContextType>({
  ...initialState,
  login: async () => {},
  logout: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>(initialState);

  useEffect(() => {
    // Get csrf token
    (async () => {
      try {
        await authService.getCsrfToken();
      } catch (error) {
        console.error('Failed to get CSRF token:', error);
      }
    })();

    // Check if the user is authenticated
    (async () => {
      try {
        const user = await userService.getCurrentUser();
        setState({
          user,
          isAuthenticated: user !== null,
          loading: false,
        });
      } catch {
        setState({
          ...initialState,
          loading: false,
        });
      }
    })();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const { user } = await authService.login(credentials);
      
      setState({
        user,
        isAuthenticated: true,
        loading: false,
      });
    } catch (error) {
      setState(prev => ({ ...prev, loading: false }));
      throw error;
    }
  };

  const logout = async () => {
    setState(prev => ({ ...prev, loading: true }));
    await authService.logout();
    setState({
      ...initialState,
      loading: false,
    });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
