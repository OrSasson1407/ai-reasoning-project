/**
 * L1 -> L2 ParsedInput Message
 * Sourced from: AIC §3.1
 */
export interface ParsedInput {
    parse_id: string;
    raw_input: string;
    entities: {
        mention: string;
        entity_type: string;
        confidence: number;
    }[];
    claims: {
        statement: string;
        confidence: number;
        temporal_marker: string | null;
    }[];
    intent: "QUERY" | "INGEST" | "RESOLVE" | "CLARIFY";
    timestamp: string;
}
