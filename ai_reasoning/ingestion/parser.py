from ai_reasoning.core.node import KnowledgeNode
from ai_reasoning.core.enums import NodeType
from datetime import datetime, timezone
import uuid

class DataIngestionParser:
    def __init__(self, default_confidence: float = 0.8):
        self.default_confidence = default_confidence

    def parse_raw_text(self, text: str, source_id: str) -> list[KnowledgeNode]:
        """
        A placeholder for an LLM-based extraction pipeline.
        In production, you would pass 'text' to Gemini/OpenAI to extract facts.
        """
        nodes = []
        # Simulate simple sentence splitting as fact extraction
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for sentence in sentences:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                label=sentence[:50] + ("..." if len(sentence) > 50 else ""),
                content=sentence,
                confidence=self.default_confidence,
                source_ids=[uuid.uuid5(uuid.NAMESPACE_DNS, source_id)],
                valid_from=datetime.now(timezone.utc)
            )
            nodes.append(node)
            
        return nodes
