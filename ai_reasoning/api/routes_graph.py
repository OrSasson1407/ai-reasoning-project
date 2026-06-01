from fastapi import APIRouter, Depends, HTTPException
from ai_reasoning.api.models import NodeCreateRequest, NodeResponse
from ai_reasoning.api.dependencies import get_graph
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.node import Node
import uuid

router = APIRouter(prefix='/graph', tags=['Knowledge Graph'])

@router.post('/nodes', response_model=NodeResponse)
def add_node(request: NodeCreateRequest, graph: KnowledgeGraph = Depends(get_graph)):
    node = Node(
        node_type=request.node_type,
        label=request.label,
        confidence=request.confidence,
        properties=request.properties,
        content=request.content
    )
    graph.add_node(node)
    return NodeResponse(
        entity_id=node.entity_id,
        node_type=node.node_type,
        label=node.label,
        confidence=node.confidence,
        quarantine_flag=node.quarantine_flag,
        is_stale=node.is_stale
    )

@router.get('/nodes/{node_id}', response_model=NodeResponse)
def get_node(node_id: uuid.UUID, graph: KnowledgeGraph = Depends(get_graph)):
    node = graph.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeResponse(
        entity_id=node.entity_id,
        node_type=node.node_type,
        label=node.label,
        confidence=node.confidence,
        quarantine_flag=node.quarantine_flag,
        is_stale=node.is_stale
    )
