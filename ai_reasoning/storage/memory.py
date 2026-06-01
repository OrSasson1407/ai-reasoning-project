from .base import BaseStorageAdapter

class InMemoryStorage(BaseStorageAdapter):
    """Temporary in-memory storage for testing DI-rules."""
    def __init__(self):
        self.nodes = {}
        self.relations = {}

    def save_node(self, node):
        self.nodes[node.entity_id] = node

    def save_relation(self, relation):
        self.relations[relation.relation_id] = relation
