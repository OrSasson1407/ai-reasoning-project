"""
AI Reasoning Project — Deductive Inference Engine
Sourced from: RRS v1.0
Applies strict logical deduction (General -> Specific). 
Yields HIGH confidence, provided premises are verified.
"""
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.enums import ReasoningMode, NodeType
from ai_reasoning.core.exceptions import HypothesisIsolationError
from ai_reasoning.inference.engine import InferenceEngine

class DeductiveEngine(InferenceEngine):
    def apply_modus_ponens(self, rule_node_id: str, fact_node_id: str, conclusion_label: str) -> dict:
        """
        If P -> Q (rule), and P (fact), then Q (conclusion).
        """
        rule_node = self.graph.require_node(rule_node_id)
        fact_node = self.graph.require_node(fact_node_id)

        # Enforce CI-09: Hypothesis Isolation
        if fact_node.node_type == NodeType.HYPOTHESIS and fact_node.confidence <= 0.50:
            raise HypothesisIsolationError(
                f"CI-09: Hypothesis {fact_node_id} cannot bootstrap deductive certainty."
            )

        # Execute standard derivation sequence (handles tracing, CI-02 checks, and audit)
        return self.derive_node(
            premise_ids=[rule_node_id, fact_node_id],
            mode=ReasoningMode.DEDUCTIVE,
            conclusion_label=conclusion_label,
            conclusion_type=NodeType.CLAIM
        )
