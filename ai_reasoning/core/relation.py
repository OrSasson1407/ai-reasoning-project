"""
AI Reasoning Project — Relation schema
Sourced from: DAD v1.0 §3.1, §3.2, §3.3
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .enums import RelationType


@dataclass
class Relation:
    """Typed directed edge between two KnowledgeNodes. (DAD §3.1)"""

    relation_type:   RelationType
    source_node_id:  uuid.UUID
    target_node_id:  uuid.UUID
    confidence:      float
    valid_from:      datetime
    source_ids:      list[uuid.UUID]

    relation_id:        uuid.UUID          = field(default_factory=uuid.uuid4)
    valid_until:        Optional[datetime] = None
    contradiction_flag: bool               = False
    causal_strength:    Optional[float]    = None
    causal_lag:         Optional[float]    = None
    causal_conditions:  list[str]          = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be [0.0, 1.0], got {self.confidence}")
        if self.valid_until is not None and self.valid_from > self.valid_until:
            raise ValueError("valid_from must be <= valid_until")
        if not self.source_ids:
            raise ValueError("Every relation must have at least one source_id (DI-04)")
        if (self.relation_type == RelationType.CONTRADICTS
                and self.source_node_id == self.target_node_id):
            raise ValueError("A node cannot CONTRADICT itself (DI-06)")
        if self.relation_type == RelationType.CAUSES:
            if self.causal_strength is not None and not (0.0 <= self.causal_strength <= 1.0):
                raise ValueError(f"causal_strength must be [0.0, 1.0], got {self.causal_strength}")

    @property
    def is_currently_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.valid_until is not None and now > self.valid_until:
            return False
        return True

    @property
    def is_strong_causal(self) -> bool:
        return (self.relation_type == RelationType.CAUSES
                and self.causal_strength is not None
                and self.causal_strength >= 0.9)

    @property
    def is_weak_causal(self) -> bool:
        return (self.relation_type == RelationType.CAUSES
                and self.causal_strength is not None
                and 0.5 <= self.causal_strength < 0.9)

    def __repr__(self) -> str:
        causal = (f" [strength={self.causal_strength:.2f}]"
                  if self.relation_type == RelationType.CAUSES and self.causal_strength else "")
        return (f"Relation({self.source_node_id} "
                f"--[{self.relation_type.value}]--> "
                f"{self.target_node_id} conf={self.confidence:.2f}{causal})")
