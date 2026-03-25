"""
Schemas Pydantic para request/response da API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="ID da sessão de chat")
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Mensagem do usuário",
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class TokensInfo(BaseModel):
    total: int = 0
    custo: float = 0.0
    custo_formatado: str = ""
    tokens_formatado: str = ""
    por_componente: Dict[str, Any] = Field(default_factory=dict)


class StatsInfo(BaseModel):
    total_chamadas_llm: int = 0
    chamadas_neste_turno: int = 0
    total_retriever_calls: int = 0
    iterations: int = 0
    tool_calls: int = 0


class ChatResponse(BaseModel):
    success: bool
    session_id: str
    response: str
    timestamp: str = ""
    elapsed_seconds: float = 0.0
    tokens: Optional[TokensInfo] = None
    stats: Optional[StatsInfo] = None


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: str


class SessionInfoResponse(BaseModel):
    session_id: str
    created_at: str
    last_active: str
    message_count: int


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]


class HealthResponse(BaseModel):
    status: str
    version: str
    active_sessions: int
    vector_store_loaded: bool


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
