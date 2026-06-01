"""
AI Reasoning Project — System Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class SystemConfig:
    # Environment boundaries
    DEBUG_MODE = os.getenv("AI_REASONING_DEBUG", "False").lower() == "true"
    
    # RRS Constants
    CONFIDENCE_FLOOR = 0.05  # UP-10: Zero is reserved for active contradictions
    
    # AIC Contract Enforcement
    STRICT_CONTRACT_ENFORCEMENT = True
    
    # VCL and Security
    ALLOW_AUTO_RESOLUTION = False # CI-08 forbids automatic HALT resolution
    
    # Database
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://localhost:5432")
    
    # Auditing
    AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "system_audit.log")
