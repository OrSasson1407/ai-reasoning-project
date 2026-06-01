/**
 * L4 -> L5 CandidateConclusion Message Contract
 * Sourced from: AIC §3.2
 */
import { ReasoningMode, CertaintyLevel, MetaSignal } from '../types/enums';

export interface CandidateConclusion {
    candidate_id: string;
    statement: string;
    reasoning_mode: ReasoningMode;
    certainty_level: CertaintyLevel;
    confidence: number;
    premise_ids: string[];
    rule_ids_applied: string[];
    reasoning_trace: any[];
    inductive_flag: boolean;
    abductive_flag: boolean;
    meta_signals: MetaSignal[];
}
