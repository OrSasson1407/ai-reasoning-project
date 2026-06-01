"""
AI Reasoning Project — Contradiction Detector
Sourced from: CCP v1.0 §2, §3
"""

import uuid
from datetime import datetime, timezone
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.enums import RelationType

class ContradictionDetector:
    """
    Scans the KnowledgeGraph for contradictions and enforces automatic quarantines.
    Implements CI-01 (Detection) and CI-05 (Derivation Integrity / Quarantine Cascade).
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def scan_for_contradictions(self) -> list[dict]:
        """
        Scans all nodes to find active CONTRADICTS relations and ensures all 
        involved nodes (and their derivations) are strictly quarantined.
        """
        active_contradictions = self.graph.get_active_contradictions()
        enforcement_log = []

        for source_id, target_id in active_contradictions:
            source_node = self.graph.get_node(source_id)
            target_node = self.graph.get_node(target_id)

            if source_node and not source_node.quarantine_flag:
                cascaded = self.graph.quarantine_node(source_id)
                enforcement_log.append({
                    "event": "QUARANTINE_ENFORCED",
                    "trigger_node": source_id,
                    "cascaded_to": cascaded,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            if target_node and not target_node.quarantine_flag:
                cascaded = self.graph.quarantine_node(target_id)
                enforcement_log.append({
                    "event": "QUARANTINE_ENFORCED",
                    "trigger_node": target_id,
                    "cascaded_to": cascaded,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

        return enforcement_log
