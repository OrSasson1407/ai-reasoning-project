"""
Inference Engine — RRS v1.0 §2 (Deductive rules DED-01..06)
Primary reasoning mode. Inductive/abductive added in Phase 2.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .enums import ReasoningMode, NodeType, RelationType
from .graph import KnowledgeGraph
from .node import KnowledgeNode
from .relation import Relation
from .confidence import chain_penalty, causal_propagation, apply_floor
from .reasoning_trace import ReasoningTrace, TraceStep

MIN_PREMISE_CONF  = 0.30   # RRS §1.2
MIN_RULE_CONF     = 0.80   # DED-01 premise (1)
HIGH_CONF         = 0.70   # contradiction threshold


@dataclass
class Conclusion:
    conclusion_id:    uuid.UUID = field(default_factory=uuid.uuid4)
    statement:        str       = ""
    confidence:       float     = 0.0
    certainty_level:  str       = "PROBABILISTIC"
    reasoning_mode:   ReasoningMode = ReasoningMode.DEDUCTIVE
    trace:            Optional[ReasoningTrace] = None
    supporting_nodes: list[uuid.UUID] = field(default_factory=list)
    valid_from:       datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until:      Optional[datetime] = None
    meta_signals:     list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "conclusion_id":   str(self.conclusion_id),
            "statement":       self.statement,
            "confidence":      self.confidence,
            "certainty_level": self.certainty_level,
            "reasoning_mode":  self.reasoning_mode.value,
            "trace_id":        str(self.trace.trace_id) if self.trace else None,
            "supporting_nodes":[str(n) for n in self.supporting_nodes],
            "valid_from":      self.valid_from.isoformat(),
            "valid_until":     self.valid_until.isoformat() if self.valid_until else None,
            "meta_signals":    self.meta_signals,
        }


class InferenceEngine:
    """
    Implements RRS deductive rules DED-01 through DED-06.
    Every conclusion has a full ReasoningTrace.
    Quarantined nodes are never used as premises (CI-02).
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph
        self.session_id = uuid.uuid4()

    # ── DED-01: Modus Ponens ──────────────────────────────────────────

    def modus_ponens(self, premise_id: uuid.UUID, rule_conf: float,
                     conclusion_label: str, conclusion_node_type: NodeType,
                     conclusion_properties: dict,
                     conclusion_source_ids: list[uuid.UUID]) -> Optional[Conclusion]:
        """
        DED-01: IF P THEN Q. Given P is true, conclude Q.
        rule_conf must be >= 0.80. premise_id must be active.
        """
        premise = self._require_active(premise_id, "DED-01")
        if rule_conf < MIN_RULE_CONF:
            return None  # rule not strong enough

        conf_out = min(rule_conf, premise.confidence)
        if conf_out < MIN_PREMISE_CONF:
            return None

        trace = self._new_trace()
        trace.add_premise(premise.entity_id, premise.label, premise.confidence,
                          premise.source_ids)
        trace.add_rule_application(premise.entity_id, "DED-01",
                                   f"IF [{premise.label}] THEN [{conclusion_label}]",
                                   premise.confidence, conf_out)

        conclusion_node = self._commit_conclusion_node(
            conclusion_label, conclusion_node_type, conclusion_properties,
            conf_out, conclusion_source_ids)

        trace.add_derivation(conclusion_node.entity_id, conclusion_label,
                             conf_out, conf_out)
        trace.finalise(conf_out)
        trace.reasoning_modes_used.append(ReasoningMode.DEDUCTIVE)

        # DERIVED_FROM relation
        self.graph.add_relation(Relation(
            relation_type=RelationType.DERIVED_FROM,
            source_node_id=conclusion_node.entity_id,
            target_node_id=premise.entity_id,
            confidence=conf_out,
            valid_from=datetime.now(timezone.utc),
            source_ids=conclusion_source_ids,
        ))

        return Conclusion(
            statement=conclusion_label, confidence=conf_out,
            certainty_level="HIGH", reasoning_mode=ReasoningMode.DEDUCTIVE,
            trace=trace, supporting_nodes=[premise.entity_id],
        )

    # ── DED-02: Modus Tollens ─────────────────────────────────────────

    def modus_tollens(self, rule_conf: float, not_q_id: uuid.UUID,
                      not_p_label: str, not_p_node_type: NodeType,
                      not_p_properties: dict,
                      not_p_source_ids: list[uuid.UUID]) -> Optional[Conclusion]:
        """
        DED-02: IF P THEN Q. Q is FALSE => P is FALSE.
        not_q confidence must be >= 0.70.
        """
        not_q = self._require_active(not_q_id, "DED-02")
        if rule_conf < MIN_RULE_CONF:
            return None
        if not_q.confidence < HIGH_CONF:
            return None   # NOT Q not strong enough

        conf_out = min(rule_conf, not_q.confidence)

        trace = self._new_trace()
        trace.add_premise(not_q.entity_id, f"NOT: {not_q.label}", not_q.confidence,
                          not_q.source_ids)
        trace.add_rule_application(not_q.entity_id, "DED-02",
                                   f"NOT [{not_q.label}] => NOT P",
                                   not_q.confidence, conf_out)

        conclusion_node = self._commit_conclusion_node(
            not_p_label, not_p_node_type, not_p_properties,
            conf_out, not_p_source_ids)

        trace.add_derivation(conclusion_node.entity_id, not_p_label, conf_out, conf_out)
        trace.finalise(conf_out)
        trace.reasoning_modes_used.append(ReasoningMode.DEDUCTIVE)

        self.graph.add_relation(Relation(
            relation_type=RelationType.DERIVED_FROM,
            source_node_id=conclusion_node.entity_id,
            target_node_id=not_q.entity_id,
            confidence=conf_out,
            valid_from=datetime.now(timezone.utc),
            source_ids=not_p_source_ids,
        ))

        return Conclusion(
            statement=not_p_label, confidence=conf_out,
            certainty_level="HIGH", reasoning_mode=ReasoningMode.DEDUCTIVE,
            trace=trace, supporting_nodes=[not_q.entity_id],
        )

    # ── DED-03: Hypothetical Syllogism ───────────────────────────────

    def hypothetical_syllogism(self, rule_pq_conf: float, rule_qr_conf: float,
                                p_id: uuid.UUID, r_label: str,
                                r_node_type: NodeType, r_properties: dict,
                                r_source_ids: list[uuid.UUID]) -> Optional[Conclusion]:
        """
        DED-03: P->Q and Q->R gives P->R.
        conf = rule_pq_conf * rule_qr_conf.
        """
        p_node = self._require_active(p_id, "DED-03")
        if rule_pq_conf < MIN_RULE_CONF or rule_qr_conf < MIN_RULE_CONF:
            return None

        conf_out, warned = chain_penalty([rule_pq_conf, rule_qr_conf])
        if conf_out < MIN_PREMISE_CONF:
            return None

        trace = self._new_trace()
        if warned:
            trace.meta_signals.append("MCT-06: chain >= 5 hops")
        trace.add_premise(p_node.entity_id, p_node.label, p_node.confidence,
                          p_node.source_ids)
        trace.add_rule_application(p_node.entity_id, "DED-03",
                                   f"P->Q (conf={rule_pq_conf}) + Q->R (conf={rule_qr_conf}) => P->R",
                                   p_node.confidence, conf_out)

        r_node = self._commit_conclusion_node(r_label, r_node_type, r_properties,
                                               conf_out, r_source_ids)
        trace.add_derivation(r_node.entity_id, r_label, conf_out, conf_out)
        trace.finalise(conf_out)
        trace.reasoning_modes_used.append(ReasoningMode.DEDUCTIVE)

        self.graph.add_relation(Relation(
            relation_type=RelationType.DERIVED_FROM,
            source_node_id=r_node.entity_id,
            target_node_id=p_node.entity_id,
            confidence=conf_out,
            valid_from=datetime.now(timezone.utc),
            source_ids=r_source_ids,
        ))

        return Conclusion(
            statement=r_label, confidence=conf_out,
            certainty_level="HIGH", reasoning_mode=ReasoningMode.DEDUCTIVE,
            trace=trace, supporting_nodes=[p_node.entity_id],
        )

    # ── DED-04: Universal Instantiation ──────────────────────────────

    def universal_instantiation(self, universal_rule_conf: float,
                                  instance_id: uuid.UUID, property_label: str,
                                  property_node_type: NodeType,
                                  property_properties: dict,
                                  property_source_ids: list[uuid.UUID]) -> Optional[Conclusion]:
        """
        DED-04: ALL C have property P. X is in C => X has P.
        Blocked if a specific EXCEPTION node exists for X.
        """
        instance = self._require_active(instance_id, "DED-04")

        # Check for exception node in graph
        exceptions = [
            r for r in self.graph.get_outbound_relations(instance_id)
            if "EXCEPTION" in (r.relation_type.value if hasattr(r.relation_type, "value") else "")
        ]
        if exceptions:
            return None  # specific exception overrides universal rule

        conf_out = min(universal_rule_conf, instance.confidence)
        if conf_out < MIN_PREMISE_CONF:
            return None

        trace = self._new_trace()
        trace.add_premise(instance.entity_id, instance.label, instance.confidence,
                          instance.source_ids)
        trace.add_rule_application(instance.entity_id, "DED-04",
                                   f"ALL members have [{property_label}] => [{instance.label}] has it",
                                   instance.confidence, conf_out)

        prop_node = self._commit_conclusion_node(
            property_label, property_node_type, property_properties,
            conf_out, property_source_ids)

        trace.add_derivation(prop_node.entity_id, property_label, conf_out, conf_out)
        trace.finalise(conf_out)
        trace.reasoning_modes_used.append(ReasoningMode.DEDUCTIVE)

        self.graph.add_relation(Relation(
            relation_type=RelationType.DERIVED_FROM,
            source_node_id=prop_node.entity_id,
            target_node_id=instance.entity_id,
            confidence=conf_out,
            valid_from=datetime.now(timezone.utc),
            source_ids=property_source_ids,
        ))
        self.graph.add_relation(Relation(
            relation_type=RelationType.HAS_PROPERTY,
            source_node_id=instance.entity_id,
            target_node_id=prop_node.entity_id,
            confidence=conf_out,
            valid_from=datetime.now(timezone.utc),
            source_ids=property_source_ids,
        ))

        return Conclusion(
            statement=f"{instance.label} has property: {property_label}",
            confidence=conf_out, certainty_level="HIGH",
            reasoning_mode=ReasoningMode.DEDUCTIVE,
            trace=trace, supporting_nodes=[instance.entity_id],
        )

    # ── DED-05: Disjunctive Syllogism ────────────────────────────────

    def disjunctive_syllogism(self, disjunction_conf: float, not_p_id: uuid.UUID,
                               q_label: str, q_node_type: NodeType,
                               q_properties: dict,
                               q_source_ids: list[uuid.UUID]) -> Optional[Conclusion]:
        """
        DED-05: P OR Q is true. P is false => Q is true.
        Requires exclusive disjunction.
        """
        not_p = self._require_active(not_p_id, "DED-05")
        conf_out = min(disjunction_conf, not_p.confidence)
        if conf_out < MIN_PREMISE_CONF:
            return None

        trace = self._new_trace()
        trace.add_premise(not_p.entity_id, f"NOT P: {not_p.label}", not_p.confidence,
                          not_p.source_ids)
        trace.add_rule_application(not_p.entity_id, "DED-05",
                                   f"(P OR Q) AND NOT P => Q: {q_label}",
                                   not_p.confidence, conf_out)

        q_node = self._commit_conclusion_node(q_label, q_node_type, q_properties,
                                               conf_out, q_source_ids)
        trace.add_derivation(q_node.entity_id, q_label, conf_out, conf_out)
        trace.finalise(conf_out)
        trace.reasoning_modes_used.append(ReasoningMode.DEDUCTIVE)

        self.graph.add_relation(Relation(
            relation_type=RelationType.DERIVED_FROM,
            source_node_id=q_node.entity_id,
            target_node_id=not_p.entity_id,
            confidence=conf_out,
            valid_from=datetime.now(timezone.utc),
            source_ids=q_source_ids,
        ))

        return Conclusion(
            statement=q_label, confidence=conf_out,
            certainty_level="HIGH", reasoning_mode=ReasoningMode.DEDUCTIVE,
            trace=trace, supporting_nodes=[not_p.entity_id],
        )

    # ── DED-06: Causal Deduction ──────────────────────────────────────

    def causal_deduction(self, cause_id: uuid.UUID,
                          causal_relation_id: uuid.UUID) -> Optional[Conclusion]:
        """
        DED-06: A CAUSES B [strength >= 0.9]. A has occurred => B will occur.
        Falls back to IND-03 if causal_strength < 0.9.
        """
        cause = self._require_active(cause_id, "DED-06")
        if cause.confidence < 0.80:
            return None

        rel = self.graph.get_relation(causal_relation_id)
        if rel is None or not rel.is_strong_causal:
            return None  # caller should use inductive path instead

        # Check no PREVENTS relation blocks the effect
        prevents = self.graph.get_outbound_relations(cause_id, [RelationType.PREVENTS])
        if prevents:
            return None  # causal chain blocked

        effect_id = rel.target_node_id
        effect = self.graph.get_node(effect_id)
        if effect is None:
            return None

        conf_out = causal_propagation(cause.confidence, rel.causal_strength)

        trace = self._new_trace()
        trace.add_premise(cause.entity_id, cause.label, cause.confidence,
                          cause.source_ids)
        trace.add_rule_application(cause.entity_id, "DED-06",
                                   f"[{cause.label}] CAUSES [{effect.label}] "
                                   f"strength={rel.causal_strength:.2f}",
                                   cause.confidence, conf_out)
        trace.add_derivation(effect.entity_id, effect.label, conf_out, conf_out)
        trace.finalise(conf_out)
        trace.reasoning_modes_used.append(ReasoningMode.DEDUCTIVE)

        return Conclusion(
            statement=f"{effect.label} (caused by {cause.label})",
            confidence=conf_out, certainty_level="HIGH",
            reasoning_mode=ReasoningMode.DEDUCTIVE,
            trace=trace,
            supporting_nodes=[cause.entity_id, effect.entity_id],
        )

    # ── Helpers ───────────────────────────────────────────────────────

    def _require_active(self, node_id: uuid.UUID, rule: str) -> KnowledgeNode:
        node = self.graph.require_node(node_id)
        if node.quarantine_flag:
            raise PermissionError(
                f"CI-02: Quarantined node {node_id} cannot be used as premise in {rule}")
        return node

    def _new_trace(self) -> ReasoningTrace:
        return ReasoningTrace(
            conclusion_id=uuid.uuid4(),
            session_id=self.session_id,
        )

    def _commit_conclusion_node(self, label: str, node_type: NodeType,
                                  properties: dict, confidence: float,
                                  source_ids: list[uuid.UUID]) -> KnowledgeNode:
        from datetime import timezone
        node = KnowledgeNode(
            node_type=node_type, label=label, properties=properties,
            valid_from=datetime.now(timezone.utc),
            source_ids=source_ids, decay_rate=0.0,
            confidence=confidence,
        )
        return self.graph.add_node(node)
