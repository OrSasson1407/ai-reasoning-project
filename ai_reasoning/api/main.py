"""
AI Reasoning Project — API Entrypoint
Sourced from: AIC v1.0
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ai_reasoning.api.middleware import ContractEnforcementMiddleware
from ai_reasoning.api.routes_graph import router as graph_router
from ai_reasoning.api.routes_inference import router as inference_router
from ai_reasoning.api.routes_meta import router as meta_router
from ai_reasoning.api.contracts import ContractViolations

app = FastAPI(
    title="AI Reasoning Architecture API",
    description="Interface Contracts Enforced: NO_TRACE, NO_CONFIDENCE, UNPARSED_INPUT, VCL_BYPASS",
    version="2.0"
)

# Enforce Interface Contracts
app.add_middleware(ContractEnforcementMiddleware)

# Exception handlers for architectural violations
@app.exception_handler(ValueError)
async def architectural_violation_handler(request: Request, exc: ValueError):
    """Maps internal architectural errors to AIC Standard Error Responses."""
    error_msg = str(exc)
    code = "UNKNOWN_ERROR"
    
    if "CV-006" in error_msg: code = "CV-006_QUARANTINE_BYPASS"
    elif "CI-08" in error_msg: code = "CI-08_RESOLUTION_AUTHORITY"
    elif "CV-008" in error_msg: code = "CV-008_VCL_BYPASS"
    
    return JSONResponse(
        status_code=400,
        content={
            "request_id": "req-" + str(uuid.uuid4())[:8],
            "status": "error",
            "error": {
                "code": code,
                "message": error_msg,
                "retryable": False
            }
        }
    )

app.include_router(graph_router, prefix="/graph", tags=["Knowledge Graph"])
app.include_router(inference_router, prefix="/inference", tags=["Inference Engine"])
app.include_router(meta_router, prefix="/meta", tags=["Meta-Cognition"])

@app.get("/health")
async def health_check():
    return {"status": "online", "architecture_version": "v2.0"}
