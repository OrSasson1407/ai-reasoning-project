/**
 * Layer 7 Meta-Cognition Summary Report
 * Aggregated summary for the EBD evaluation cycle.
 */
export interface MetaCognitionSummary {
    report_id: string;
    period: { start: string; end: string };
    domains: {
        domain_name: string;
        confidence_score: number;
        accuracy_vs_truth: number;
        horizon_status: "INSIDE" | "BOUNDARY" | "OUTSIDE";
    }[];
    calibration: {
        expected_calibration_error: number;
        over_confidence_rate: number;
    };
}
