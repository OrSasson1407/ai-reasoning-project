from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.exceptions import SafetyViolationError

class ValuesConstraintLayer:
    def __init__(self): self.restricted_tags = {"harm_generation", "bias_detected", "pii_leak"}
    def evaluate_node(self, node: KnowledgeNode) -> bool:
        for tag in node.meta_tags:
            if tag in self.restricted_tags:
                node.quarantine_flag = True
                raise SafetyViolationError(f"Blocked by VCL. Reason: {tag}")
        return True
