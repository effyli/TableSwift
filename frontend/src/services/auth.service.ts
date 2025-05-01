import axios from 'axios';
import { LoginCredentials, LoginResponse } from '../types/auth';

const API_URL = 'http://localhost:80';

axios.defaults.withCredentials = true;

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await axios.post(`${API_URL}/auth/login`, formData, {
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
      await axios.post(`${API_URL}/auth/logout`);
    } catch {
      return
    }
  },
};
