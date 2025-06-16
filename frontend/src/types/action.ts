import { Operation } from './operation';
import { Descriptions } from './description';
import { File } from './file';

export interface ActionBase {
    id: number;
    project_id: string;
    datetime: string;
    operation?: Operation;
    file_column?: string;
    file?: File;
}

export interface Action extends ActionBase {
    active_description: number;
    active_labels: number;
    active_code: number;
    descriptions: Descriptions[];
}

export interface ActionCreate {
    project_id: string;
}

