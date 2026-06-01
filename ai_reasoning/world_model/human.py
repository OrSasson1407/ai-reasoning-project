from dataclasses import dataclass, field
from ai_reasoning.core.node import KnowledgeNode

@dataclass
class EmotionalStateVector:
    fear_anxiety: float = 0.0
    anger_frustration: float = 0.0
    trust_openness: float = 0.0
    cognitive_dissonance: float = 0.0
    def calculate_irrationality_factor(self) -> float:
        return (self.fear_anxiety + self.anger_frustration + self.cognitive_dissonance) / 2.0

@dataclass
class HumanAgentNode(KnowledgeNode):
    emotional_state: EmotionalStateVector = field(default_factory=EmotionalStateVector)
