"""
AI Reasoning Project — Main Ingestion Pipeline
"""
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.ingestion.parsers.text_parser import NaturalLanguageParser
from ai_reasoning.storage.audit import StrictAuditLogger

class IngestionPipeline:
    """Orchestrates L1 -> L2 processing."""
    def __init__(self, graph: KnowledgeGraph, audit_logger: StrictAuditLogger):
        self.graph = graph
        self.parser = NaturalLanguageParser()
        self.audit = audit_logger

    def ingest_document(self, raw_text: str, source_id: str):
        """Processes an external document and commits it to the graph."""
        nodes = self.parser.parse_to_nodes(raw_text, source_id)
        
        ingested_ids = []
        for node in nodes:
            # DI-04: Source check
            if not node.source_ids:
                raise ValueError(f"DI-04 Violation: Node {node.entity_id} missing source.")
                
            self.graph.add_node(node)
            ingested_ids.append(str(node.entity_id))
            
            # DI-09: Audit Log Mandatory
            self.audit.log_mutation(
                action="NODE_INGEST",
                entity_id=node.entity_id,
                actor="IngestionPipeline",
                context={"source_id": str(source_id)}
            )
            
        return ingested_ids
