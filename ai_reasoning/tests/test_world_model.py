import pytest
from ai_reasoning.world_model.human import EmotionalStateVector, HumanAgentNode
import uuid

def test_emotional_state_irrationality():
    """Tests the emotional model calculations from Architecture v2.0"""
    vector = EmotionalStateVector(fear_anxiety=0.8, cognitive_dissonance=0.5)
    factor = vector.calculate_irrationality_factor()
    assert factor > 0.5  # High fear and dissonance should yield high irrationality

def test_human_agent_node_creation():
    node = HumanAgentNode(label="Agent Smith", properties={}, source_ids=[uuid.uuid4()], decay_rate=0.0, confidence=1.0)
    assert node.emotional_state.fear_anxiety == 0.0
