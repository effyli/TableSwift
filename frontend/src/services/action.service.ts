import axiosInstance from './axios.config';
import { Action, ActionBase, ActionCreate, ActionUpdate } from '../types/action';

export const actionService = {
    async createAction(action: ActionCreate): Promise<ActionBase> {
        try {
            const response = await axiosInstance.post<ActionBase>('/action', action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to create action');
        }
    },

    async getAction(actionId: number): Promise<Action> {
        try {
            const response = await axiosInstance.get<Action>(`/action/${actionId}`);
            return response.data;
        } catch (error) {
            throw new Error('Failed to fetch action');
        }
    },

    async updateAction(actionId: number, action: ActionUpdate): Promise<Action> {
        try {
            const response = await axiosInstance.put<Action>(`/action/${actionId}`, action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to update action');
        }
    },

    async deleteAction(actionId: number): Promise<void> {
        try {
            await axiosInstance.delete(`/action/${actionId}`);
        } catch (error) {
            throw new Error('Failed to delete action');
        }
    },
};
