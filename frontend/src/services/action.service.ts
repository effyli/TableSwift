import axiosInstance from './axios.config';
import { Action, ActionBase, ActionCreate
 } from '../types/action';
import { Labels } from '../types/labels';
import { Code } from '../types/code';
import { Descriptions } from '../types/description';
import { File } from '../types/file';

const DEFAULT_PAGE_SIZE = 20;

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
            const response = await axiosInstance.put<Action>(`/action/${action.id}`, action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to update action');
        }
    },

    async revertAction(actionId: number): Promise<File | null> {
        try {
            const response = await axiosInstance.post<File | null>(`/action/${actionId}/revert`);
            return response.data;
        } catch (error) {
            throw new Error('Failed to revert action');
        }
    },

    async generateLabels(action: Action): Promise<Descriptions> {
        try {
            const response = await axiosInstance.post<Descriptions>(`/action/generate_labels`, action);
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

    async saveCode(code: Code): Promise<any> {
        try {
            const response = await axiosInstance.post<any>(`/action/save_code`, code);
            return response.data;
        } catch (error) {
            throw new Error('Failed to save code');
        }
    },

    async executeCode(action: Action): Promise<[File, File]> {
        try {
            const response = await axiosInstance.post<[File, File]>(`/action/execute_code`, action);
            return response.data;
        } catch (error) {
            throw new Error('Failed to execute code');
        }
    },

    async loadAffectedRows(action_id: number, offset: number, limit: number = DEFAULT_PAGE_SIZE): Promise<File> {
        try {
            const response = await axiosInstance.get(`/action/${action_id}/affected_rows`, {
                params: { offset, limit }
            });
            return response.data;
        } catch (error) {
            throw new Error('Failed to load affected rows');
        }
    },

    async searchAffectedRows(action_id: number, query: string, offset: number = 0, limit: number = DEFAULT_PAGE_SIZE): Promise<File> {
        try {
            const response = await axiosInstance.get(`/action/${action_id}/search`, {
                params: { query, offset, limit }
            });
            return response.data;
        } catch (error) {
            throw new Error('Failed to search affected rows');
        }
    },
}
