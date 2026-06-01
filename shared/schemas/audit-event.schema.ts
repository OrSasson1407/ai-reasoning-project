/**
 * AuditEvent Schema
 * Sourced from: DAD DI-09 (Immutable State Mutation)
 */
export interface AuditEvent {
    audit_id: string;
    timestamp: string;
    actor: "SYSTEM" | "HUMAN_OPERATOR" | "INGESTION_PIPELINE";
    action_type: "CREATE" | "UPDATE" | "QUARANTINE" | "RESOLVE";
    entity_id: string;
    context: Record<string, any>;
    hash: string; // Cryptographic hash for immutability verification
}
