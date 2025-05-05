import axiosInstance from "./axios.config";

export interface Project {
    id: string;
    name: string;
    file_path: string;
    user_id: string;
    created_at: string;
}

export const projectService = {
    async uploadFile(file: File): Promise<Project> {
        try {
            // Validate file size client-side first
            const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
            if (file.size > MAX_FILE_SIZE) {
                throw new Error('File size too large. Maximum size is 10MB');
            }

            // Validate file type
            if (!file.name.toLowerCase().endsWith('.csv')) {
                throw new Error('Only CSV files are allowed');
            }

            const formData = new FormData();
            formData.append('file', file);
    
            const response = await axiosInstance.post<Project>('/project/', formData, {
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
    
    async getProjects(): Promise<Project[]> {
        try {
            const response = await axiosInstance.get<Project[]>('/project');
            return response.data;
        } catch (error) {
            throw new Error('Failed to fetch projects');
        }
    },
    
    async getFile(fileId: string): Promise<Blob> {
        try {
            const response = await axiosInstance.get(`/files/${fileId}`, {
                responseType: 'blob',
            });
            return response.data;
        } catch (error) {
            throw new Error('Failed to fetch file');
        }
    },
}