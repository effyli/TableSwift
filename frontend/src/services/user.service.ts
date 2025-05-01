import axios from 'axios';
import { User } from '../types/user';

const API_URL = 'http://localhost:80';

axios.defaults.withCredentials = true;

export const userService = {
    async getCurrentUser(): Promise<User | null> {
        try {
            const response = await axios.get(`${API_URL}/users/me`);
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
            const response = await axios.get(`${API_URL}/users`);
            return response.data;
        } catch (error) {
            throw error;
        }
    },
}