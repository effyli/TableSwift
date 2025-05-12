import { Operation } from './operation';
import { Labels } from './labels';

export interface ActionBase {
    id: number;
    project_id: string;
    datetime: string;
    operation?: Operation;
    file_column?: string;
}

export interface Action extends ActionBase {
    description?: string;
    labels?: Labels[];
}

export interface ActionCreate {
    project_id: string;
}

