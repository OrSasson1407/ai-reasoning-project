/**
 * AIC Section 5.1: Standard Error Response
 */
export interface StandardErrorResponse {
    request_id: string;
    timestamp: string;
    status: "error";
    error: {
        code: string; // e.g., "CV-001"
        message: string;
        detail?: Record<string, any>;
        trace_id?: string;
        retryable: boolean;
    };
}
