/**
 * VCLAuditReport Schema
 * Sourced from: AIC §4.4
 * Summarizes VCL violations over an operational window.
 */
export interface VCLAuditReport {
    audit_id: string;
    window: { start: string; end: string };
    violations: {
        violation_id: string;
        timestamp: string;
        conclusion_id: string;
        violated_constraint: string; // e.g., "harm_generation"
        system_response: "HALT" | "FLAG" | "LOG_ONLY";
    }[];
    total_blocked_conclusions: number;
}
