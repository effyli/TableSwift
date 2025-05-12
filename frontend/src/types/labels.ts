import { Code } from './code';

export interface Labels {
    id: number;
    json: any;
    version: number;
    codes: Code[];
}
