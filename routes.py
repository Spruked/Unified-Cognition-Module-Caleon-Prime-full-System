from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from vault_loader import load_seed_vault
from trace_router import trace_reasoning

router = APIRouter()

class ReasonRequest(BaseModel):
    content: str
    priority: str
    metadata: Dict[str, Any]

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "Unified Cognition Module"}

@router.post("/reason")
async def reason(request: ReasonRequest):
    try:
        # Load seed vault
        seed_vault = load_seed_vault()

        # Perform reasoning (placeholder logic)
        response = await trace_reasoning(request.content, request.priority, request.metadata, seed_vault)

        return {"result": response, "priority": request.priority, "metadata": request.metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))