"""
AI Reasoning Project — Specific Inference Engine Tests
Ensures Modus Ponens, Inductive limits, and Abductive caps behave strictly.
"""
import pytest
import uuid
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType
from ai_reasoning.core.exceptions import HypothesisIsolationError
from ai_reasoning.inference.deductive import DeductiveEngine
from ai_reasoning.inference.inductive import InductiveEngine
from ai_reasoning.inference.abductive import AbductiveEngine
from datetime import datetime, timezone

def _make_node(label, n_type, conf):
    node = KnowledgeNode(
        node_type=n_type,
        label=label,
        properties={},
        source_ids=[uuid.uuid4()],
        valid_from=datetime.now(timezone.utc),
        confidence=conf
    )
    return node

def test_ci09_hypothesis_isolation_deduction():
    """Rule CI-09: Abductive outputs cannot be sole deductive premises."""
    g = KnowledgeGraph()
    rule = _make_node("If A then B", NodeType.RULE, 0.95)
    hypo = _make_node("A", NodeType.HYPOTHESIS, 0.40) # Low confidence hypothesis
    
    g.add_node(rule); g.add_node(hypo)
    
    engine = DeductiveEngine(g)
    with pytest.raises(HypothesisIsolationError, match="CI-09"):
        engine.apply_modus_ponens(rule.entity_id, hypo.entity_id, "B")

def test_inductive_minimum_observations():
    """Inductive engine must reject attempts to generalize from < 3 facts."""
    g = KnowledgeGraph()
    n1 = _make_node("Obs 1", NodeType.FACT, 0.90)
    n2 = _make_node("Obs 2", NodeType.FACT, 0.90)
    
    g.add_node(n1); g.add_node(n2)
    
    engine = InductiveEngine(g)
    with pytest.raises(ValueError, match="minimum of 3 supporting observations"):
        engine.derive_pattern([n1.entity_id, n2.entity_id], "General Pattern")

def test_abductive_cap():
    """Abductive engine must strictly cap at 0.50 regardless of premise strength."""
    g = KnowledgeGraph()
    obs = _make_node("Strange Observation", NodeType.FACT, 0.99)
    g.add_node(obs)
    
    engine = AbductiveEngine(g)
    result = engine.propose_hypothesis(obs.entity_id, "Proposed Explanation")
    
    assert result["confidence"] <= 0.50
    assert result["mode"] == "ABDUCTIVE"
