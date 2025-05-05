export interface Project {
    id: string;
    name: string;
}

export interface ProjectItem extends Project {
    file_path: string;
    created_at: string;
}