import pytest
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.node import Node
from ai_reasoning.core.relation import Relation
from ai_reasoning.core.enums import NodeType, RelationType
from ai_reasoning.ccp.detector import ContradictionDetector

def test_ci05_quarantine_cascade():
    """Rule CI-05 / DI-07: Quarantine propagation through DERIVED_FROM."""
    graph = KnowledgeGraph()
    n1 = Node(node_type=NodeType.FACT, content="A", confidence=0.9, source_ids=["s1"])
    n2 = Node(node_type=NodeType.FACT, content="B (derived)", confidence=0.8, source_ids=["s2"])
    
    graph.add_node(n1)
    graph.add_node(n2)
    
    rel = Relation(
        source_node_id=n1.entity_id,
        target_node_id=n2.entity_id,
        relation_type=RelationType.DERIVED_FROM,
        confidence=0.9,
        source_ids=["s3"]
    )
    graph.add_relation(rel)
    
    # Trigger cascade
    graph.quarantine_cascade(n1.entity_id)
    
    assert graph.get_node(n1.entity_id).quarantined is True
    assert graph.get_node(n2.entity_id).quarantined is True
