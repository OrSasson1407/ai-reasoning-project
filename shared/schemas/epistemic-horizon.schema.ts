/**
 * EpistemicHorizon Schema
 * Sourced from: EBD v1.0
 */
export interface EpistemicHorizonReport {
    domain: string;
    current_confidence: number;
    horizon_status: "INSIDE" | "BOUNDARY" | "OUTSIDE";
    last_calibration_error: number;
    trigger_meta_learning: boolean;
}
