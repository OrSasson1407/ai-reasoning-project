from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

CONFIDENCE_FLOOR = 0.05

@dataclass
class KnowledgeNode:
    node_type: Any = None
    label: str = 'default'
    properties: Dict[str, Any] = field(default_factory=dict)
    source_ids: List[uuid.UUID] = field(default_factory=list)
    valid_from: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.5
    entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    quarantine_flag: bool = False
    content: str = ''
    decay_rate: float = 0.0
    valid_until: Optional[datetime] = None
    meta_tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.valid_until and self.valid_from > self.valid_until:
            raise ValueError("valid_from must be <= valid_until")

    @property
    def is_stale(self) -> bool: return bool(self.valid_until and datetime.utcnow() > self.valid_until)
    @property
    def quarantined(self) -> bool: return self.quarantine_flag

Node = KnowledgeNode
