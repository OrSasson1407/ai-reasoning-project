/**
 * VCLCompliance Schema
 * Sourced from: AIC §4.4 (Values Constraint Layer)
 */
export interface VCLComplianceReport {
    request_id: string;
    is_compliant: boolean;
    violated_constraints: string[];
    risk_score: number;
    remediation_required: boolean;
}
