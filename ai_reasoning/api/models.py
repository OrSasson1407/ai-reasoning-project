from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from ai_reasoning.core.enums import ReasoningMode, NodeType

class NodeCreateRequest(BaseModel):
    node_type: NodeType; label: str; confidence: float = Field(..., ge=0.0, le=1.0)
    properties: Dict[str, Any] = {}; content: str = ""

class NodeResponse(BaseModel):
    entity_id: uuid.UUID; node_type: NodeType; label: str
    confidence: float; quarantine_flag: bool; is_stale: bool

class InferenceRequest(BaseModel):
    premise_ids: List[uuid.UUID]; mode: ReasoningMode; conclusion_label: str; conclusion_type: NodeType

class InferenceResponse(BaseModel):
    status: str; conclusion_node_id: Optional[uuid.UUID] = None; error: Optional[str] = None
