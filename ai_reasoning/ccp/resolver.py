"""
AI Reasoning Project — Contradiction Resolver
Sourced from: CCP v1.0 §4, §5
"""

import uuid
from datetime import datetime, timezone
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.enums import RelationType, ResolutionStatus

class SilentResolutionError(Exception):
    """Raised if an attempt is made to clear a contradiction without an audit log (CI-03)."""

class ContradictionResolver:
    """
    Handles explicit resolution of contradictions. 
    Enforces CI-03 (No Silent Resolution) and CI-07 (Audit Completeness).
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
        self._audit_log = []

    def resolve_contradiction(self, relation_id: uuid.UUID, 
                              resolution_strategy: str, 
                              human_override: bool = False,
                              drop_node_id: uuid.UUID = None) -> dict:
        """
        Resolves a contradiction relation by invalidating/dropping one of the nodes,
        clearing the contradiction flags, and logging the resolution.
        """
        relation = self.graph.get_relation(relation_id)
        if not relation or relation.relation_type != RelationType.CONTRADICTS:
            raise ValueError(f"Relation {relation_id} is not an active CONTRADICTS relation.")

        if not human_override and resolution_strategy == "AUTO":
             # CI-08: Level 1 HALT contradictions require explicit oversight.
             raise ValueError("CI-08 Violation: HALT contradictions require human_override=True.")

        # 1. Generate Audit Entry (CI-07)
        audit_id = uuid.uuid4()
        audit_entry = {
            "audit_id": str(audit_id),
            "relation_id": str(relation_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strategy": resolution_strategy,
            "human_override": human_override,
            "dropped_node": str(drop_node_id) if drop_node_id else None,
            "status": ResolutionStatus.RESOLVED.value
        }

        # 2. State Mutation
        node_a = self.graph.require_node(relation.source_node_id)
        node_b = self.graph.require_node(relation.target_node_id)

        node_a.clear_contradiction()
        node_b.clear_contradiction()

        # If a node was explicitly determined false, drop its confidence to 0 (UP-10 logic)
        if drop_node_id:
            dropped = self.graph.require_node(drop_node_id)
            self.graph.update_node_confidence(drop_node_id, 0.0)
            
            # Release quarantine on the surviving node
            survivor_id = node_b.entity_id if drop_node_id == node_a.entity_id else node_a.entity_id
            self.graph.require_node(survivor_id).release_quarantine()

        # Invalidate the contradiction relation
        relation.valid_until = datetime.now(timezone.utc)

        # 3. Commit Audit
        self._audit_log.append(audit_entry)
        return audit_entry

    def get_resolution_audit_log(self) -> list[dict]:
        return self._audit_log
