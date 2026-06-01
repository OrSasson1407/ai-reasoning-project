import pytest
from ai_reasoning.meta.horizon import EpistemicHorizon
from ai_reasoning.meta.learning import MetaLearningLoop

def test_epistemic_horizon_boundary():
    horizon = EpistemicHorizon()
    # EBD defines Economic Forecasting as 0.48 (Outside Horizon)
    status = horizon.check_horizon("Economic Forecasting")
    assert status["horizon_status"] == "OUTSIDE"

def test_ece_calibration_penalty():
    horizon = EpistemicHorizon()
    horizon.domain_calibration["Physics"] = 0.90
    
    loop = MetaLearningLoop(horizon)
    # System expected 90% accuracy but ECE showed 20% error
    loop.process_calibration_feedback("Physics", 0.20)
    
    # The domain score should be penalized heavily
    assert horizon.domain_calibration["Physics"] < 0.90
