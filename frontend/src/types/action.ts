import { Operation } from './operation';
import { Descriptions } from './description';

export interface ActionBase {
    id: number;
    project_id: string;
    datetime: string;
    operation?: Operation;
    file_column?: string;
}

export interface Action extends ActionBase {
    active_description: number;
    descriptions: Descriptions[];
}

export interface ActionCreate {
    project_id: string;
}

