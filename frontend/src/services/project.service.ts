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
            const formData = new FormData();
            formData.append('file', file);
            console.log('Uploading file:', file);
    
            const response = await axiosInstance.post<Project>('/project', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            throw new Error('Failed to upload file');
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