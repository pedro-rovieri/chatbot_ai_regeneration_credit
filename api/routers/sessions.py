"""
Endpoints de gerenciamento de sessões de chat
"""
import asyncio
import logging

from fastapi import APIRouter, Request, HTTPException

from api.models.schemas import (
    SessionCreateResponse,
    SessionInfoResponse,
    SessionHistoryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sessions", response_model=SessionCreateResponse, status_code=201)
async def create_session(request: Request):
    """
    Cria uma nova sessão de chat.
    
    Retorna um session_id que deve ser usado em todas as
    chamadas subsequentes ao endpoint /chat.
    """
    agent_manager = request.app.state.agent_manager

    session_id = await asyncio.to_thread(agent_manager.create_session)

    info = agent_manager.get_session_info(session_id)
    return SessionCreateResponse(
        session_id=session_id,
        created_at=info["created_at"],
    )


@router.get("/sessions/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(request: Request, session_id: str):
    """Retorna metadados de uma sessão ativa."""
    agent_manager = request.app.state.agent_manager
    info = agent_manager.get_session_info(session_id)

    if info is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return SessionInfoResponse(**info)


@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(request: Request, session_id: str):
    """Retorna o histórico de mensagens de uma sessão."""
    agent_manager = request.app.state.agent_manager
    history = agent_manager.get_session_history(session_id)

    if history is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return SessionHistoryResponse(
        session_id=session_id,
        messages=history,
    )


@router.delete("/sessions/{session_id}", status_code=200)
async def delete_session(request: Request, session_id: str):
    """Encerra e remove uma sessão de chat."""
    agent_manager = request.app.state.agent_manager
    removed = agent_manager.delete_session(session_id)

    if not removed:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return {"detail": "Sessão encerrada com sucesso"}
