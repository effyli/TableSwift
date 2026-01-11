export interface File {
    file_path: string;
    data?: Record<string, any>[];
    total_rows?: number;
    loaded_rows?: number;
}
