from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_reasoning.api.models import NodeCreateRequest, NodeResponse, InferenceRequest, InferenceResponse
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.core.node import Node
from ai_reasoning.inference.engine import InferenceEngine

app = FastAPI(title='AI Reasoning Cognitive Engine V1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

engine_graph = KnowledgeGraph()
reasoning_engine = InferenceEngine(engine_graph)

@app.post('/graph/nodes', response_model=NodeResponse)
def add_node(req: NodeCreateRequest):
    node = Node(node_type=req.node_type, label=req.label, confidence=req.confidence, properties=req.properties, content=req.content)
    engine_graph.add_node(node)
    return NodeResponse(entity_id=node.entity_id, node_type=node.node_type, label=node.label, confidence=node.confidence, quarantine_flag=node.quarantine_flag, is_stale=node.is_stale)

@app.post('/inference/derive', response_model=InferenceResponse)
def derive_knowledge(req: InferenceRequest):
    try:
        result = reasoning_engine.derive_node(req.premise_ids, req.mode, req.conclusion_label, req.conclusion_type)
        return InferenceResponse(status=result["status"], conclusion_node_id=result.get("node_id"))
    except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
    except Exception as e: raise HTTPException(status_code=403, detail=f"Invariant Violation: {str(e)}")

@app.get('/health')
def health_check(): return {'status': 'ONLINE', 'layer': 'Gateway', 'integrity': 'VERIFIED'}
