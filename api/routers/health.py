"""
Endpoint de health check da API
"""
from fastapi import APIRouter, Request

from api.models.schemas import HealthResponse

router = APIRouter()

API_VERSION = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Verifica o status do serviço."""
    agent_manager = request.app.state.agent_manager
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        active_sessions=agent_manager.active_session_count,
        vector_store_loaded=True,
    )
