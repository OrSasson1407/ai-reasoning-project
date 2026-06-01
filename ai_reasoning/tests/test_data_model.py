"""
AI Reasoning Project — Tests for core data model
Covers: DAD §2, §3, §4, §5, §7 · CCP §2, §5, §6 · RRS §6
"""

import uuid, math
from datetime import datetime, timedelta, timezone
import pytest
from ai_reasoning.core.enums import NodeType, RelationType, EpistemicModel, ConfidenceLevel
from ai_reasoning.core.node import KnowledgeNode, STALENESS_THRESHOLD
from ai_reasoning.core.relation import Relation
from ai_reasoning.core.graph import KnowledgeGraph, CausalPrecedenceError, OrphanRelationError

def _source(): return [uuid.uuid4()]
def _now():    return datetime.now(timezone.utc)

def _make_node(label="Test Node", node_type=NodeType.CLAIM, confidence=0.80,
               valid_from=None, valid_until=None, decay_rate=0.0, **kw):
    return KnowledgeNode(node_type=node_type, label=label, properties={"content": label},
                         valid_from=valid_from or _now(), source_ids=_source(),
                         decay_rate=decay_rate, confidence=confidence,
                         valid_until=valid_until, **kw)

# ── Node validation ────────────────────────────────────────────────────────

class TestNodeValidation:
    def test_creates_valid_node(self):
        n = _make_node("Water boils at 100C"); assert n.label == "Water boils at 100C"
    def test_confidence_too_high(self):
        with pytest.raises(ValueError): _make_node(confidence=1.5)
    def test_confidence_negative(self):
        with pytest.raises(ValueError): _make_node(confidence=-0.1)
    def test_valid_from_after_valid_until(self):
        now = _now()
        with pytest.raises(ValueError): _make_node(valid_from=now+timedelta(days=1), valid_until=now)
    def test_no_source_raises(self):
        with pytest.raises(ValueError):
            KnowledgeNode(node_type=NodeType.CLAIM, label="x", properties={},
                          valid_from=_now(), source_ids=[], decay_rate=0.0)
    def test_hypothesis_no_certainty_one(self):
        with pytest.raises(ValueError): _make_node(node_type=NodeType.HYPOTHESIS, confidence=1.0)
    def test_math_object_no_decay(self):
        with pytest.raises(ValueError): _make_node(node_type=NodeType.MATHEMATICAL_OBJECT, decay_rate=0.01)
    def test_unique_ids(self):
        assert _make_node().entity_id != _make_node().entity_id

# ── Confidence helpers ─────────────────────────────────────────────────────

class TestConfidenceHelpers:
    def test_verified(self):    assert _make_node(confidence=0.95).confidence_level == ConfidenceLevel.VERIFIED
    def test_high(self):        assert _make_node(confidence=0.75).confidence_level == ConfidenceLevel.HIGH
    def test_moderate(self):    assert _make_node(confidence=0.55).confidence_level == ConfidenceLevel.MODERATE
    def test_low(self):         assert _make_node(confidence=0.35).confidence_level == ConfidenceLevel.LOW
    def test_very_low(self):    assert _make_node(confidence=0.10).confidence_level == ConfidenceLevel.VERY_LOW
    def test_contradicted(self):assert _make_node(confidence=0.02).confidence_level == ConfidenceLevel.CONTRADICTED
    def test_stale_by_expiry(self):
        past = _now() - timedelta(hours=1)
        assert _make_node(valid_from=_now()-timedelta(hours=2), valid_until=past).is_stale
    def test_stale_by_low_conf(self):   assert _make_node(confidence=0.25).is_stale
    def test_active_node(self):         assert _make_node(confidence=0.80).is_active
    def test_quarantined_not_active(self):
        n = _make_node(confidence=0.80); n.quarantine(); assert not n.is_active

# ── Decay ──────────────────────────────────────────────────────────────────

class TestDecay:
    def test_permanent_no_decay(self):
        n = _make_node(confidence=0.90, decay_rate=0.0)
        orig = n.confidence; n.apply_decay(86400); assert n.confidence == orig
    def test_volatile_decays(self):
        n = _make_node(confidence=0.90, decay_rate=0.0001)
        n.apply_decay(100)
        assert abs(n.confidence - 0.90 * math.exp(-0.0001 * 100)) < 1e-9
    def test_floor_enforced(self):
        n = _make_node(confidence=0.90, decay_rate=1.0)
        n.apply_decay(100_000); assert n.confidence >= 0.05
    def test_contradicted_reaches_zero(self):
        n = _make_node(confidence=0.90, decay_rate=1.0)
        n.flag_contradiction(); n.apply_decay(100_000); assert n.confidence == 0.0

# ── Bayesian update ────────────────────────────────────────────────────────

class TestBayesianUpdate:
    def test_increases(self):
        n = _make_node(confidence=0.60); n.bayesian_update(0.9, 0.5); assert n.confidence > 0.60
    def test_decreases(self):
        n = _make_node(confidence=0.70); n.bayesian_update(0.1, 0.5); assert n.confidence < 0.70
    def test_zero_prior_raises(self):
        with pytest.raises(ValueError): _make_node().bayesian_update(0.8, 0.0)
    def test_caps_at_one(self):
        n = _make_node(confidence=0.90); n.bayesian_update(1.0, 0.1); assert n.confidence <= 1.0

# ── Relation validation ────────────────────────────────────────────────────

class TestRelationValidation:
    def test_valid_relation(self):
        r = Relation(RelationType.SUPPORTS, uuid.uuid4(), uuid.uuid4(),
                     0.80, _now(), _source()); assert r.confidence == 0.80
    def test_no_self_contradiction(self):
        nid = uuid.uuid4()
        with pytest.raises(ValueError): Relation(RelationType.CONTRADICTS, nid, nid, 0.9, _now(), _source())
    def test_confidence_out_of_range(self):
        with pytest.raises(ValueError): Relation(RelationType.IS_A, uuid.uuid4(), uuid.uuid4(), 2.0, _now(), _source())
    def test_strong_causal(self):
        r = Relation(RelationType.CAUSES, uuid.uuid4(), uuid.uuid4(), 0.9, _now(), _source(), causal_strength=0.95)
        assert r.is_strong_causal and not r.is_weak_causal
    def test_weak_causal(self):
        r = Relation(RelationType.CAUSES, uuid.uuid4(), uuid.uuid4(), 0.7, _now(), _source(), causal_strength=0.65)
        assert r.is_weak_causal and not r.is_strong_causal

# ── KnowledgeGraph ─────────────────────────────────────────────────────────

class TestKnowledgeGraph:
    def _two_nodes(self):
        g = KnowledgeGraph()
        n1, n2 = _make_node("A", confidence=0.85), _make_node("B", confidence=0.75)
        g.add_node(n1); g.add_node(n2); return g, n1, n2

    def test_add_retrieve(self):
        g = KnowledgeGraph(); n = _make_node(); g.add_node(n); assert g.get_node(n.entity_id) == n
    def test_duplicate_raises(self):
        g = KnowledgeGraph(); n = _make_node(); g.add_node(n)
        with pytest.raises(ValueError): g.add_node(n)
    def test_add_relation(self):
        g, n1, n2 = self._two_nodes()
        g.add_relation(Relation(RelationType.SUPPORTS, n1.entity_id, n2.entity_id, 0.80, _now(), _source()))
        assert len(g.get_outbound_relations(n1.entity_id, [RelationType.SUPPORTS])) == 1
    def test_orphan_relation_raises(self):
        g = KnowledgeGraph()
        with pytest.raises(OrphanRelationError):
            g.add_relation(Relation(RelationType.IS_A, uuid.uuid4(), uuid.uuid4(), 0.8, _now(), _source()))
    def test_causal_precedence(self):
        g = KnowledgeGraph(); now = _now()
        cause  = _make_node("Cause",  valid_from=now)
        effect = _make_node("Effect", valid_from=now - timedelta(seconds=1))
        g.add_node(cause); g.add_node(effect)
        with pytest.raises(CausalPrecedenceError):
            g.add_relation(Relation(RelationType.CAUSES, cause.entity_id, effect.entity_id,
                                    0.9, now, _source(), causal_strength=0.95))
    def test_query_confidence_range(self):
        g = KnowledgeGraph()
        for c in [0.20, 0.50, 0.80, 0.95]: g.add_node(_make_node(f"n{c}", confidence=c))
        assert all(0.50 <= n.confidence <= 0.85 for n in g.query_nodes(min_confidence=0.50, max_confidence=0.85))
    def test_query_excludes_quarantined(self):
        g = KnowledgeGraph(); n = _make_node(confidence=0.80); g.add_node(n); n.quarantine()
        assert n not in g.query_nodes()
    def test_temporal_snapshot(self):
        g = KnowledgeGraph(); past = _now() - timedelta(hours=2)
        old = _make_node("Old", valid_from=past-timedelta(hours=1), valid_until=past+timedelta(minutes=30))
        new = _make_node("New")
        g.add_node(old); g.add_node(new)
        ids = [n.entity_id for n in g.query_nodes(valid_at=past, include_stale=True)]
        assert old.entity_id in ids and new.entity_id not in ids

# ── Causal traversal ───────────────────────────────────────────────────────

class TestCausalTraversal:
    def _chain(self):
        g = KnowledgeGraph(); t0 = _now()
        a = _make_node("A", valid_from=t0)
        b = _make_node("B", valid_from=t0+timedelta(seconds=1))
        c = _make_node("C", valid_from=t0+timedelta(seconds=2))
        for n in [a, b, c]: g.add_node(n)
        for src, tgt in [(a, b), (b, c)]:
            g.add_relation(Relation(RelationType.CAUSES, src.entity_id, tgt.entity_id,
                                    0.9, t0, _source(), causal_strength=0.95))
        return g, a, b, c

    def test_forward_finds_end(self):
        g, a, b, c = self._chain()
        paths = g.causal_forward(a.entity_id)
        assert any(c.entity_id in p for p in paths)

    def test_backward_finds_root(self):
        g, a, b, c = self._chain()
        paths = g.causal_backward(c.entity_id)
        assert any(a.entity_id in p for p in paths)

    def test_loop_detected(self):
        g = KnowledgeGraph(); t0 = _now()
        a = _make_node("A", valid_from=t0)
        b = _make_node("B", valid_from=t0+timedelta(seconds=1))
        g.add_node(a); g.add_node(b)
        g.add_relation(Relation(RelationType.CAUSES, a.entity_id, b.entity_id,
                                0.85, t0, _source(), causal_strength=0.90))
        loop_rel = Relation(RelationType.CAUSES, b.entity_id, a.entity_id,
                            0.85, t0+timedelta(seconds=2), _source(), causal_strength=0.90)
        g._relations[loop_rel.relation_id] = loop_rel
        g._outbound[b.entity_id].append(loop_rel.relation_id)
        g._inbound[a.entity_id].append(loop_rel.relation_id)
        paths = g.causal_forward(a.entity_id)
        assert any("__CAUSAL_LOOP__" in p for p in paths)

# ── Contradiction & quarantine ─────────────────────────────────────────────

class TestContradictionAndQuarantine:
    def test_flag_sets_both_nodes(self):
        g = KnowledgeGraph()
        n1 = _make_node("Round", confidence=0.95)
        n2 = _make_node("Flat",  confidence=0.80)
        g.add_node(n1); g.add_node(n2)
        g.flag_contradiction(n1.entity_id, n2.entity_id)
        assert g.get_node(n1.entity_id).contradiction_flag
        assert g.get_node(n2.entity_id).contradiction_flag
        assert len(g.get_active_contradictions()) == 1

    def test_quarantine_propagates(self):
        g = KnowledgeGraph(); t0 = _now()
        root    = _make_node("Root",    confidence=0.90, valid_from=t0)
        derived = _make_node("Derived", confidence=0.75, valid_from=t0+timedelta(seconds=1))
        g.add_node(root); g.add_node(derived)
        g.add_relation(Relation(RelationType.DERIVED_FROM, derived.entity_id, root.entity_id,
                                0.75, t0, _source()))
        quarantined = g.quarantine_node(root.entity_id)
        assert root.entity_id in quarantined
        assert derived.entity_id in quarantined

    def test_staleness_scan(self):
        g = KnowledgeGraph(); now = _now()
        stale = _make_node("Expired", valid_from=now-timedelta(hours=2), valid_until=now-timedelta(hours=1))
        fresh = _make_node("Current", confidence=0.80)
        g.add_node(stale); g.add_node(fresh)
        scan = g.staleness_scan()
        assert stale in scan and fresh not in scan

    def test_stats(self):
        g = KnowledgeGraph()
        n1, n2 = _make_node(confidence=0.80), _make_node(confidence=0.75)
        g.add_node(n1); g.add_node(n2)
        g.flag_contradiction(n1.entity_id, n2.entity_id)
        g.quarantine_node(n1.entity_id)
        s = g.stats()
        assert s["total_nodes"] == 2 and s["active_contradictions"] == 1
