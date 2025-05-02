import { LoginCredentials, LoginResponse } from '../types/auth';
import axiosInstance from './axios.config';

export const authService = {
  async getCsrfToken(): Promise<void> {
    try {
      await axiosInstance.get('/csrf-token');
    } catch (error) {
      throw new Error('Failed to get CSRF token');
    }
  },

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await axiosInstance.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      
      return {
        user: response.data
      };
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Invalid credentials');
    }
  },

  async logout(): Promise<void> {
    try {
      await axiosInstance.post('/auth/logout');
    } catch {
      return;
    }
  },
};
