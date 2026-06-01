import pytest
from ai_reasoning.inference.hybrid import HybridInferenceEngine

def test_dempster_shafer_combination():
    """Testing the Phase 4 probability combination logic."""
    engine = HybridInferenceEngine()
    
    # Two independent weak sources (0.6 and 0.6)
    # Should combine to be stronger than either alone (0.6 + 0.6 - 0.36 = 0.84)
    combined = engine.combine_evidence_dempster_shafer([0.6, 0.6])
    assert 0.83 < combined < 0.85

    # Three weak sources (0.5, 0.5, 0.5)
    combined_three = engine.combine_evidence_dempster_shafer([0.5, 0.5, 0.5])
    assert 0.87 < combined_three < 0.88
