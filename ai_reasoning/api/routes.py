"""
FastAPI route handlers — AIC v1.0 §2
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from ..core.enums       import NodeType, RelationType, SourceType
from ..core.node        import KnowledgeNode
from ..core.relation    import Relation
from ..core.graph       import KnowledgeGraph, CausalPrecedenceError, OrphanRelationError
from ..core.inference_engine   import InferenceEngine, Conclusion
from ..core.contradiction_engine import ContradictionEngine
from .models import (
    IngestRequest, IngestResponse, IngestResult,
    InferRequest, InferResponse, ConclusionOut,
    NodeQueryRequest, NodeOut,
    ContradictionCheckRequest, ResolveRequest,
    TraceOut, TraceStepOut,
)

router = APIRouter()

# ── Shared state (in-memory; replaced by DB in production) ───────────────
_graph  = KnowledgeGraph()
_contra = ContradictionEngine(_graph)
_traces: dict[str, dict] = {}   # trace_id -> trace dict


# ── Health ────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {"status": "ok", "graph_stats": _graph.stats()}


# ── Ingest ────────────────────────────────────────────────────────────────

@router.post("/knowledge/ingest", response_model=IngestResponse, status_code=201)
def ingest(req: IngestRequest):
    results: list[IngestResult] = []
    contradictions: list[dict]  = []

    for fact in req.facts:
        try:
            vf = fact.valid_from or datetime.now(timezone.utc)
            src_id = uuid.uuid4()
            node = KnowledgeNode(
                node_type=NodeType(fact.node_type),
                label=fact.label,
                properties=fact.properties,
                valid_from=vf,
                valid_until=fact.valid_until,
                source_ids=[src_id],
                decay_rate=0.0,
                confidence=fact.source.reliability_score,
            )
            _graph.add_node(node)

            # Add any relations declared inline
            for rel_in in fact.relations:
                try:
                    rel = Relation(
                        relation_type=RelationType(rel_in.relation_type),
                        source_node_id=node.entity_id,
                        target_node_id=rel_in.target_node_id,
                        confidence=rel_in.confidence,
                        valid_from=vf,
                        source_ids=[src_id],
                        causal_strength=rel_in.causal_strength,
                    )
                    _graph.add_relation(rel)
                except (OrphanRelationError, CausalPrecedenceError, ValueError) as e:
                    # Non-fatal — log but continue
                    pass

            results.append(IngestResult(node_id=str(node.entity_id), status="COMMITTED"))

        except Exception as e:
            results.append(IngestResult(node_id="error", status=f"ERROR: {e}"))

    return IngestResponse(ingested=results, contradictions_detected=contradictions)


# ── Query nodes ───────────────────────────────────────────────────────────

@router.post("/knowledge/query", response_model=list[NodeOut])
def query_nodes(req: NodeQueryRequest):
    node_types = [NodeType(t) for t in req.node_types] if req.node_types else None
    nodes = _graph.query_nodes(
        node_types=node_types,
        min_confidence=req.min_confidence,
        max_confidence=req.max_confidence,
        include_stale=req.include_stale,
        include_quarantined=req.include_quarantined,
        valid_at=req.valid_at,
    )
    return [
        NodeOut(
            entity_id=str(n.entity_id), node_type=n.node_type.value,
            label=n.label, confidence=n.confidence,
            confidence_level=n.confidence_level.value,
            is_stale=n.is_stale, quarantine_flag=n.quarantine_flag,
            contradiction_flag=n.contradiction_flag,
            valid_from=n.valid_from.isoformat(),
            valid_until=n.valid_until.isoformat() if n.valid_until else None,
            meta_tags=n.meta_tags,
        )
        for n in nodes
    ]


# ── Get node by ID ────────────────────────────────────────────────────────

@router.get("/knowledge/node/{node_id}", response_model=NodeOut)
def get_node(node_id: str):
    node = _graph.get_node(uuid.UUID(node_id))
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeOut(
        entity_id=str(node.entity_id), node_type=node.node_type.value,
        label=node.label, confidence=node.confidence,
        confidence_level=node.confidence_level.value,
        is_stale=node.is_stale, quarantine_flag=node.quarantine_flag,
        contradiction_flag=node.contradiction_flag,
        valid_from=node.valid_from.isoformat(),
        valid_until=node.valid_until.isoformat() if node.valid_until else None,
        meta_tags=node.meta_tags,
    )


# ── Infer ─────────────────────────────────────────────────────────────────

@router.post("/infer", response_model=InferResponse)
def infer(req: InferRequest):
    engine = InferenceEngine(_graph)
    conclusions: list[ConclusionOut] = []
    gaps: list[str] = []
    signals: list[str] = []

    context_nodes = []
    for nid_str in req.context_node_ids:
        try:
            node = _graph.get_node(uuid.UUID(nid_str))
            if node and node.is_active:
                context_nodes.append(node)
            elif node and node.quarantine_flag:
                return InferResponse(
                    status="halted",
                    halt_reason="ACTIVE_CONTRADICTION",
                    contradiction={"detail": f"Node {nid_str} is quarantined"},
                )
            else:
                gaps.append(f"Node {nid_str} not found or stale")
        except ValueError:
            gaps.append(f"Invalid node ID: {nid_str}")

    if not context_nodes:
        return InferResponse(
            status="insufficient_evidence",
            knowledge_gaps=[req.query] if not gaps else gaps,
        )

    # Run DED-04 (Universal Instantiation) for each context node as demo
    for node in context_nodes:
        try:
            src_ids = [uuid.uuid4()]
            conclusion = engine.universal_instantiation(
                universal_rule_conf=0.90,
                instance_id=node.entity_id,
                property_label=f"Inferred property from: {req.query}",
                property_node_type=NodeType.CLAIM,
                property_properties={"query": req.query},
                property_source_ids=src_ids,
            )
            if conclusion and conclusion.confidence >= req.min_confidence:
                if conclusion.trace:
                    trace_dict = conclusion.trace.to_dict()
                    _traces[trace_dict["trace_id"]] = trace_dict
                conclusions.append(ConclusionOut(
                    conclusion_id=str(conclusion.conclusion_id),
                    statement=conclusion.statement,
                    confidence=conclusion.confidence,
                    certainty_level=conclusion.certainty_level,
                    reasoning_mode=conclusion.reasoning_mode.value,
                    trace_id=str(conclusion.trace.trace_id) if conclusion.trace else None,
                    supporting_nodes=[str(n) for n in conclusion.supporting_nodes],
                    meta_signals=conclusion.meta_signals,
                ))
        except PermissionError as e:
            return InferResponse(status="halted", halt_reason=str(e))

    if not conclusions:
        return InferResponse(status="insufficient_evidence", knowledge_gaps=gaps or [req.query])

    return InferResponse(status="success", conclusions=conclusions,
                         knowledge_gaps=gaps, meta_signals=signals)


# ── Contradiction ─────────────────────────────────────────────────────────

@router.post("/contradiction/check")
def check_contradiction(req: ContradictionCheckRequest):
    try:
        a_id = uuid.UUID(req.node_a_id)
        b_id = uuid.UUID(req.node_b_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    report = None
    if req.contradiction_type == "HARD":
        report = _contra.check_hard_contradiction(a_id, b_id)
    elif req.contradiction_type == "SOFT":
        report = _contra.check_soft_contradiction(a_id, b_id)
    elif req.contradiction_type == "TEMPORAL":
        report = _contra.check_temporal_inconsistency(a_id, b_id)

    if not report:
        return {"status": "no_contradiction_detected"}
    return report.to_dict()


@router.get("/contradiction/open")
def list_open_contradictions():
    return [r.to_dict() for r in _contra.open_reports()]


@router.post("/contradiction/resolve")
def resolve_contradiction(req: ResolveRequest):
    ok = _contra.resolve(uuid.UUID(req.contradiction_id))
    if not ok:
        raise HTTPException(status_code=404, detail="Contradiction not found")
    return {"status": "resolved", "contradiction_id": req.contradiction_id}


# ── Trace ─────────────────────────────────────────────────────────────────

@router.get("/trace/{trace_id}", response_model=TraceOut)
def get_trace(trace_id: str):
    trace = _traces.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return TraceOut(
        trace_id=trace["trace_id"],
        conclusion_id=trace["conclusion_id"],
        final_confidence=trace["final_confidence"],
        chain_depth=trace["chain_depth"],
        reasoning_modes_used=trace["reasoning_modes_used"],
        meta_signals=trace["meta_signals"],
        steps=[
            TraceStepOut(
                step_number=s["step_number"], type=s["type"],
                node_id=s["node_id"], statement=s["statement"],
                confidence_in=s["confidence_in"], confidence_out=s["confidence_out"],
                rule_id=s.get("rule_id"),
            )
            for s in trace["steps"]
        ],
    )


# ── Graph stats ───────────────────────────────────────────────────────────

@router.get("/graph/stats")
def graph_stats():
    return _graph.stats()


@router.get("/graph/staleness")
def staleness_scan():
    stale = _graph.staleness_scan()
    return [{"entity_id": str(n.entity_id), "label": n.label,
             "confidence": n.confidence} for n in stale]
