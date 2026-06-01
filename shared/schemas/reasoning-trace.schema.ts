/**
 * ReasoningTrace Schema
 * Sourced from: AIC §4.1
 */
export interface ReasoningTrace {
    trace_id: string;
    conclusion_id: string;
    session_id: string;
    steps: TraceStep[];
    final_confidence: number;
    chain_depth: number;
    reasoning_modes_used: string[];
    created_at: string;
}

export interface TraceStep {
    step_number: number;
    type: "PREMISE" | "RULE_APPLICATION" | "DERIVATION" | "ABDUCTIVE_HYPOTHESIS";
    node_id: string;
    statement: string;
    confidence_in: number;
    confidence_out: number;
    rule_id?: string;
    source_ids?: string[];
}
