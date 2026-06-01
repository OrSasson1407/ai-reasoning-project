from .node import Node
from .relation import Relation
from typing import Dict, Optional, List
import uuid

class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.relations: List[Relation] = []
    
    def add_node(self, node: Node): self.nodes[str(node.entity_id)] = node
    def get_node(self, node_id: uuid.UUID) -> Optional[Node]: return self.nodes.get(str(node_id))
        
    def require_node(self, node_id: uuid.UUID) -> Node:
        node = self.get_node(node_id)
        if not node: raise ValueError(f'Node {node_id} not found')
        return node

    def add_relation(self, relation: Relation): self.relations.append(relation)

    def quarantine_node(self, node_id: uuid.UUID):
        node = self.require_node(node_id)
        node.quarantine_flag = True

    def quarantine_cascade(self, node_id: uuid.UUID):
        self.quarantine_node(node_id)
        for rel in self.relations:
            if str(rel.source_node_id) == str(node_id):
                try: self.quarantine_cascade(rel.target_node_id)
                except ValueError: pass
