"""
AI Reasoning Project — Hybrid Probabilistic Model
Sourced from: SRD Phase 4
Implements Bayesian + Dempster-Shafer evidence combination.
"""
from typing import List
from ai_reasoning.core.node import CONFIDENCE_FLOOR

class HybridInferenceEngine:
    """
    Handles complex probability matrices when multiple independent sources 
    provide conflicting or supporting evidence.
    """
    
    def combine_evidence_dempster_shafer(self, masses: List[float]) -> float:
        """
        Combines independent probability masses (confidences) using Dempster's Rule of Combination.
        Used when multiple inductive paths support the same conclusion.
        """
        if not masses:
            return CONFIDENCE_FLOOR
            
        if len(masses) == 1:
            return masses[0]

        # Simplified Dempster's rule for combining two independent belief masses
        # m12 = (m1 * m2) / (1 - conflict)
        # For pure supporting evidence, conflict is 0.
        combined_mass = masses[0]
        for i in range(1, len(masses)):
            m1 = combined_mass
            m2 = masses[i]
            # Orthogonal sum assuming independent supporting sources
            combined_mass = m1 + m2 - (m1 * m2)
            
        return min(combined_mass, 0.99) # Never 1.0 absolute certainty

    def calculate_fuzzy_truth(self, premise_truths: List[float], logic_gate: str) -> float:
        """
        Applies fuzzy logic for complex node evaluations.
        AND -> min(), OR -> max()
        """
        if logic_gate == "AND":
            return min(premise_truths)
        elif logic_gate == "OR":
            return max(premise_truths)
        return CONFIDENCE_FLOOR
