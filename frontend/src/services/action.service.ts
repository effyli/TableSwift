import axiosInstance from './axios.config';
import { Action, ActionBase, ActionCreate
 } from '../types/action';
import { Labels } from '../types/labels';
import { Code } from '../types/code';

export const actionService = {
    async createAction(action: ActionCreate): Promise<ActionBase> {
        try {
            const response = await axiosInstance.post<ActionBase>('/action', action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to create action');
        }
    },

    async deleteAction(actionId: number): Promise<void> {
        try {
            await axiosInstance.delete(`/action/${actionId}`);
        } catch (error) {
            throw new Error('Failed to delete action');
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

    async updateAction(action: Action): Promise<Action> {
        try {
            console.log('Updating action:', action);
            const response = await axiosInstance.put<Action>(`/action/${action.id}`, action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to update action');
        }
    },

    async generateLabels(action: Action): Promise<Labels> {
        try {
            const response = await axiosInstance.post<Labels>(`/action/generate_labels`, action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to generate labels');
        }
    },

    async saveLabels(labels: Labels): Promise<any> {
        try {
            const response = await axiosInstance.post<any>(`/action/save_labels`, labels);
            return response.data;
        } catch (error) {
            throw new Error('Failed to save labels');
        }
    },

    async generateCode(action: Action): Promise<Code> {
        try {
            const response = await axiosInstance.post<Code>(`/action/generate_code`, action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to generate code');
        }
    },
};
