import uuid
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from .enums import RelationType

class Relation(BaseModel):
    relation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), frozen=True)
    source_node_id: str
    target_node_id: str
    relation_type: RelationType
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_ids: list[str] = Field(min_length=1)

    @model_validator(mode='after')
    def check_self_contradiction(self):
        if self.relation_type == RelationType.CONTRADICTS:
            if self.source_node_id == self.target_node_id:
                raise ValueError("A node cannot hold CONTRADICTS relation to itself (Rule DI-06)")
        return self
