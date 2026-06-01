/**
 * L5 -> L6 ValidationRequest Message Contract
 * Sourced from: AIC §3.3
 */
import { CandidateConclusion } from '../../messaging/layer-contracts';

export interface ValidationRequest {
    validation_id: string;
    candidates: CandidateConclusion[];
    session_id: string;
}

export interface ValidationResult {
    validation_id: string;
    approved: string[];
    flagged: any[];
    halted: any[];
    vcl_blocks: any[];
}
