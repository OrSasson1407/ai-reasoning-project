"""
AI Reasoning Project — Epistemic Horizon Mapping
Sourced from: EBD v1.0 · SRD Phase 3
"""

from typing import Dict
from ai_reasoning.core.enums import ReasoningMode

class EpistemicHorizon:
    """
    Maps the boundaries of what the system knows it does not know.
    If domain confidence drops below 0.50, it is flagged as 'Outside Horizon'.
    """

    def __init__(self):
        # Baseline calibration from EBD Evaluation
        self.domain_calibration: Dict[str, float] = {
            "Physics": 0.94,
            "Current Events": 0.61,
            "Economic Forecasting": 0.48
        }

    def check_horizon(self, domain: str) -> dict:
        """Returns the horizon status and recommended scalar for a domain."""
        score = self.domain_calibration.get(domain, 0.50) # Default unknown to boundary edge
        
        status = "INSIDE"
        if score < 0.50:
            status = "OUTSIDE"
        elif score < 0.70:
            status = "BOUNDARY"
            
        return {
            "domain": domain,
            "calibration_score": score,
            "horizon_status": status,
            "requires_meta_trigger": status == "OUTSIDE"
        }

    def update_calibration(self, domain: str, expected_calibration_error: float):
        """Adjusts the horizon based on EBD periodic testing."""
        current = self.domain_calibration.get(domain, 0.50)
        # Shift calibration down if error is high
        self.domain_calibration[domain] = max(0.05, current - expected_calibration_error)
