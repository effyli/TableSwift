import { File } from './file';

export interface Project {
    id: string;
    name: string;
    file: File;
    user_id: string;
    created_at: string;
}