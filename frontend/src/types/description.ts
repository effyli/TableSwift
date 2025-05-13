import { Labels } from './labels';

export interface Descriptions {
    id?: number;
    description: string;
    version?: number;
    labels?: Labels[];
}
