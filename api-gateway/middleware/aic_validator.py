"""
API Gateway — AIC Contract Validator
Enforces Document AIC v1.0 constraints at the network edge.
"""
import json
from fastapi import HTTPException
import httpx

class ContractViolationException(HTTPException):
    def __init__(self, code: str, message: str):
        super().__init__(status_code=500, detail={"error_code": code, "message": message})

def validate_egress_contract(response: httpx.Response, path: str):
    """
    Intercepts the response from the Core Engine before sending it to the client.
    Checks for CV-001 (NO_TRACE) and CV-002 (NO_CONFIDENCE).
    """
    if response.status_code != 200 or "application/json" not in response.headers.get("content-type", ""):
        return

    try:
        body = response.json()
    except Exception:
        return

    # Egress Validation: If a conclusion is returned, it MUST have a trace and confidence
    if path.startswith("/inference/derive"):
        if "reasoning_trace_id" not in body:
            raise ContractViolationException(
                code="CV-001_NO_TRACE", 
                message="CRITICAL: Core engine returned a conclusion without a reasoning_trace_id."
            )
        if "confidence" not in body:
            raise ContractViolationException(
                code="CV-002_NO_CONFIDENCE", 
                message="CRITICAL: Core engine returned a conclusion without a confidence score."
            )

def validate_ingress_contract(body: bytes, path: str):
    """
    Checks incoming payloads.
    Prevents CV-003 (UNPARSED_INPUT) — L1 passing free text directly to L2.
    """
    if path.startswith("/graph/nodes"):
        try:
            data = json.loads(body)
            if "raw_text" in data and "parsed_statement" not in data:
                raise HTTPException(
                    status_code=400, 
                    detail={"error_code": "CV-003_UNPARSED_INPUT", "message": "L1 passed free text directly to L2. Input must be parsed."}
                )
            if "source_ids" not in data or not data["source_ids"]:
                raise HTTPException(
                    status_code=400, 
                    detail={"error_code": "CV-009_MISSING_SOURCE", "message": "Node ingested without source_ids (Rule DI-04)."}
                )
        except json.JSONDecodeError:
            pass
