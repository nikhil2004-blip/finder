import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export interface FileUploadResponse {
    message: string;
    file_path: string;
    processed_json?: string;
    blocks_count?: number;
}

export interface SearchResult {
    text: string;
    file_name: string;
    page_number: number;
    score: number;
    source: string;
    metadata?: any;
}

export const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post<FileUploadResponse>(`${API_URL}/files/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const searchFiles = async (query: string) => {
    const response = await axios.post<SearchResult[]>(`${API_URL}/search`, { query, max_results: 20 });
    return response.data;
};

export const listFiles = async () => {
    const response = await axios.get(`${API_URL}/files/list`);
    return response.data;
};

export const deleteFile = async (filename: string) => {
    const response = await axios.delete(`${API_URL}/files/${filename}`);
    return response.data;
};
