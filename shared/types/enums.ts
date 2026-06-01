/**
 * Shared Type Enums - Single Source of Truth
 * Ensures L1 through L7 speak the same language.
 */

export enum ReasoningMode {
    DEDUCTIVE = "DEDUCTIVE",
    INDUCTIVE = "INDUCTIVE",
    ABDUCTIVE = "ABDUCTIVE"
}

export enum CertaintyLevel {
    HIGH = "HIGH",
    PROBABILISTIC = "PROBABILISTIC",
    HYPOTHESIS = "HYPOTHESIS"
}

export enum MetaSignal {
    HALT = "HALT",
    FLAG = "FLAG",
    WARN = "WARN",
    ESCALATION = "ESCALATION_REQUIRED"
}
