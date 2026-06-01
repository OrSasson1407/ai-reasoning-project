"""
API Gateway — Rate Limiting Middleware
Protects the core inference engine from denial-of-service or runaway loops.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean up old requests
        self.clients[client_ip] = [req_time for req_time in self.clients[client_ip] if now - req_time < self.window_seconds]
        
        if len(self.clients[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=429, 
                detail={"error_code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests to the reasoning engine. Please slow down."}
            )
            
        self.clients[client_ip].append(now)
        return await call_next(request)
