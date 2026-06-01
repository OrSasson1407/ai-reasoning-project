import pytest
from datetime import datetime, timedelta
from ai_reasoning.core.node import Node
from ai_reasoning.core.relation import Relation
from ai_reasoning.core.enums import NodeType, RelationType

def test_di03_temporal_consistency():
    """Rule DI-03: valid_from must be <= valid_until."""
    now = datetime.utcnow()
    past = now - timedelta(days=1)
    
    with pytest.raises(ValueError, match="valid_from must be <= valid_until"):
        Node(
            node_type=NodeType.FACT,
            content="Invalid temporal bounds",
            confidence=0.9,
            source_ids=["src-1"],
            valid_from=now,
            valid_until=past
        )

def test_di06_no_self_contradiction():
    """Rule DI-06: A node cannot hold CONTRADICTS relation to itself."""
    with pytest.raises(ValueError, match="A node cannot hold CONTRADICTS relation to itself"):
        Relation(
            source_node_id="node-a",
            target_node_id="node-a",
            relation_type=RelationType.CONTRADICTS,
            confidence=1.0,
            source_ids=["src-1"]
        )
