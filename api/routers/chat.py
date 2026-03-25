"""
Endpoint principal de chat — ponte entre o frontend e o RegenerationCreditAgent
"""
import asyncio
import logging

from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect

from api.models.schemas import ChatRequest, ChatResponse, TokensInfo, StatsInfo

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_chat_response(session_id: str, result: dict) -> ChatResponse:
    """Converte o dict retornado pelo agente em ChatResponse tipado."""
    tokens_raw = result.get("tokens")
    tokens = None
    if tokens_raw:
        tokens = TokensInfo(
            total=tokens_raw.get("total", 0),
            custo=tokens_raw.get("custo", 0.0),
            custo_formatado=tokens_raw.get("custo_formatado", ""),
            tokens_formatado=tokens_raw.get("tokens_formatado", ""),
            por_componente=tokens_raw.get("por_componente", {}),
        )

    stats_raw = result.get("stats")
    stats = None
    if stats_raw:
        stats = StatsInfo(
            total_chamadas_llm=stats_raw.get("total_chamadas_llm", 0),
            chamadas_neste_turno=stats_raw.get("chamadas_neste_turno", 0),
            total_retriever_calls=stats_raw.get("total_retriever_calls", 0),
            iterations=stats_raw.get("iterations", 0),
            tool_calls=stats_raw.get("tool_calls", 0),
        )

    return ChatResponse(
        success=result.get("success", False),
        session_id=session_id,
        response=result.get("response", ""),
        timestamp=result.get("timestamp", ""),
        elapsed_seconds=result.get("elapsed_seconds", 0.0),
        tokens=tokens,
        stats=stats,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    """
    Envia uma mensagem ao chatbot e recebe a resposta.

    Requer um session_id válido (obtido via POST /sessions).
    O agente executa RAG + LLM de forma síncrona em uma thread separada
    para não bloquear o event loop do FastAPI.
    """
    agent_manager = request.app.state.agent_manager
    agent = agent_manager.get_agent(body.session_id)

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou expirada. Crie uma nova sessão via POST /api/v1/sessions",
        )

    logger.info(f"[{body.session_id[:8]}] Mensagem recebida: {body.message[:80]}...")

    try:
        result = await asyncio.to_thread(agent.chat, body.message)
    except Exception as e:
        logger.error(f"[{body.session_id[:8]}] Erro no agente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao processar mensagem")

    response = _build_chat_response(body.session_id, result)

    logger.info(
        f"[{body.session_id[:8]}] Resposta enviada | "
        f"tokens={response.tokens.total if response.tokens else 0} | "
        f"elapsed={response.elapsed_seconds:.2f}s"
    )

    return response


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket para chat em tempo real.
    
    O cliente envia mensagens de texto e recebe respostas JSON.
    Útil para uma UX mais fluida no frontend.
    """
    agent_manager = websocket.app.state.agent_manager
    agent = agent_manager.get_agent(session_id)

    if agent is None:
        await websocket.close(code=4004, reason="Sessão não encontrada")
        return

    await websocket.accept()
    logger.info(f"[{session_id[:8]}] WebSocket conectado")

    try:
        while True:
            message = await websocket.receive_text()

            if not message or not message.strip():
                await websocket.send_json({"error": "Mensagem vazia"})
                continue

            logger.info(f"[{session_id[:8]}] WS mensagem: {message[:80]}...")

            try:
                result = await asyncio.to_thread(agent.chat, message)
                response = _build_chat_response(session_id, result)
                await websocket.send_json(response.model_dump())
            except Exception as e:
                logger.error(f"[{session_id[:8]}] WS erro: {e}", exc_info=True)
                await websocket.send_json({
                    "success": False,
                    "error": "Erro interno ao processar mensagem",
                })

    except WebSocketDisconnect:
        logger.info(f"[{session_id[:8]}] WebSocket desconectado")
