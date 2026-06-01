from abc import ABC, abstractmethod

class BaseStorageAdapter(ABC):
    @abstractmethod
    def save_node(self, node): pass
    @abstractmethod
    def save_relation(self, relation): pass
