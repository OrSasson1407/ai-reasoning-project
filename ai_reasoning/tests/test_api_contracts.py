import pytest
from ai_reasoning.api.contracts import StandardErrorResponse, ContractViolations

def test_contract_violation_definitions():
    """Ensure CRITICAL contract violations are properly defined."""
    assert "NO_TRACE" in ContractViolations.CV_001
    assert "VCL_BYPASS" in ContractViolations.CV_008
