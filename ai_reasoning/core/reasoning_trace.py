"""
ReasoningTrace — AIC v1.0 §4.1 / §4.2
Every conclusion must carry a full auditable trace.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from .enums import ReasoningMode


@dataclass
class TraceStep:
    step_number:    int
    type:           str          # PREMISE | RULE_APPLICATION | DERIVATION | ABDUCTIVE_HYPOTHESIS
    node_id:        uuid.UUID
    statement:      str
    confidence_in:  float
    confidence_out: float
    rule_id:        Optional[str]       = None
    source_ids:     list[uuid.UUID]     = field(default_factory=list)


@dataclass
class ReasoningTrace:
    conclusion_id:        uuid.UUID
    session_id:           uuid.UUID
    steps:                list[TraceStep]     = field(default_factory=list)
    final_confidence:     float               = 0.0
    chain_depth:          int                 = 0
    reasoning_modes_used: list[ReasoningMode] = field(default_factory=list)
    meta_signals:         list[str]           = field(default_factory=list)
    trace_id:             uuid.UUID           = field(default_factory=uuid.uuid4)
    created_at:           datetime            = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_premise(self, node_id: uuid.UUID, statement: str,
                    confidence: float, source_ids: list[uuid.UUID] = None) -> None:
        self.steps.append(TraceStep(
            step_number=len(self.steps) + 1, type="PREMISE",
            node_id=node_id, statement=statement,
            confidence_in=confidence, confidence_out=confidence,
            source_ids=source_ids or [],
        ))

    def add_rule_application(self, node_id: uuid.UUID, rule_id: str,
                              statement: str, conf_in: float, conf_out: float) -> None:
        self.steps.append(TraceStep(
            step_number=len(self.steps) + 1, type="RULE_APPLICATION",
            node_id=node_id, statement=statement,
            confidence_in=conf_in, confidence_out=conf_out, rule_id=rule_id,
        ))

    def add_derivation(self, node_id: uuid.UUID, statement: str,
                        conf_in: float, conf_out: float) -> None:
        self.steps.append(TraceStep(
            step_number=len(self.steps) + 1, type="DERIVATION",
            node_id=node_id, statement=statement,
            confidence_in=conf_in, confidence_out=conf_out,
        ))

    def finalise(self, final_confidence: float) -> None:
        self.final_confidence = final_confidence
        self.chain_depth = len(self.steps)
        if self.chain_depth >= 5:
            self.meta_signals.append("MCT-06: chain length >= 5")

    def to_dict(self) -> dict:
        return {
            "trace_id":             str(self.trace_id),
            "conclusion_id":        str(self.conclusion_id),
            "session_id":           str(self.session_id),
            "final_confidence":     self.final_confidence,
            "chain_depth":          self.chain_depth,
            "reasoning_modes_used": [m.value for m in self.reasoning_modes_used],
            "meta_signals":         self.meta_signals,
            "created_at":           self.created_at.isoformat(),
            "steps": [
                {
                    "step_number":    s.step_number,
                    "type":           s.type,
                    "node_id":        str(s.node_id),
                    "statement":      s.statement,
                    "confidence_in":  s.confidence_in,
                    "confidence_out": s.confidence_out,
                    "rule_id":        s.rule_id,
                    "source_ids":     [str(x) for x in s.source_ids],
                }
                for s in self.steps
            ],
        }
