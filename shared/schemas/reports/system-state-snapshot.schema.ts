/**
 * SystemStateSnapshot Schema
 * Captures a point-in-time state of the Knowledge Graph for recovery.
 */
export interface SystemStateSnapshot {
    snapshot_id: string;
    timestamp: string;
    stats: {
        node_count: number;
        relation_count: number;
        active_contradictions: number;
        quarantine_depth: number;
    };
    checksum: string; // Integrity verification
}
