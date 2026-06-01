"""
AI Reasoning Project — Tests for Inference Engine & CCP
Covers: CI-02, CI-06, CI-09, CV-006
"""

import uuid
import pytest
from ai_reasoning.core.graph import KnowledgeGraph, QuarantineBypassError
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType, ReasoningMode
from ai_reasoning.inference.engine import InferenceEngine
from datetime import datetime, timezone

def _make_node(label, confidence=0.8):
    return KnowledgeNode(
        node_type=NodeType.CLAIM,
        label=label,
        properties={},
        valid_from=datetime.now(timezone.utc),
        source_ids=[uuid.uuid4()],
        decay_rate=0.0,
        confidence=confidence
    )

class TestInferenceEngine:
    def test_ci06_deductive_degradation(self):
        g = KnowledgeGraph()
        n1 = _make_node("A", 0.90)
        n2 = _make_node("B", 0.90)
        g.add_node(n1); g.add_node(n2)
        
        engine = InferenceEngine(g)
        result = engine.derive_node([n1.entity_id, n2.entity_id], ReasoningMode.DEDUCTIVE, "C", NodeType.CLAIM)
        assert 0.85 <= result["confidence"] <= 0.86  # 0.90 * 0.95 = 0.855

    def test_ci06_inductive_cap(self):
        g = KnowledgeGraph()
        n1 = _make_node("A", 0.99)
        g.add_node(n1)
        
        engine = InferenceEngine(g)
        result = engine.derive_node([n1.entity_id], ReasoningMode.INDUCTIVE, "Pattern", NodeType.HYPOTHESIS)
        assert result["confidence"] <= 0.85  # Capped at 0.85

    def test_ci02_quarantine_bypass(self):
        g = KnowledgeGraph()
        n1 = _make_node("A", 0.90)
        g.add_node(n1)
        g.quarantine_node(n1.entity_id) # Node is quarantined
        
        engine = InferenceEngine(g)
        with pytest.raises(QuarantineBypassError, match="CV-006"):
            engine.derive_node([n1.entity_id], ReasoningMode.DEDUCTIVE, "C", NodeType.CLAIM)
            
    def test_ci09_hypothesis_isolation(self):
        g = KnowledgeGraph()
        n1 = _make_node("H", 0.40)
        n1.node_type = NodeType.HYPOTHESIS
        g.add_node(n1)
        
        engine = InferenceEngine(g)
        with pytest.raises(ValueError, match="CI-09"):
            engine.derive_node([n1.entity_id], ReasoningMode.DEDUCTIVE, "D", NodeType.CLAIM)
