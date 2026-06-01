/**
 * ContradictionReport Schema
 * Sourced from: AIC §4.3
 */
export interface ContradictionReport {
    contradiction_id: string;
    contradiction_type: "HARD" | "SOFT" | "CONFIDENCE_COLLAPSE" | "TEMPORAL" | "CAUSAL_LOOP" | "VCL_VIOLATION";
    severity: "HALT" | "FLAG" | "WARN";
    detected_at: string;
    node_a_id: string;
    node_b_id: string;
    belief_path_a: string[];
    belief_path_b: string[];
    quarantined_nodes: string[];
    resolution_status: "UNRESOLVED" | "IN_PROGRESS" | "RESOLVED" | "ESCALATED";
    audit_log_ref: string;
}
