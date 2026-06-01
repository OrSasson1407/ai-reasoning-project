/**
 * Meta-Cognition Types
 * Defines the signal-adjustment feedback loop (Layer 6 -> Layer 7).
 */
export interface MetaAdjustment {
    adjustment_id: string;
    target_layer: "L1" | "L2" | "L3" | "L4" | "L5" | "L6";
    adjustment_type: "CONFIDENCE_SCALAR" | "DOMAIN_FLAG" | "RULE_SENSITIVITY" | "RELOAD_ACB";
    parameters: Record<string, any>;
    rationale: string;
}

export interface EpistemicHorizonBoundary {
    domain: string;
    confidence_score: number;
    is_at_risk: boolean;
}
