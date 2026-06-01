"""
AI Reasoning Project — Reasoning Rules Specification (RRS)
Sourced from: RRS v1.0 §6, §7
"""

from ai_reasoning.core.enums import ReasoningMode
from ai_reasoning.core.node import CONFIDENCE_FLOOR

class ConfidenceCapError(Exception):
    """Raised when confidence inflation is attempted (CI-06)."""

class ReasoningRuleProcessor:
    """
    Applies logic constraints and calculates resulting confidence scores 
    based on the RRS rules (UP-10, CI-06).
    """

    def __init__(self, mode: ReasoningMode):
        self.mode = mode

    def calculate_confidence(self, premises_confidence: list[float]) -> float:
        """
        Rule CI-06: Confidence Consistency.
        A conclusion's confidence may never exceed the minimum confidence of its premises 
        multiplied by a chain strength factor.
        """
        if not premises_confidence:
            return CONFIDENCE_FLOOR
            
        min_conf = min(premises_confidence)
        
        if self.mode == ReasoningMode.DEDUCTIVE:
            raw_calc = min_conf * 0.95  # Standard chain degradation
            return max(CONFIDENCE_FLOOR, raw_calc)
            
        elif self.mode == ReasoningMode.INDUCTIVE:
            # CI-06: Cap Inductive certainty
            raw_calc = min_conf * 0.85
            return min(max(CONFIDENCE_FLOOR, raw_calc), 0.85) 
            
        elif self.mode == ReasoningMode.ABDUCTIVE:
            # CI-06: Cap Abductive certainty (Hypothesis)
            raw_calc = min_conf * 0.50
            return min(max(CONFIDENCE_FLOOR, raw_calc), 0.50)

        return CONFIDENCE_FLOOR
