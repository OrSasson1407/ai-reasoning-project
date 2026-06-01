"""
AI Reasoning Project — Abductive Inference Engine
Sourced from: RRS v1.0
Generates the most probable explanation for an observation.
Strictly capped at 0.50 Confidence (Rule CI-06) and forced to type HYPOTHESIS.
"""
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.enums import ReasoningMode, NodeType
from ai_reasoning.inference.engine import InferenceEngine

class AbductiveEngine(InferenceEngine):
    def propose_hypothesis(self, observation_node_id: str, hypothesis_label: str) -> dict:
        """
        Creates a HYPOTHESIS node explaining an orphan or unusual fact.
        Always outputs low-confidence nodes that trigger Socratic Clarification probes.
        """
        # The base engine enforces the 0.50 cap for ABDUCTIVE mode.
        return self.derive_node(
            premise_ids=[observation_node_id],
            mode=ReasoningMode.ABDUCTIVE,
            conclusion_label=hypothesis_label,
            conclusion_type=NodeType.HYPOTHESIS
        )
