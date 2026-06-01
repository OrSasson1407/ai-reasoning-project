import pytest
import uuid
from ai_reasoning.alignment.vcl import ValuesConstraintLayer, SafetyViolationError
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType
from datetime import datetime, timezone

def test_vcl_bypass_prevention():
    """Rule CV-008: Ensure constrained conclusions throw the correct error."""
    vcl = ValuesConstraintLayer()
    
    bad_node = KnowledgeNode(
        node_type=NodeType.CLAIM,
        label="Harmful plan",
        properties={},
        source_ids=[uuid.uuid4()],
        decay_rate=0.0,
        confidence=0.9
    )
    # Simulate tagging by the safety classifier
    bad_node.meta_tags.append("harm_generation")
    
    with pytest.raises(SafetyViolationError, match="CV-008"):
        vcl.evaluate_conclusion(bad_node, "trace_123")
