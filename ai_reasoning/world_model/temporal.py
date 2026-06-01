from datetime import datetime
from ai_reasoning.core.graph import KnowledgeGraph

class TemporalDynamics:
    """Phase 2 feature: Fact decay logic and staleness detection."""
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def check_staleness(self):
        """Flags nodes that have passed their valid_until boundary."""
        stale_nodes = []
        now = datetime.utcnow()
        for node_id, node in self.graph.nodes.items():
            if node.valid_until and node.valid_until < now:
                stale_nodes.append(node_id)
        return stale_nodes
