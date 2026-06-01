"""
AI Reasoning Project — Self-Reflection Mechanism
Sourced from: Architecture Doc v2.0 (Page 34)
"""
from ai_reasoning.core.graph import KnowledgeGraph

class SelfReflectionEngine:
    """
    Monitors the system's own reasoning paths for cognitive biases.
    """
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
        self.bias_audit_log = []

    def detect_confirmation_bias(self, target_node_id: str) -> dict:
        """
        Flags cases where the system accepts supporting evidence too readily
        while systematically downweighting contradictory evidence.
        """
        node = self.graph.get_node(target_node_id)
        if not node:
            return {"status": "error", "message": "Node not found"}

        inbound_rels = self.graph.get_inbound_relations(target_node_id)
        supporting = [r for r in inbound_rels if r.relation_type.value == "SUPPORTS"]
        contradicting = [r for r in inbound_rels if r.relation_type.value == "CONTRADICTS"]

        bias_detected = False
        warning = None

        # Heuristic: High volume of accepted weak support vs. rejected strong contradiction
        if len(supporting) > 3 and len(contradicting) > 0:
            avg_support_conf = sum(r.confidence for r in supporting) / len(supporting)
            max_contradict_conf = max(r.confidence for r in contradicting)
            
            if avg_support_conf < 0.6 and max_contradict_conf > 0.8:
                bias_detected = True
                warning = "Disconfirmation Resistance: System maintaining belief despite high-confidence contradiction."
                
        return {
            "node_id": target_node_id,
            "bias_detected": bias_detected,
            "warning": warning
        }
