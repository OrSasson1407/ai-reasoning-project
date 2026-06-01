from fastapi import APIRouter, Depends, HTTPException
from ai_reasoning.api.models import InferenceRequest, InferenceResponse, NodeResponse
from ai_reasoning.api.dependencies import get_engine
from ai_reasoning.inference.engine import InferenceEngine
from ai_reasoning.core.exceptions import AIReasoningArchitecturalError

router = APIRouter(prefix='/inference', tags=['Reasoning Engine'])

@router.post('/derive', response_model=InferenceResponse)
def derive_knowledge(request: InferenceRequest, engine: InferenceEngine = Depends(get_engine)):
    try:
        # Trigger the 7-layer architecture
        engine.derive_node(
            premise_ids=request.premise_ids,
            mode=request.mode,
            conclusion_label=request.conclusion_label,
            conclusion_type=request.conclusion_type
        )
        
        # In a real scenario, derive_node would return the ID of the new node.
        # For the API, we acknowledge the process completed without Architectural Errors.
        return InferenceResponse(status="SUCCESS")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIReasoningArchitecturalError as e:
        raise HTTPException(status_code=403, detail=f"Invariant Violation: {str(e)}")
