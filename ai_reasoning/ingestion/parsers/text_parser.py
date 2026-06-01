"""
AI Reasoning Project — Text Parser (Layer 1 to Layer 2 Transition)
Sourced from: SRD Phase 1 & AIC (Prevents CV-003)
"""
import uuid
from datetime import datetime, timezone
from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType
from ai_reasoning.ingestion.sanitization.pii_scrubber import PIIScrubber

class NaturalLanguageParser:
    """
    Simulates NLP parsing. Raw L1 text MUST be converted into structured L2 nodes.
    Failure to do this triggers CV-003.
    """
    def __init__(self, confidence_baseline: float = 0.50):
        self.confidence_baseline = confidence_baseline

    def parse_to_nodes(self, raw_text: str, source_id: str) -> list[KnowledgeNode]:
        """Parses a block of text into discrete claim nodes."""
        if not raw_text or not raw_text.strip():
            raise ValueError("Cannot parse empty text block.")

        safe_text = PIIScrubber.scrub(raw_text)
        
        # In a real implementation, SpaCy or an LLM extracts discrete entities/claims here.
        # We simulate extracting one claim from the sanitized text.
        parsed_claim = f"Extracted assertion from: {safe_text[:30]}..."
        
        node = KnowledgeNode(
            node_type=NodeType.CLAIM,
            label=parsed_claim,
            properties={"original_text_snippet": safe_text[:100]},
            source_ids=[uuid.UUID(source_id) if isinstance(source_id, str) else source_id],
            valid_from=datetime.now(timezone.utc),
            confidence=self.confidence_baseline
        )
        return [node]
