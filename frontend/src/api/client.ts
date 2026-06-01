/**
 * AI Reasoning Project — Frontend API Client
 * Routes all traffic through the API Gateway (Port 8080) to enforce AIC Contracts.
 */
import { KnowledgeNode, InferenceResult, ReasoningMode, NodeType } from '../types';

const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8080';
const API_KEY = import.meta.env.VITE_API_KEY || 'strict-architecture-key';

const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
};

export const ApiClient = {
    async getHealth() {
        const res = await fetch(`${GATEWAY_URL}/health`, { headers });
        if (!res.ok) throw new Error('Gateway unreachable');
        return res.json();
    },

    async ingestText(rawText: string, sourceId: string): Promise<string[]> {
        // Triggers the Layer 1 -> Layer 2 ingestion pipeline
        const res = await fetch(`${GATEWAY_URL}/graph/nodes`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ raw_text: rawText, source_ids: [sourceId] })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error?.message || 'Ingestion failed');
        }
        return res.json(); // Returns array of new entity_ids
    },

    async runInference(premiseIds: string[], mode: ReasoningMode, label: string, type: NodeType): Promise<InferenceResult> {
        const res = await fetch(`${GATEWAY_URL}/inference/derive`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
                premise_ids: premiseIds,
                mode,
                conclusion_label: label,
                conclusion_type: type
            })
        });
        if (!res.ok) {
            const err = await res.json();
            // This will catch CV-006, CI-08, etc. mapped by the backend
            throw new Error(`[${err.error?.code}] ${err.error?.message}`);
        }
        return res.json();
    },

    async getSystemMetrics() {
        const res = await fetch(`${GATEWAY_URL}/meta/ebd/report`, { headers });
        if (!res.ok) throw new Error('Failed to fetch EBD metrics');
        return res.json();
    }
};
