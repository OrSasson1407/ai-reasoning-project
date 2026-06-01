"""
AI Reasoning Project — Meta-Cognition API Routes
"""

from fastapi import APIRouter
from ai_reasoning.meta.horizon import EpistemicHorizon

router = APIRouter()
horizon_engine = EpistemicHorizon()

@router.get("/horizon/{domain}")
async def get_domain_horizon(domain: str):
    """Checks if a reasoning domain is within the system's epistemic horizon."""
    return horizon_engine.check_horizon(domain)

@router.get("/ebd/report")
async def get_ebd_report():
    """Triggers the EBD evaluation and returns the post-consolidation report."""
    # Requires injection of the graph and engine in a full FastAPI dependency setup
    return {"status": "Report generation available via BenchmarkingEngine."}
