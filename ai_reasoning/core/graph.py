"""
AI Reasoning Project — KnowledgeGraph
Sourced from: DAD v1.0 §3, §4, §6 · CCP v1.0 §2, §5 · SRD §2.1
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from .enums import RelationType, NodeType
from .node import KnowledgeNode, STALENESS_THRESHOLD
from .relation import Relation


class QuarantineBypassError(Exception):
    """Quarantined node used as inference premise (CI-02)."""

class CausalPrecedenceError(Exception):
    """CAUSES relation where effect precedes cause (DI-05 / CI-04)."""

class OrphanRelationError(Exception):
    """Relation references a non-existent node (DI-01)."""


class KnowledgeGraph:
    """
    In-memory Knowledge Graph.
    Enforces DAD §7 data-integrity invariants and CCP §6 consistency invariants.
    """

    def __init__(self) -> None:
        self._nodes:     dict[uuid.UUID, KnowledgeNode] = {}
        self._relations: dict[uuid.UUID, Relation]      = {}
        self._outbound:  dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
        self._inbound:   dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)

    # ── Nodes ──────────────────────────────────────────────────────────

    def add_node(self, node: KnowledgeNode) -> KnowledgeNode:
        if node.entity_id in self._nodes:
            raise ValueError(f"Node {node.entity_id} already exists (DI-08).")
        self._nodes[node.entity_id] = node
        return node

    def get_node(self, node_id: uuid.UUID) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    def require_node(self, node_id: uuid.UUID) -> KnowledgeNode:
        node = self._nodes.get(node_id)
        if node is None:
            raise KeyError(f"Node {node_id} not found")
        return node

    def update_node_confidence(self, node_id: uuid.UUID, new_confidence: float) -> KnowledgeNode:
        node = self.require_node(node_id)
        if not (0.0 <= new_confidence <= 1.0):
            raise ValueError(f"confidence must be [0.0, 1.0], got {new_confidence}")
        node.confidence = new_confidence
        node.last_updated = datetime.now(timezone.utc)
        return node

    def remove_node(self, node_id: uuid.UUID) -> None:
        if node_id not in self._nodes:
            raise KeyError(f"Node {node_id} not found")
        for rid in (self._outbound.get(node_id, []) + self._inbound.get(node_id, [])):
            self._relations.pop(rid, None)
        self._outbound.pop(node_id, None)
        self._inbound.pop(node_id, None)
        del self._nodes[node_id]

    # ── Relations ──────────────────────────────────────────────────────

    def add_relation(self, relation: Relation) -> Relation:
        if relation.source_node_id not in self._nodes:
            raise OrphanRelationError(f"Source node {relation.source_node_id} does not exist (DI-01)")
        if relation.target_node_id not in self._nodes:
            raise OrphanRelationError(f"Target node {relation.target_node_id} does not exist (DI-01)")
        if relation.relation_type == RelationType.CAUSES:
            self._check_causal_precedence(relation)
        self._relations[relation.relation_id] = relation
        self._outbound[relation.source_node_id].append(relation.relation_id)
        self._inbound[relation.target_node_id].append(relation.relation_id)
        return relation

    def _check_causal_precedence(self, relation: Relation) -> None:
        src = self._nodes[relation.source_node_id]
        tgt = self._nodes[relation.target_node_id]
        if src.valid_from >= tgt.valid_from:
            raise CausalPrecedenceError(
                f"CAUSES violates temporal precedence: "
                f"cause '{src.label}' valid_from={src.valid_from} >= "
                f"effect '{tgt.label}' valid_from={tgt.valid_from} (DI-05)")

    def get_relation(self, relation_id: uuid.UUID) -> Optional[Relation]:
        return self._relations.get(relation_id)

    def get_outbound_relations(self, node_id: uuid.UUID,
                               relation_types: Optional[list[RelationType]] = None) -> list[Relation]:
        rels = [self._relations[rid] for rid in self._outbound.get(node_id, [])
                if rid in self._relations]
        if relation_types:
            rels = [r for r in rels if r.relation_type in relation_types]
        return rels

    def get_inbound_relations(self, node_id: uuid.UUID,
                              relation_types: Optional[list[RelationType]] = None) -> list[Relation]:
        rels = [self._relations[rid] for rid in self._inbound.get(node_id, [])
                if rid in self._relations]
        if relation_types:
            rels = [r for r in rels if r.relation_type in relation_types]
        return rels

    # ── Query ──────────────────────────────────────────────────────────

    def query_nodes(self, *, node_types=None, min_confidence=0.0, max_confidence=1.0,
                    valid_at=None, include_stale=False, include_quarantined=False,
                    meta_tags=None) -> list[KnowledgeNode]:
        results = []
        for node in self._nodes.values():
            if node_types and node.node_type not in node_types: continue
            if not (min_confidence <= node.confidence <= max_confidence): continue
            if not include_stale and node.is_stale: continue
            if not include_quarantined and node.quarantine_flag: continue
            if valid_at is not None:
                if node.valid_from > valid_at: continue
                if node.valid_until is not None and node.valid_until < valid_at: continue
            if meta_tags and not any(t in node.meta_tags for t in meta_tags): continue
            results.append(node)
        return results

    # ── Causal traversal ───────────────────────────────────────────────

    def causal_forward(self, start_node_id: uuid.UUID, max_depth: int = 7,
                       time_horizon=None) -> list[list[uuid.UUID]]:
        paths: list[list[uuid.UUID]] = []
        self._dfs_causal(start_node_id, [start_node_id], set(), paths, "forward", max_depth)
        return paths

    def causal_backward(self, effect_node_id: uuid.UUID, max_depth: int = 7) -> list[list[uuid.UUID]]:
        paths: list[list[uuid.UUID]] = []
        self._dfs_causal(effect_node_id, [effect_node_id], set(), paths, "backward", max_depth)
        return paths

    def _dfs_causal(self, node_id, path, visited, paths, direction, max_depth) -> None:
        if len(path) > max_depth:
            paths.append(list(path))
            return
        rels = (self.get_outbound_relations(node_id, [RelationType.CAUSES])
                if direction == "forward"
                else self.get_inbound_relations(node_id, [RelationType.CAUSES]))
        leaf = True
        for rel in rels:
            next_id = rel.target_node_id if direction == "forward" else rel.source_node_id
            if next_id in visited:
                paths.append(list(path) + [next_id, "__CAUSAL_LOOP__"])
                continue
            leaf = False
            visited.add(next_id)
            self._dfs_causal(next_id, path + [next_id], visited, paths, direction, max_depth)
            visited.discard(next_id)
        if leaf:
            paths.append(list(path))

    # ── Contradiction & quarantine ─────────────────────────────────────

    def flag_contradiction(self, node_a_id: uuid.UUID, node_b_id: uuid.UUID) -> Relation:
        self.require_node(node_a_id).flag_contradiction()
        self.require_node(node_b_id).flag_contradiction()
        rel = Relation(
            relation_type=RelationType.CONTRADICTS,
            source_node_id=node_a_id,
            target_node_id=node_b_id,
            confidence=1.0,
            valid_from=datetime.now(timezone.utc),
            source_ids=[uuid.uuid4()],
        )
        self._relations[rel.relation_id] = rel
        self._outbound[node_a_id].append(rel.relation_id)
        self._inbound[node_b_id].append(rel.relation_id)
        return rel

    def quarantine_node(self, node_id: uuid.UUID) -> list[uuid.UUID]:
        quarantined: list[uuid.UUID] = []
        queue = [node_id]
        while queue:
            nid = queue.pop()
            node = self._nodes.get(nid)
            if node and not node.quarantine_flag:
                node.quarantine()
                quarantined.append(nid)
                for rel in self.get_inbound_relations(nid, [RelationType.DERIVED_FROM]):
                    queue.append(rel.source_node_id)
        return quarantined

    def get_active_contradictions(self) -> list[tuple[uuid.UUID, uuid.UUID]]:
        return [(r.source_node_id, r.target_node_id)
                for r in self._relations.values()
                if r.relation_type == RelationType.CONTRADICTS]

    def provenance_trace(self, node_id: uuid.UUID) -> list[uuid.UUID]:
        chain, visited, queue = [node_id], {node_id}, [node_id]
        while queue:
            nid = queue.pop()
            for rel in self.get_outbound_relations(nid, [RelationType.DERIVED_FROM]):
                tid = rel.target_node_id
                if tid not in visited:
                    visited.add(tid); chain.append(tid); queue.append(tid)
        return chain

    def staleness_scan(self) -> list[KnowledgeNode]:
        return [n for n in self._nodes.values() if n.is_stale]

    def stats(self) -> dict:
        nodes = list(self._nodes.values())
        return {
            "total_nodes":           len(nodes),
            "total_relations":       len(self._relations),
            "quarantined_nodes":     sum(1 for n in nodes if n.quarantine_flag),
            "contradicted_nodes":    sum(1 for n in nodes if n.contradiction_flag),
            "stale_nodes":           sum(1 for n in nodes if n.is_stale),
            "active_contradictions": len(self.get_active_contradictions()),
        }

    def __repr__(self) -> str:
        s = self.stats()
        return (f"KnowledgeGraph(nodes={s['total_nodes']}, "
                f"relations={s['total_relations']}, "
                f"quarantined={s['quarantined_nodes']}, "
                f"contradictions={s['active_contradictions']})")
