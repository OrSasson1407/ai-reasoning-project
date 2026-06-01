/**
 * AI Reasoning Project — Frontend Type Definitions
 * Strictly mirrors the Python Backend schemas to ensure End-to-End type safety.
 */

export enum NodeType {
    FACT = "FACT",
    HYPOTHESIS = "HYPOTHESIS",
    RULE = "RULE",
    ASSUMPTION = "ASSUMPTION",
    CLAIM = "CLAIM",
    PERSON = "PERSON"
}

export enum RelationType {
    DERIVED_FROM = "DERIVED_FROM",
    CONTRADICTS = "CONTRADICTS",
    CAUSES = "CAUSES",
    CORRELATES_WITH = "CORRELATES_WITH",
    SUPPORTS = "SUPPORTS"
}

export enum ReasoningMode {
    DEDUCTIVE = "DEDUCTIVE",
    INDUCTIVE = "INDUCTIVE",
    ABDUCTIVE = "ABDUCTIVE"
}

export interface KnowledgeNode {
    entity_id: string;
    node_type: NodeType;
    label: string;
    confidence: number;
    quarantine_flag: boolean;
    valid_from: string;
    valid_until?: string;
    source_ids: string[];
    meta_tags: string[];
}

export interface Relation {
    relation_id: string;
    source_node_id: string;
    target_node_id: string;
    relation_type: RelationType;
    confidence: number;
}

export interface InferenceResult {
    reasoning_trace_id: string;
    conclusion_node_id: string;
    confidence: number;
    mode: ReasoningMode;
}

export interface ApiError {
    request_id: string;
    status: string;
    error: {
        code: string;
        message: string;
        retryable: boolean;
    }
}
