import uuid
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from .enums import NodeType, ConfidenceLevel

class Node(BaseModel):
    entity_id: str = Field(default_factory=lambda: str(uuid.uuid4()), frozen=True)
    node_type: NodeType
    content: Any
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    source_ids: List[str] = Field(min_length=1)
    quarantined: bool = False

    @field_validator('valid_until')
    def check_temporal_consistency(cls, v, info):
        if v is not None and 'valid_from' in info.data:
            if info.data['valid_from'] > v:
                raise ValueError("valid_from must be <= valid_until (Rule DI-03)")
        return v

    @property
    def confidence_level(self) -> ConfidenceLevel:
        return ConfidenceLevel.get_level(self.confidence)

    def quarantine(self):
        self.quarantined = True
