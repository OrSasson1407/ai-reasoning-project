"""
API Gateway — AIC Validation Tests
Ensures the Gateway successfully intercepts architectural violations.
"""
import pytest
import json
import httpx
from fastapi import HTTPException
from api_gateway.middleware.aic_validator import (
    validate_egress_contract, 
    validate_ingress_contract, 
    ContractViolationException
)

def test_egress_cv001_no_trace_blocked():
    """Rule CV-001: The gateway MUST block responses missing a reasoning trace."""
    
    # Mocking a bad response from the Core Engine
    bad_response = httpx.Response(
        status_code=200,
        headers={"content-type": "application/json"},
        content=json.dumps({"conclusion": "The sky is blue", "confidence": 0.99}) # Missing trace!
    )
    
    with pytest.raises(ContractViolationException) as excinfo:
        validate_egress_contract(bad_response, "/inference/derive")
        
    assert "CV-001_NO_TRACE" in str(excinfo.value.detail)

def test_egress_cv002_no_confidence_blocked():
    """Rule CV-002: The gateway MUST block responses missing a confidence score."""
    
    bad_response = httpx.Response(
        status_code=200,
        headers={"content-type": "application/json"},
        content=json.dumps({"conclusion": "The sky is blue", "reasoning_trace_id": "uuid-123"}) # Missing confidence!
    )
    
    with pytest.raises(ContractViolationException) as excinfo:
        validate_egress_contract(bad_response, "/inference/derive")
        
    assert "CV-002_NO_CONFIDENCE" in str(excinfo.value.detail)

def test_ingress_cv003_unparsed_input_blocked():
    """Rule CV-003: The gateway MUST block raw text from hitting the graph."""
    
    bad_request_body = json.dumps({"raw_text": "I think it will rain today", "source_ids": ["src-1"]}).encode('utf-8')
    
    with pytest.raises(HTTPException) as excinfo:
        validate_ingress_contract(bad_request_body, "/graph/nodes")
        
    assert "CV-003_UNPARSED_INPUT" in str(excinfo.value.detail)
