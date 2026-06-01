"""
AI Reasoning Project — Prometheus Telemetry
Tracks real-time system health, contraction states, and rule violations.
"""
from prometheus_client import Counter, Gauge, Histogram

class SystemMetrics:
    # CCP (Contradiction & Consistency Protocol) Metrics
    ACTIVE_CONTRADICTIONS = Gauge('active_contradictions_total', 'Current number of unresolved Level 1 HALT contradictions')
    QUARANTINED_NODES = Gauge('quarantined_nodes_total', 'Number of nodes currently under quarantine (CI-05)')
    
    # AIC (API Interface Contract) Metrics
    CONTRACT_VIOLATIONS = Counter('contract_violations_total', 'Count of AIC violations intercepted', ['violation_code'])
    
    # Inference & Meta-Cognition Metrics
    INFERENCE_OPERATIONS = Counter('inference_operations_total', 'Total derivations processed', ['mode'])
    CONFIDENCE_CALIBRATION_ERROR = Gauge('expected_calibration_error', 'Current ECE from EBD benchmarking phase')

    @classmethod
    def record_violation(cls, code: str):
        """Records a CV-XXX violation to trigger Grafana alerts."""
        cls.CONTRACT_VIOLATIONS.labels(violation_code=code).inc()
