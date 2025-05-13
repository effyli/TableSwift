import { Code } from './code';

export interface Labels {
    id: number;
    description: string;
    json: any | null;
    version: number;
    codes: Code[];
}
