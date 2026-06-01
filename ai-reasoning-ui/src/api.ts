import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface NodeResponse {
    entity_id: string;
    node_type: 'FACT' | 'HYPOTHESIS' | 'RULE' | 'CLAIM';
    label: string;
    confidence: number;
    quarantine_flag: boolean;
    is_stale: boolean;
}

export const api = {
    addNode: async (node_type: string, label: string, confidence: number): Promise<NodeResponse> => {
        const response = await axios.post(`${API_URL}/graph/nodes`, {
            node_type,
            label,
            confidence,
            properties: {},
            content: label
        });
        return response.data;
    },
    deriveKnowledge: async (
        premise_ids: string[], 
        mode: string, 
        conclusion_label: string, 
        conclusion_type: string
    ) => {
        const response = await axios.post(`${API_URL}/inference/derive`, {
            premise_ids,
            mode,
            conclusion_label,
            conclusion_type
        });
        return response.data;
    },
    checkHealth: async () => {
        const response = await axios.get(`${API_URL}/health`);
        return response.data;
    }
};
