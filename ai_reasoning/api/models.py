"""
Pydantic schemas — AIC v1.0 §2, §4
"""

from __future__ import annotations
from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# ── Ingest ────────────────────────────────────────────────────────────────

class SourceIn(BaseModel):
    source_type:       str   = "USER_ASSERTION"
    reliability_score: float = Field(0.70, ge=0.0, le=1.0)
    url_or_ref:        Optional[str] = None

class RelationIn(BaseModel):
    relation_type:   str
    target_node_id:  UUID
    confidence:      float = Field(0.80, ge=0.0, le=1.0)
    causal_strength: Optional[float] = Field(None, ge=0.0, le=1.0)

class FactIn(BaseModel):
    node_type:   str
    label:       str
    properties:  dict[str, Any]     = {}
    valid_from:  Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source:      SourceIn           = SourceIn()
    relations:   list[RelationIn]   = []

class IngestRequest(BaseModel):
    facts: list[FactIn]

class IngestResult(BaseModel):
    node_id: str
    status:  str   # COMMITTED | QUARANTINED | ERROR

class IngestResponse(BaseModel):
    ingested:                list[IngestResult]
    contradictions_detected: list[dict] = []


# ── Infer ─────────────────────────────────────────────────────────────────

class InferRequest(BaseModel):
    query:           str
    context_node_ids:list[str]  = []
    min_confidence:  float      = Field(0.30, ge=0.0, le=1.0)
    include_trace:   bool       = True

class ConclusionOut(BaseModel):
    conclusion_id:    str
    statement:        str
    confidence:       float
    certainty_level:  str
    reasoning_mode:   str
    trace_id:         Optional[str]
    supporting_nodes: list[str]
    meta_signals:     list[str]

class InferResponse(BaseModel):
    status:          str   # success | halted | insufficient_evidence
    conclusions:     list[ConclusionOut] = []
    knowledge_gaps:  list[str]           = []
    meta_signals:    list[str]           = []
    halt_reason:     Optional[str]       = None
    contradiction:   Optional[dict]      = None


# ── Node query ────────────────────────────────────────────────────────────

class NodeQueryRequest(BaseModel):
    min_confidence:      float = 0.0
    max_confidence:      float = 1.0
    node_types:          list[str]  = []
    include_stale:       bool  = False
    include_quarantined: bool  = False
    valid_at:            Optional[datetime] = None

class NodeOut(BaseModel):
    entity_id:          str
    node_type:          str
    label:              str
    confidence:         float
    confidence_level:   str
    is_stale:           bool
    quarantine_flag:    bool
    contradiction_flag: bool
    valid_from:         str
    valid_until:        Optional[str]
    meta_tags:          list[str]


# ── Contradiction ─────────────────────────────────────────────────────────

class ContradictionCheckRequest(BaseModel):
    node_a_id:          str
    node_b_id:          str
    contradiction_type: str = "HARD"   # HARD | SOFT | TEMPORAL

class ResolveRequest(BaseModel):
    contradiction_id: str
    resolution_type:  str = "RESOLVED"


# ── Trace ─────────────────────────────────────────────────────────────────

class TraceStepOut(BaseModel):
    step_number:    int
    type:           str
    node_id:        str
    statement:      str
    confidence_in:  float
    confidence_out: float
    rule_id:        Optional[str]

class TraceOut(BaseModel):
    trace_id:             str
    conclusion_id:        str
    final_confidence:     float
    chain_depth:          int
    reasoning_modes_used: list[str]
    meta_signals:         list[str]
    steps:                list[TraceStepOut]
