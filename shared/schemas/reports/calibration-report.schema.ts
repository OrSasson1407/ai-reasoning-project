/**
 * CalibrationReport Schema
 * Sourced from: EBD v1.0
 * Measures how well confidence scores correlate with actual accuracy.
 */
export interface CalibrationReport {
    report_id: string;
    target_domain: string;
    test_window: { start: string; end: string };
    metrics: {
        ece: number; // Expected Calibration Error
        over_confidence_rate: number;
        under_confidence_rate: number;
        total_inferences: number;
    };
    actionable_recommendations: string[];
}
