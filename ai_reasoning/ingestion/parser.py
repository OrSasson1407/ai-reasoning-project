from ai_reasoning.core.node import Node
from ai_reasoning.core.enums import NodeType

class InputParser:
    """
    Prevents CV-003: UNPARSED_INPUT.
    Ensures free text from L1 is structured before hitting L2 inference.
    """
    def parse_to_node(self, raw_text: str, source_id: str) -> Node:
        if not raw_text.strip():
            raise ValueError("Empty input cannot be parsed.")
            
        # Stub logic for NLP parsing into structured representation
        return Node(
            node_type=NodeType.FACT,
            content={"parsed_statement": raw_text},
            confidence=0.5, # Default starting confidence
            source_ids=[source_id]
        )
