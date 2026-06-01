import pytest
from ai_reasoning.telemetry.metrics import SystemMetrics

def test_metric_registration():
    """Ensures that the Prometheus metrics registry correctly initializes."""
    # Simulate a contract violation being caught by the API gateway
    SystemMetrics.record_violation("CV-001_NO_TRACE")
    
    # Fetch the value from the Prometheus internal registry
    count = SystemMetrics.CONTRACT_VIOLATIONS.labels(violation_code="CV-001_NO_TRACE")._value.get()
    assert count >= 1
