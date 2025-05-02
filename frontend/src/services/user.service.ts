import { User } from '../types/user';
import axiosInstance from './axios.config';

export const userService = {
    async getCurrentUser(): Promise<User | null> {
        try {
            const response = await axiosInstance.get('/users/me');
            if (response.status === 200) {
                return response.data;
            }
            return null;
        }
        catch (error) {
            throw error;
        }
    },

    async getAllUsers(): Promise<User[]> {
        try {
            const response = await axiosInstance.get('/users');
            return response.data;
        } catch (error) {
            throw error;
        }
    },
}