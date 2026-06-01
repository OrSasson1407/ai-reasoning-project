"""
AI Reasoning Project — Graph Traversal & Tracing
Sourced from: SRD Phase 3 & AIC Traceability Guarantees
"""
from typing import List, Dict
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.enums import RelationType

class TraceabilityEngine:
    """
    Guarantees CV-001 (NO_TRACE). Reconstructs the exact proof tree for any conclusion.
    """
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def generate_proof_tree(self, target_node_id: str, max_depth: int = 10) -> Dict:
        """
        Performs a Breadth-First Search (BFS) backwards through DERIVED_FROM relations
        to expose the full reasoning trace.
        """
        node = self.graph.get_node(target_node_id)
        if not node:
            return {"error": "Node not found"}

        tree = {
            "node_id": target_node_id,
            "label": node.label,
            "confidence": node.confidence,
            "premises": []
        }

        if max_depth <= 0:
            tree["premises"].append({"warning": "MCT-06: Maximum trace depth reached"})
            return tree

        inbound_rels = self.graph.get_inbound_relations(target_node_id)
        derivation_rels = [r for r in inbound_rels if r.relation_type == RelationType.DERIVED_FROM]

        for rel in derivation_rels:
            premise_tree = self.generate_proof_tree(rel.source_node_id, max_depth - 1)
            tree["premises"].append(premise_tree)

        return tree
