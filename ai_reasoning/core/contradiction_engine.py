"""
Contradiction Detection Engine — CCP v1.0 §2
CP-01 Hard Contradiction
CP-02 Soft Contradiction
CP-03 Confidence Collapse
CP-04 Temporal Inconsistency
CP-05 Causal Loop
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .enums import ResolutionStatus, RelationType
from .graph import KnowledgeGraph
from .node import KnowledgeNode

HIGH_CONF      = 0.70
SOFT_CONF      = 0.50
SOFT_PENALTY   = 0.20


@dataclass
class ContradictionReport:
    contradiction_id:   uuid.UUID = field(default_factory=uuid.uuid4)
    contradiction_type: str       = "HARD"
    severity:           str       = "HALT"
    detected_at:        datetime  = field(default_factory=lambda: datetime.now(timezone.utc))
    node_a_id:          Optional[uuid.UUID] = None
    node_b_id:          Optional[uuid.UUID] = None
    belief_path_a:      list[uuid.UUID]     = field(default_factory=list)
    belief_path_b:      list[uuid.UUID]     = field(default_factory=list)
    quarantined_nodes:  list[uuid.UUID]     = field(default_factory=list)
    resolution_status:  ResolutionStatus    = ResolutionStatus.UNRESOLVED
    detail:             str                 = ""

    def to_dict(self) -> dict:
        return {
            "contradiction_id":  str(self.contradiction_id),
            "contradiction_type":self.contradiction_type,
            "severity":          self.severity,
            "detected_at":       self.detected_at.isoformat(),
            "node_a_id":         str(self.node_a_id) if self.node_a_id else None,
            "node_b_id":         str(self.node_b_id) if self.node_b_id else None,
            "belief_path_a":     [str(x) for x in self.belief_path_a],
            "belief_path_b":     [str(x) for x in self.belief_path_b],
            "quarantined_nodes": [str(x) for x in self.quarantined_nodes],
            "resolution_status": self.resolution_status.value,
            "detail":            self.detail,
        }


class ContradictionEngine:

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph
        self.reports: list[ContradictionReport] = []

    # ── CP-01: Hard logical contradiction ────────────────────────────

    def check_hard_contradiction(self, node_a_id: uuid.UUID,
                                   node_b_id: uuid.UUID) -> Optional[ContradictionReport]:
        """
        CP-01: Both nodes >= 0.70 confidence and directly contradictory.
        HALT — quarantine both and all descendants.
        """
        a = self.graph.get_node(node_a_id)
        b = self.graph.get_node(node_b_id)
        if a is None or b is None:
            return None
        if a.confidence < HIGH_CONF or b.confidence < HIGH_CONF:
            return None  # not a hard contradiction yet

        self.graph.flag_contradiction(node_a_id, node_b_id)
        q_a = self.graph.quarantine_node(node_a_id)
        q_b = self.graph.quarantine_node(node_b_id)
        all_quarantined = list(set(q_a + q_b))

        report = ContradictionReport(
            contradiction_type="HARD", severity="HALT",
            node_a_id=node_a_id, node_b_id=node_b_id,
            belief_path_a=self.graph.provenance_trace(node_a_id),
            belief_path_b=self.graph.provenance_trace(node_b_id),
            quarantined_nodes=all_quarantined,
            detail=f"Hard contradiction: '{a.label}' vs '{b.label}'",
        )
        self.reports.append(report)
        return report

    # ── CP-02: Soft contradiction ─────────────────────────────────────

    def check_soft_contradiction(self, node_a_id: uuid.UUID,
                                   node_b_id: uuid.UUID) -> Optional[ContradictionReport]:
        """
        CP-02: Mutually exclusive in context but not strict negations.
        FLAG — reduce derived confidence by SOFT_PENALTY.
        """
        a = self.graph.get_node(node_a_id)
        b = self.graph.get_node(node_b_id)
        if a is None or b is None:
            return None
        if max(a.confidence, b.confidence) < SOFT_CONF:
            return None

        a.flag_contradiction()
        b.flag_contradiction()

        report = ContradictionReport(
            contradiction_type="SOFT", severity="FLAG",
            node_a_id=node_a_id, node_b_id=node_b_id,
            detail=(f"Soft contradiction between '{a.label}' and '{b.label}'. "
                    f"Confidence penalty {SOFT_PENALTY} applied to derived conclusions."),
        )
        self.reports.append(report)
        return report

    # ── CP-03: Confidence collapse ────────────────────────────────────

    def check_confidence_collapse(self, path_a_nodes: list[uuid.UUID], conclusion_a: str,
                                    path_b_nodes: list[uuid.UUID], conclusion_b: str,
                                    conf_a: float, conf_b: float) -> Optional[ContradictionReport]:
        """
        CP-03: Two independent high-confidence paths reach mutually exclusive conclusions.
        HALT the weaker path.
        """
        if conf_a < HIGH_CONF or conf_b < HIGH_CONF:
            return None

        weaker_path  = path_a_nodes if conf_a <= conf_b else path_b_nodes
        weaker_label = conclusion_a if conf_a <= conf_b else conclusion_b

        for nid in weaker_path:
            self.graph.quarantine_node(nid)

        report = ContradictionReport(
            contradiction_type="CONFIDENCE_COLLAPSE", severity="HALT",
            belief_path_a=path_a_nodes, belief_path_b=path_b_nodes,
            quarantined_nodes=weaker_path,
            detail=(f"Confidence collapse: '{conclusion_a}' (conf={conf_a:.2f}) vs "
                    f"'{conclusion_b}' (conf={conf_b:.2f}). "
                    f"Halted weaker path: '{weaker_label}'."),
        )
        self.reports.append(report)
        return report

    # ── CP-04: Temporal inconsistency ────────────────────────────────

    def check_temporal_inconsistency(self, node_a_id: uuid.UUID,
                                       node_b_id: uuid.UUID) -> Optional[ContradictionReport]:
        """
        CP-04: Overlapping validity windows with incompatible states.
        FLAG — mark both SUSPECT for overlap period.
        """
        a = self.graph.get_node(node_a_id)
        b = self.graph.get_node(node_b_id)
        if a is None or b is None:
            return None

        a_end = a.valid_until
        b_start = b.valid_from
        if a_end is None or b_start is None:
            return None

        # Check overlap
        if not (a.valid_from <= b_start <= a_end):
            return None  # no overlap

        a.flag_contradiction()
        b.flag_contradiction()

        report = ContradictionReport(
            contradiction_type="TEMPORAL", severity="FLAG",
            node_a_id=node_a_id, node_b_id=node_b_id,
            detail=(f"Temporal overlap: '{a.label}' valid until {a_end.isoformat()}, "
                    f"'{b.label}' starts {b_start.isoformat()}"),
        )
        self.reports.append(report)
        return report

    # ── CP-05: Causal loop detection ─────────────────────────────────

    def check_causal_loop(self, start_node_id: uuid.UUID) -> Optional[ContradictionReport]:
        """
        CP-05: Traverse CAUSES chain; detect cycle; HALT and quarantine.
        """
        paths = self.graph.causal_forward(start_node_id, max_depth=20)
        loop_paths = [p for p in paths if "__CAUSAL_LOOP__" in p]
        if not loop_paths:
            return None

        loop_nodes = [nid for nid in loop_paths[0]
                      if isinstance(nid, uuid.UUID)]
        for nid in loop_nodes:
            self.graph.quarantine_node(nid)

        report = ContradictionReport(
            contradiction_type="CAUSAL_LOOP", severity="HALT",
            quarantined_nodes=loop_nodes,
            detail=f"Causal loop detected starting from {start_node_id}. Loop path quarantined.",
        )
        self.reports.append(report)
        return report

    def open_reports(self) -> list[ContradictionReport]:
        return [r for r in self.reports if r.resolution_status == ResolutionStatus.UNRESOLVED]

    def resolve(self, contradiction_id: uuid.UUID, action: str = "RESOLVED") -> bool:
        for r in self.reports:
            if r.contradiction_id == contradiction_id:
                r.resolution_status = ResolutionStatus.RESOLVED
                # Release quarantine on affected nodes
                for nid in r.quarantined_nodes:
                    node = self.graph.get_node(nid)
                    if node:
                        node.release_quarantine()
                        node.clear_contradiction()
                return True
        return False
