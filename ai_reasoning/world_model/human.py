"""
AI Reasoning Project — Integrated Emotional Model
Sourced from: Architecture Doc v2.0 (Page 35)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType

@dataclass
class EmotionalStateVector:
    """
    Architecture v2.0 - Emotional state is an integrated dimension of human agent nodes.
    Values bounded [0.0, 1.0].
    """
    fear_anxiety: float = 0.0
    desire_motivation: float = 0.0
    cognitive_dissonance: float = 0.0
    bias_susceptibility: float = 0.0

    def calculate_irrationality_factor(self) -> float:
        """Computes how heavily emotion might override logic for this agent."""
        return min(1.0, (self.fear_anxiety * 1.5 + self.cognitive_dissonance + self.bias_susceptibility) / 3.0)

class HumanAgentNode(KnowledgeNode):
    """Extends standard KnowledgeNode to include emotional state."""
    
    emotional_state: EmotionalStateVector = field(default_factory=EmotionalStateVector)

    def __post_init__(self):
        self.node_type = NodeType.PERSON
        super().__post_init__()

    def update_emotional_state(self, new_state: EmotionalStateVector):
        """Updates state and bumps the last_updated timestamp."""
        self.emotional_state = new_state
        self.last_updated = datetime.now(timezone.utc)
