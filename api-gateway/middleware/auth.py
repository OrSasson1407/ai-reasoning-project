"""
API Gateway — Ingress Authentication
Prevents unauthorized access to the reasoning engine.
"""
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from api_gateway.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
        
    if api_key != settings.AUTH_SECRET:
        raise HTTPException(status_code=403, detail="Invalid API Key")
        
    return api_key
