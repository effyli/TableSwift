import { Operation } from './operation';

export interface ActionBase {
    id: number;
    project_id: string;
    datetime: string;
    operation?: Operation;
    file_column?: string;
}

export interface Action extends ActionBase {
    description?: string;
    labels?: JSON[];
    code?: string;
}

export interface ActionCreate {
    project_id: string;
}

export interface ActionUpdate {
    id: number;
    operation_id: number;
    file_column: string;
    description: string;
}
