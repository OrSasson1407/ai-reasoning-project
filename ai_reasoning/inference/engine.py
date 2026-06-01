"""
AI Reasoning Project — Inference Engine
Sourced from: RRS v1.0 §1, §6
"""

import uuid
from datetime import datetime, timezone
from ai_reasoning.core.graph import KnowledgeGraph, QuarantineBypassError
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.relation import Relation
from ai_reasoning.core.enums import ReasoningMode, NodeType, RelationType
from .rules import ReasoningRuleProcessor

class InferenceEngine:
    """
    Layer 4 Engine. Derives new knowledge from the KnowledgeGraph.
    Enforces CI-02 (No Quarantine Bypass) and generates reasoning traces (CV-001 prevention).
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def derive_node(self, 
                    premise_ids: list[uuid.UUID], 
                    mode: ReasoningMode, 
                    conclusion_label: str, 
                    conclusion_type: NodeType) -> dict:
        """
        Processes an inference step, enforcing CI-02 and returning a traceable result.
        """
        # 1. Fetch Premises and check CI-02 Quarantine Bypass
        premise_nodes = []
        for pid in premise_ids:
            node = self.graph.require_node(pid)
            if node.quarantine_flag:
                raise QuarantineBypassError(
                    f"CV-006: QUARANTINE_BYPASS - Node {pid} is quarantined and cannot be a premise."
                )
            if node.is_stale:
                raise ValueError(f"Stale node {pid} cannot be used as a premise.")
            premise_nodes.append(node)

        # 2. Calculate Confidence (CI-06)
        rule_processor = ReasoningRuleProcessor(mode)
        derived_confidence = rule_processor.calculate_confidence([n.confidence for n in premise_nodes])

        # CI-09: Hypothesis Isolation
        if mode == ReasoningMode.DEDUCTIVE:
            for node in premise_nodes:
                if node.node_type == NodeType.HYPOTHESIS and node.confidence <= 0.50:
                    raise ValueError("CI-09: Low-confidence Hypothesis cannot be sole premise for Deduction.")

        # 3. Create Conclusion Node
        trace_id = uuid.uuid4()
        conclusion_node = KnowledgeNode(
            node_type=conclusion_type,
            label=conclusion_label,
            properties={"reasoning_trace_id": str(trace_id), "mode": mode.value},
            valid_from=datetime.now(timezone.utc),
            source_ids=[trace_id],  # The inference execution is the source
            decay_rate=0.01,
            confidence=derived_confidence
        )
        
        self.graph.add_node(conclusion_node)

        # 4. Link Premises via DERIVED_FROM relations
        for pid in premise_ids:
            rel = Relation(
                relation_type=RelationType.DERIVED_FROM,
                source_node_id=conclusion_node.entity_id,
                target_node_id=pid,
                confidence=derived_confidence,
                valid_from=datetime.now(timezone.utc),
                source_ids=[trace_id]
            )
            self.graph.add_relation(rel)

        return {
            "reasoning_trace_id": str(trace_id),
            "conclusion_node_id": str(conclusion_node.entity_id),
            "confidence": derived_confidence,
            "mode": mode.value
        }
