"""
AI Reasoning Project — Knowledge Seeding
Bootstraps the empty graph with baseline facts for testing the Inference Engine.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from datetime import datetime, timezone
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType
from ai_reasoning.api.dependencies import global_graph

def seed_graph():
    print("Seeding Knowledge Graph with baseline test facts...")
    
    n1 = KnowledgeNode(
        node_type=NodeType.FACT,
        label="Water boils at 100C at 1atm",
        properties={"domain": "Physics"},
        source_ids=[uuid.uuid4()],
        decay_rate=0.0,
        confidence=0.99
    )
    
    n2 = KnowledgeNode(
        node_type=NodeType.FACT,
        label="The system is operating at 1atm",
        properties={"domain": "Physics"},
        source_ids=[uuid.uuid4()],
        decay_rate=0.0,
        confidence=0.90
    )
    
    global_graph.add_node(n1)
    global_graph.add_node(n2)
    print(f"Added {n1.entity_id} and {n2.entity_id}")
    print("Seeding complete.")

if __name__ == "__main__":
    seed_graph()
