/**
 * Standard API Request Wrapper
 * Enforces AIC traceability guarantees at the gateway edge.
 */
export interface ApiRequestWrapper<T> {
    request_id: string;
    timestamp: string;
    payload: T;
    metadata: {
        source_id: string;
        priority: "CRITICAL" | "STANDARD" | "LOW";
        skip_vcl_check: boolean; // Only allowed for internal trusted system calls
    };
}
