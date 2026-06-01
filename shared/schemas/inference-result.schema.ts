/**
 * InferenceResult Schema
 * Sourced from: AIC §4.2
 */
import { ReasoningMode } from '../types/enums';

export interface InferenceResult {
    result_id: string;
    conclusion_node_id: string;
    reasoning_trace_id: string; // Critical for CV-001 avoidance
    mode: ReasoningMode;
    confidence: number;
    metadata: {
        chain_depth: number;
        execution_time_ms: number;
        vcl_passed: boolean;
    };
}
