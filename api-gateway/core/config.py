"""
API Gateway — System Configuration
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8080"))
    # The URL of the internal Layer 4 Inference Engine
    CORE_ENGINE_URL: str = os.getenv("CORE_ENGINE_URL", "http://localhost:8000")
    AUTH_SECRET: str = os.getenv("AUTH_SECRET", "strict-architecture-key")
    ENFORCE_AIC_CONTRACTS: bool = True
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "True").lower() == "true"

settings = Settings()
