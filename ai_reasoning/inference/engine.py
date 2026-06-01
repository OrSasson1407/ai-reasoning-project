import uuid
from datetime import datetime, timezone
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.relation import Relation
from ai_reasoning.core.enums import ReasoningMode, NodeType, RelationType
from ai_reasoning.core.exceptions import QuarantineBypassError
from .rules import ReasoningRuleProcessor

class InferenceEngine:
    def __init__(self, graph: KnowledgeGraph): self.graph = graph

    def derive_node(self, premise_ids: list[uuid.UUID], mode: ReasoningMode, conclusion_label: str, conclusion_type: NodeType) -> dict:
        premise_nodes = []
        for pid in premise_ids:
            node = self.graph.require_node(pid)
            if node.quarantine_flag: raise QuarantineBypassError(f"CV-006: Node {pid} is quarantined.")
            if node.is_stale: raise ValueError(f"Stale node {pid} cannot be used.")
            premise_nodes.append(node)
            
        rule_processor = ReasoningRuleProcessor(mode)
        derived_confidence = rule_processor.calculate_confidence([n.confidence for n in premise_nodes])
        
        if mode == ReasoningMode.DEDUCTIVE:
            for node in premise_nodes:
                if node.node_type == NodeType.HYPOTHESIS and node.confidence <= 0.50:
                    raise ValueError("CI-09: Low-confidence Hypothesis isolation.")
                    
        trace_id = uuid.uuid4()
        conclusion_node = KnowledgeNode(
            node_type=conclusion_type, label=conclusion_label,
            properties={"reasoning_trace_id": str(trace_id), "mode": mode.value},
            source_ids=[trace_id], confidence=derived_confidence
        )
        self.graph.add_node(conclusion_node)
        
        for pid in premise_ids:
            rel = Relation(
                relation_type=RelationType.DERIVED_FROM, source_node_id=conclusion_node.entity_id,
                target_node_id=pid, confidence=derived_confidence, source_ids=[str(trace_id)]
            )
            self.graph.add_relation(rel)
        return {"status": "SUCCESS", "node_id": conclusion_node.entity_id}
