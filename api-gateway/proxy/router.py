"""
API Gateway — Reverse Proxy Router
Handles forwarding traffic to the Core Engine and triggering AIC validations.
"""
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import StreamingResponse
import httpx
from api_gateway.core.config import settings
from api_gateway.middleware.auth import verify_api_key
from api_gateway.middleware.aic_validator import validate_egress_contract, validate_ingress_contract

router = APIRouter()
client = httpx.AsyncClient(base_url=settings.CORE_ENGINE_URL, timeout=60.0)

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], dependencies=[Depends(verify_api_key)])
async def proxy_to_core(request: Request, path: str):
    """
    Proxies requests to the internal AI Reasoning Core Engine.
    """
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    
    # 1. Read request body and enforce Ingress Contracts (CV-003)
    body = await request.body()
    if request.method in ["POST", "PUT", "PATCH"]:
        validate_ingress_contract(body, request.url.path)

    # 2. Forward request
    req = client.build_request(
        method=request.method,
        url=url,
        headers=request.headers.raw,
        content=body
    )
    
    try:
        response = await client.send(req)
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Core Inference Engine is offline or unreachable.")

    # 3. Enforce Egress Contracts (CV-001, CV-002)
    if settings.ENFORCE_AIC_CONTRACTS:
        validate_egress_contract(response, request.url.path)

    # 4. Return safely validated response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
