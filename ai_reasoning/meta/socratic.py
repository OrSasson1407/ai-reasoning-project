"""
AI Reasoning Project — Socratic Clarification Engine
Sourced from: SRD Phase 3
"""

from ai_reasoning.core.graph import KnowledgeGraph
import uuid

class SocraticEngine:
    """
    Identifies missing premises and generates queries to resolve them,
    preventing confident hallucination when data is missing.
    """
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def generate_probe(self, target_node_id: uuid.UUID) -> dict:
        """
        Analyzes an uncertain node and formulates the exact missing data requirements.
        """
        node = self.graph.get_node(target_node_id)
        if not node:
            return {"error": "Node not found"}

        inbound_rels = self.graph.get_inbound_relations(target_node_id)
        
        if not inbound_rels:
            return {
                "probe_type": "ORPHAN_FACT",
                "question": f"Node '{node.label}' lacks supporting premises. What is the source of this claim?",
                "target": str(target_node_id)
            }
            
        # Detect weak links
        weak_links = [r for r in inbound_rels if r.confidence < 0.5]
        if weak_links:
            return {
                "probe_type": "WEAK_PREMISE",
                "question": f"The conclusion depends on uncertain premises. Can we verify {weak_links[0].source_node_id}?",
                "target": str(weak_links[0].relation_id)
            }

        return {"probe_type": "SUFFICIENT", "question": None}
