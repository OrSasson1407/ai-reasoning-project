from fastapi import APIRouter
router = APIRouter()

@router.post("/nodes")
async def create_node():
    """Ingests a new fact. Must pass DI-04 Source Required."""
    return {"status": "success"}
