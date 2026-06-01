from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.enums import RelationType

class ContradictionDetector:
    def __init__(self, graph: KnowledgeGraph): self.graph = graph
    def scan_for_contradictions(self):
        found = 0
        for rel in self.graph.relations:
            if rel.relation_type == RelationType.CONTRADICTS:
                src = self.graph.get_node(rel.source_node_id)
                tgt = self.graph.get_node(rel.target_node_id)
                if not src or not tgt or src.quarantined or tgt.quarantined: continue
                if src.confidence > tgt.confidence: self.graph.quarantine_cascade(tgt.entity_id); found += 1
                elif tgt.confidence > src.confidence: self.graph.quarantine_cascade(src.entity_id); found += 1
                else: self.graph.quarantine_cascade(src.entity_id); self.graph.quarantine_cascade(tgt.entity_id); found += 2
        return found
