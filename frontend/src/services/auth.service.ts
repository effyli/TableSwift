import axios from 'axios';
import { LoginCredentials, LoginResponse } from '../types/auth';

const API_URL = 'http://localhost:80/api'; // Replace with your actual API URL

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      // Convert credentials to FormData as expected by the backend
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await axios.post(`${API_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      throw new Error('Invalid credentials');
    }
  },

  getStoredToken(): string | null {
    return localStorage.getItem('token');
  },

  setStoredToken(token: string): void {
    localStorage.setItem('token', token);
  },

  removeStoredToken(): void {
    localStorage.removeItem('token');
  },

  getStoredUser(): string | null {
    const userStr = localStorage.getItem('user');
    return userStr ? userStr : null;
  },

  setStoredUser(user: any): void {
    localStorage.setItem('user', JSON.stringify(user));
  },

  removeStoredUser(): void {
    localStorage.removeItem('user');
  }
};
