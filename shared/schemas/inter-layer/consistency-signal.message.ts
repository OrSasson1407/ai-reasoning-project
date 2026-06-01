/**
 * L6 -> L7 ConsistencySignal Message
 * Sourced from: AIC §3.4
 */
import { MetaSignal } from '../../types/enums';

export interface ConsistencySignal {
    signal_id: string;
    signal_type: MetaSignal;
    source_session_id: string;
    affected_nodes: string[];
    detail: string;
    timestamp: string;
}
