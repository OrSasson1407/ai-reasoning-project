from typing import Dict, List, Optional
from .node import Node
from .relation import Relation
from .enums import RelationType

class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.relations: Dict[str, Relation] = {}
        self.adjacency_list: Dict[str, List[str]] = {}

    def add_node(self, node: Node) -> None:
        self.nodes[node.entity_id] = node
        if node.entity_id not in self.adjacency_list:
            self.adjacency_list[node.entity_id] = []

    def add_relation(self, relation: Relation) -> None:
        if relation.source_node_id not in self.nodes or relation.target_node_id not in self.nodes:
            raise ValueError("No Orphan Relations allowed (Rule DI-01)")
            
        # Causal Precedence Check (Rule DI-05)
        if relation.relation_type == RelationType.CAUSES:
            source_node = self.nodes[relation.source_node_id]
            target_node = self.nodes[relation.target_node_id]
            if source_node.valid_from >= target_node.valid_from:
                raise ValueError("CAUSES relation invalid: Effect cannot precede cause (Rule DI-05)")

        self.relations[relation.relation_id] = relation
        self.adjacency_list[relation.source_node_id].append(relation.relation_id)

    def get_node(self, entity_id: str) -> Optional[Node]:
        return self.nodes.get(entity_id)
        
    def quarantine_cascade(self, node_id: str) -> List[str]:
        """
        When a node is quarantined, all conclusions derived from it 
        via DERIVED_FROM are also quarantined (Rule DI-07).
        """
        quarantined_ids = [node_id]
        if node_id in self.nodes:
            self.nodes[node_id].quarantine()
            
            for rel_id in self.adjacency_list.get(node_id, []):
                rel = self.relations[rel_id]
                if rel.relation_type == RelationType.DERIVED_FROM and rel.target_node_id == node_id:
                    quarantined_ids.extend(self.quarantine_cascade(rel.source_node_id))
                    
        return list(set(quarantined_ids))
