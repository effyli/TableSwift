import axios from 'axios';
import { LoginCredentials, LoginResponse } from '../types/auth';

const API_URL = 'http://localhost:8000/api'; // Replace with your actual API URL

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      // In a real application, this would be a real API endpoint
      const response = await axios.post(`${API_URL}/auth/login`, credentials);
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
