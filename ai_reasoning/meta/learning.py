"""
AI Reasoning Project — Meta-Learning & Calibration
Sourced from: SRD Phase 3
"""
from ai_reasoning.meta.horizon import EpistemicHorizon

class MetaLearningLoop:
    """
    Feedback loop for confidence calibration improvement.
    Adjusts domain scalars if the Expected Calibration Error (ECE) is out of bounds.
    """
    def __init__(self, horizon: EpistemicHorizon):
        self.horizon = horizon

    def process_calibration_feedback(self, domain: str, expected_calibration_error: float):
        """
        If the system was 90% confident but only 70% accurate in testing, 
        ECE is 0.20. The system must penalize its future confidence in this domain.
        """
        if expected_calibration_error > 0.05: # Strict 5% tolerance from EBD
            # Penalize the domain calibration score
            penalty = expected_calibration_error * 1.5
            current_score = self.horizon.domain_calibration.get(domain, 0.50)
            
            new_score = max(0.05, current_score - penalty)
            self.horizon.domain_calibration[domain] = new_score
            
            return {
                "action": "CALIBRATION_ADJUSTED",
                "domain": domain,
                "old_score": current_score,
                "new_score": new_score,
                "reason": f"ECE {expected_calibration_error} exceeded 0.05 threshold."
            }
            
        return {"action": "NO_CHANGE", "domain": domain}
