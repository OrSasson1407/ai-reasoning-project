from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import ReasoningMode

class EpistemicHorizonError(Exception):
    pass

class EpistemicHorizon:
    def __init__(self, min_confidence: float = 0.20, max_depth: int = 5):
        self.min_confidence = min_confidence
        self.max_depth = max_depth

    def validate_trajectory(self, premises: list[KnowledgeNode], mode: ReasoningMode, current_depth: int):
        """
        Stops the engine from deducing conclusions from increasingly weak premises.
        """
        if current_depth >= self.max_depth:
            raise EpistemicHorizonError(f"Reasoning depth {current_depth} exceeds the Epistemic Horizon of {self.max_depth}.")
            
        for node in premises:
            if node.confidence < self.min_confidence:
                raise EpistemicHorizonError(
                    f"Premise {node.entity_id} confidence ({node.confidence}) is below the Epistemic Horizon ({self.min_confidence})."
                )
        return True
