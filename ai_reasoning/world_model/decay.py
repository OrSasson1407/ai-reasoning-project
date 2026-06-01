"""
AI Reasoning Project — Temporal Fact Decay
Sourced from: SRD Phase 2 ("Fact decay logic and staleness detection")
"""
from datetime import datetime, timezone
from ai_reasoning.core.graph import KnowledgeGraph

class TemporalDecayEngine:
    """
    Gradually lowers the confidence of temporally volatile facts.
    """
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def apply_decay(self):
        """
        Iterates over nodes. If a node has a decay_rate > 0, 
        its confidence drops as time elapses since its valid_from date.
        """
        now = datetime.now(timezone.utc)
        decayed_count = 0
        
        for node_id, node in self.graph.nodes.items():
            if getattr(node, 'decay_rate', 0.0) > 0.0:
                delta_days = (now - node.valid_from).days
                if delta_days > 0:
                    new_conf = max(0.05, node.confidence - (node.decay_rate * delta_days))
                    if new_conf != node.confidence:
                        self.graph.update_node_confidence(node_id, new_conf)
                        decayed_count += 1
                        
        return decayed_count
