class PhysicalWorldModel:
    """Models physical laws, temporal constraints, and causality."""
    def __init__(self, graph):
        self.graph = graph

    def validate_causality(self, source_node, target_node) -> bool:
        """Rule DI-05: CAUSES relation invalid if effect precedes cause."""
        if source_node.valid_from >= target_node.valid_from:
            return False
        return True
