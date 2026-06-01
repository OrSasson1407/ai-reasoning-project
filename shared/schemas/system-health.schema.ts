/**
 * SystemHealth Schema
 * Used for Gateway Heartbeat (/health)
 */
export interface SystemHealth {
    service_name: string;
    status: "ONLINE" | "DEGRADED" | "HALTED";
    active_contradictions: number;
    quarantined_nodes: number;
    last_ebd_run: string;
}
