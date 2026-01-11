import axiosInstance from "./axios.config";
import { Project, ProjectSidebar } from "../types/project";

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024; // 10MB in bytes
const DEFAULT_PAGE_SIZE = 20;

export const projectService = {
    async uploadFile(file: File): Promise<ProjectSidebar> {
        try {
            // Validate file size client-side first
            if (file.size > MAX_FILE_SIZE_BYTES) {
                throw new Error(`File size too large. Maximum size is ${MAX_FILE_SIZE_MB}MB`);
            }

            // Validate file type
            if (!file.name.toLowerCase().endsWith('.csv')) {
                throw new Error('Only CSV files are allowed');
            }

            const formData = new FormData();
            formData.append('file', file);
    
            const response = await axiosInstance.post<ProjectSidebar>('/project/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error: any) {
            // Handle both axios error responses and other errors
            if (error.response?.data?.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error(error.message || 'Failed to upload file');
        }
    },
    
    async getProjects(): Promise<ProjectSidebar[]> {
        try {
            const response = await axiosInstance.get<ProjectSidebar[]>('/project');
            return response.data;
        } catch (error) {
            throw new Error('Failed to fetch projects');
        }
    },

    async deleteProject(projectId: string): Promise<void> {
        try {
            await axiosInstance.delete(`/project/${projectId}`);
        } catch (error) {
            throw new Error('Failed to delete project');
        }
    },

    async getProjectDetails(projectId: string, actionId: string | undefined): Promise<Project> {
        try {
            const response = await axiosInstance.get<Project>(`/project/${projectId}?actionId=${actionId}`);
            return response.data;
        } catch (error) {
            throw new Error('Failed to fetch project details');
        }
    },

    async loadMoreRows(projectId: string, offset: number, limit: number = DEFAULT_PAGE_SIZE): Promise<{
        data: Record<string, any>[];
        total_rows: number;
        loaded_rows: number;
    }> {
        try {
            const response = await axiosInstance.get(`/project/${projectId}/data`, {
                params: { offset, limit }
            });
            return response.data;
        } catch (error) {
            throw new Error('Failed to load more rows');
        }
    },

    async searchProjectData(
        projectId: string,
        query: string,
        offset: number = 0,
        limit: number = DEFAULT_PAGE_SIZE
    ): Promise<{
        data: Record<string, any>[];
        total_rows: number;
        loaded_rows: number;
    }> {
        try {
            const response = await axiosInstance.get(`/project/${projectId}/search`, {
                params: { query, offset, limit }
            });
            return response.data;
        } catch (error) {
            throw new Error('Failed to search project data');
        }
    },
}