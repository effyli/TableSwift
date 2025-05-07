import { File } from './file';
import { ActionBase, Action } from './action';

export interface ProjectSidebar {
    id: string;
    name: string;
}

export interface Project {
    id: string;
    name: string;
    file: File;
    actions: ActionBase[];
    active_action: Action | null;
    user_id: string;
    created_at: string;
}