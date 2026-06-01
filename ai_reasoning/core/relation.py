from pydantic import BaseModel, model_validator
from typing import List, Any
from ai_reasoning.core.enums import RelationType

class Relation(BaseModel):
    source_node_id: Any
    target_node_id: Any
    relation_type: RelationType
    confidence: float
    source_ids: List[Any]

    @model_validator(mode='after')
    def check_self_contradiction(self) -> 'Relation':
        if self.relation_type == RelationType.CONTRADICTS and str(self.source_node_id) == str(self.target_node_id):
            raise ValueError("A node cannot hold CONTRADICTS relation to itself")
        return self
