import pytest
from ai_reasoning.inference.rules import ReasoningRule, ReasoningMode

def test_ci06_confidence_caps():
    """Rule CI-06: Confidence caps for Inductive and Abductive reasoning."""
    premises_conf = [0.95, 0.90] # Strong premises
    
    deductive = ReasoningRule(ReasoningMode.DEDUCTIVE)
    inductive = ReasoningRule(ReasoningMode.INDUCTIVE)
    abductive = ReasoningRule(ReasoningMode.ABDUCTIVE)
    
    assert deductive.calculate_confidence(premises_conf) > 0.85
    assert inductive.calculate_confidence(premises_conf) <= 0.85 # Inductive Cap
    assert abductive.calculate_confidence(premises_conf) <= 0.50 # Abductive Cap
