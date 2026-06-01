/**
 * DI-09 Audit Log Snapshot
 * Used to verify system state mutations over a time window.
 */
export interface AuditLogSnapshot {
    snapshot_id: string;
    start_time: string;
    end_time: string;
    entries: {
        audit_id: string;
        mutation_type: string;
        entity_id: string;
        signature: string; // Cryptographic hash
    }[];
}
