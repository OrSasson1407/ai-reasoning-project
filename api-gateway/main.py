"""
AI Reasoning Project — API Gateway Entrypoint
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api_gateway.proxy.router import router as proxy_router
from api_gateway.core.config import settings
from api_gateway.core.logger import gateway_logger
from api_gateway.middleware.aic_validator import ContractViolationException
from api_gateway.middleware.rate_limit import RateLimitMiddleware
import uuid
import datetime
import time

app = FastAPI(
    title="AI Reasoning API Gateway",
    description="Edge router enforcing AIC Interface Contracts and Security.",
    version="2.0"
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rate Limiting Middleware (100 req / minute default)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# 3. Access Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    gateway_logger.info(
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Status: {response.status_code} | Latency: {process_time:.4f}s"
    )
    return response

# 4. Standard AIC Error Handling
@app.exception_handler(ContractViolationException)
async def aic_violation_handler(request: Request, exc: ContractViolationException):
    """Formats contract violations strictly according to AIC Section 5.1"""
    gateway_logger.error(f"CONTRACT VIOLATION INTERCEPTED: {exc.detail['error_code']}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "status": "error",
            "error": {
                "code": exc.detail["error_code"],
                "message": exc.detail["message"],
                "retryable": False
            }
        }
    )

@app.get("/health", tags=["Gateway Operations"])
async def health_check():
    return {
        "service": "api-gateway",
        "status": "online",
        "aic_enforcement": settings.ENFORCE_AIC_CONTRACTS,
        "core_engine_target": settings.CORE_ENGINE_URL
    }

# Mount the proxy router
app.include_router(proxy_router)
