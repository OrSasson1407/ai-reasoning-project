"""
AI Reasoning Project — Knowledge Node schema
Sourced from: DAD v1.0 §2.1, §5.3
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .enums import ConfidenceLevel, EpistemicModel, NodeType, SourceType

CONFIDENCE_MIN      = 0.0
CONFIDENCE_MAX      = 1.0
CONFIDENCE_FLOOR    = 0.05
STALENESS_THRESHOLD = 0.30


@dataclass
class Source:
    source_type:       SourceType
    timestamp:         datetime
    source_id:         uuid.UUID        = field(default_factory=uuid.uuid4)
    reliability_score: float            = 0.70
    domain_expertise:  list[str]        = field(default_factory=list)
    url_or_ref:        Optional[str]    = None
    bias_flags:        list[str]        = field(default_factory=list)
    track_record:      Optional[float]  = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.reliability_score <= 1.0):
            raise ValueError("reliability_score must be in [0.0, 1.0]")


@dataclass
class KnowledgeNode:
    """Atomic unit of all stored knowledge. (DAD §2.1)"""

    node_type:   NodeType
    label:       str
    properties:  dict[str, Any]
    valid_from:  datetime
    source_ids:  list[uuid.UUID]
    decay_rate:  float

    entity_id:          uuid.UUID          = field(default_factory=uuid.uuid4)
    confidence:         float              = 0.70
    confidence_model:   EpistemicModel     = EpistemicModel.BAYESIAN
    valid_until:        Optional[datetime] = None
    contradiction_flag: bool               = False
    quarantine_flag:    bool               = False
    created_at:         datetime           = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated:       datetime           = field(default_factory=lambda: datetime.now(timezone.utc))
    meta_tags:          list[str]          = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not (CONFIDENCE_MIN <= self.confidence <= CONFIDENCE_MAX):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")
        if self.valid_until is not None and self.valid_from > self.valid_until:
            raise ValueError(f"valid_from must be <= valid_until")
        if not self.source_ids:
            raise ValueError("Every node must have at least one source_id (DI-04)")
        if self.node_type == NodeType.HYPOTHESIS and self.confidence >= 1.0:
            raise ValueError("HYPOTHESIS nodes must have confidence < 1.0")
        if self.node_type == NodeType.MATHEMATICAL_OBJECT and self.decay_rate != 0.0:
            raise ValueError("MATHEMATICAL_OBJECT nodes must have decay_rate=0.0")

    @property
    def confidence_level(self) -> ConfidenceLevel:
        return ConfidenceLevel.from_score(self.confidence)

    @property
    def is_stale(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.valid_until is not None and now > self.valid_until:
            return True
        return self.confidence < STALENESS_THRESHOLD

    @property
    def is_active(self) -> bool:
        return not self.quarantine_flag and not self.is_stale

    def apply_decay(self, elapsed_seconds: float) -> None:
        if self.decay_rate == 0.0:
            return
        new_conf = self.confidence * math.exp(-self.decay_rate * elapsed_seconds)
        floor = 0.0 if self.contradiction_flag else CONFIDENCE_FLOOR
        self.confidence = max(floor, new_conf)
        self.last_updated = datetime.now(timezone.utc)

    def bayesian_update(self, likelihood: float, prior_evidence: float) -> None:
        if prior_evidence <= 0:
            raise ValueError("prior_evidence (P(E)) must be > 0")
        updated = (likelihood * self.confidence) / prior_evidence
        self.confidence = min(CONFIDENCE_MAX, max(CONFIDENCE_FLOOR, updated))
        self.last_updated = datetime.now(timezone.utc)

    def quarantine(self) -> None:
        self.quarantine_flag = True
        self.last_updated = datetime.now(timezone.utc)

    def release_quarantine(self) -> None:
        self.quarantine_flag = False
        self.last_updated = datetime.now(timezone.utc)

    def flag_contradiction(self) -> None:
        self.contradiction_flag = True
        self.last_updated = datetime.now(timezone.utc)

    def clear_contradiction(self) -> None:
        self.contradiction_flag = False
        self.last_updated = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        markers = ""
        if self.is_stale:         markers += " [STALE]"
        if self.quarantine_flag:  markers += " [QUARANTINED]"
        if self.contradiction_flag: markers += " [CONTRADICTION]"
        return (f"KnowledgeNode({self.node_type.value} | '{self.label}' | "
                f"conf={self.confidence:.2f} [{self.confidence_level.value}]{markers})")
