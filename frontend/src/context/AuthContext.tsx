import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthContextType, AuthState, LoginCredentials, User } from '../types/auth';
import { authService } from '../services/auth.service';

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
};

export const AuthContext = createContext<AuthContextType>({
  ...initialState,
  login: async () => {},
  logout: () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>(initialState);

  useEffect(() => {
    // Check for stored authentication on mount
    const token = authService.getStoredToken();
    const userStr = authService.getStoredUser();
    
    if (token && userStr) {
      const user = JSON.parse(userStr);
      setState({
        user,
        token,
        isAuthenticated: true,
      });
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const { user, token } = await authService.login(credentials);
      
      // Store authentication data
      authService.setStoredToken(token);
      authService.setStoredUser(user);
      
      setState({
        user,
        token,
        isAuthenticated: true,
      });
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    // Clear stored authentication data
    authService.removeStoredToken();
    authService.removeStoredUser();
    
    setState(initialState);
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
