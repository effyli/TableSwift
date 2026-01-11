import { File } from './file';
import { ActionBase, Action } from './action';

export interface ProjectSidebar {
    id: string;
    name: string;
}

export interface Project extends ProjectSidebar {
    file: File;
    actions: ActionBase[];
    active_action: Action | null;
    created_at: string;
}