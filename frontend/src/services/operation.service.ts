import axiosInstance from './axios.config';
import { Operation } from '../types/operation';

export const operationService = {
    async getOperations(): Promise<Operation[]> {
        try {
            const response = await axiosInstance.get<Operation[]>('/operation');
            return response.data;
        } catch (error) {
            throw new Error('Failed to fetch operations');
        }
    }
};
