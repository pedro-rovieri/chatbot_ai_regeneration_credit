"""
Gerenciador de sessões e instâncias do RegenerationCreditAgent.

Cada sessão de chat no frontend recebe sua própria instância do agente
(memória conversacional isolada), mas o VectorStore ChromaDB é compartilhado.
Sessões expiram automaticamente após um período de inatividade (TTL).
"""
import uuid
import threading
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from agents.main_agent import RegenerationCreditAgent

logger = logging.getLogger(__name__)


class SessionData:
    """Dados de uma sessão ativa."""

    def __init__(self, agent: RegenerationCreditAgent):
        self.agent = agent
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.message_count = 0

    def touch(self):
        self.last_active = datetime.now()
        self.message_count += 1


class AgentManager:
    """
    Pool de sessões do chatbot.

    - Cria/destrói instâncias do RegenerationCreditAgent por sessão
    - Expira sessões inativas (TTL configurável)
    - Limita quantidade máxima de sessões simultâneas
    - Thread-safe via lock
    """

    def __init__(self, max_sessions: int = 100, ttl_minutes: int = 60):
        self.max_sessions = max_sessions
        self.ttl = timedelta(minutes=ttl_minutes)
        self._sessions: Dict[str, SessionData] = {}
        self._lock = threading.Lock()
        logger.info(
            f"AgentManager inicializado | max_sessions={max_sessions} | ttl={ttl_minutes}min"
        )

    @property
    def active_session_count(self) -> int:
        with self._lock:
            return len(self._sessions)

    def create_session(self) -> str:
        """Cria uma nova sessão com um agente dedicado."""
        with self._lock:
            self._evict_expired()

            if len(self._sessions) >= self.max_sessions:
                oldest_id = min(
                    self._sessions,
                    key=lambda sid: self._sessions[sid].last_active,
                )
                logger.warning(
                    f"Limite de sessões atingido. Removendo sessão mais antiga: {oldest_id}"
                )
                self._remove_session(oldest_id)

        session_id = str(uuid.uuid4())
        logger.info(f"Criando sessão {session_id}...")

        agent = RegenerationCreditAgent()

        with self._lock:
            self._sessions[session_id] = SessionData(agent=agent)

        logger.info(
            f"Sessão {session_id} criada | Total ativas: {len(self._sessions)}"
        )
        return session_id

    def get_agent(self, session_id: str) -> Optional[RegenerationCreditAgent]:
        """Retorna o agente da sessão (ou None se não existir/expirada)."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            if datetime.now() - session.last_active > self.ttl:
                logger.info(f"Sessão {session_id} expirada por TTL")
                self._remove_session(session_id)
                return None
            session.touch()
            return session.agent

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retorna metadados da sessão."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            return {
                "session_id": session_id,
                "created_at": session.created_at.isoformat(),
                "last_active": session.last_active.isoformat(),
                "message_count": session.message_count,
            }

    def get_session_history(self, session_id: str) -> Optional[list]:
        """Retorna histórico de mensagens da sessão."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            return session.agent.get_conversation_history()

    def delete_session(self, session_id: str) -> bool:
        """Remove uma sessão e libera recursos."""
        with self._lock:
            if session_id not in self._sessions:
                return False
            self._remove_session(session_id)
            logger.info(
                f"Sessão {session_id} removida | Total ativas: {len(self._sessions)}"
            )
            return True

    def cleanup(self):
        """Remove todas as sessões (chamado no shutdown)."""
        with self._lock:
            session_ids = list(self._sessions.keys())
            for sid in session_ids:
                self._remove_session(sid)
            logger.info("Todas as sessões removidas (shutdown)")

    def _remove_session(self, session_id: str):
        """Remove sessão sem lock (deve ser chamado dentro de um bloco with self._lock)."""
        session = self._sessions.pop(session_id, None)
        if session:
            try:
                session.agent.clear_memory()
            except Exception as e:
                logger.error(f"Erro ao limpar agente da sessão {session_id}: {e}")

    def _evict_expired(self):
        """Remove sessões expiradas (deve ser chamado dentro de um bloco with self._lock)."""
        now = datetime.now()
        expired = [
            sid
            for sid, s in self._sessions.items()
            if now - s.last_active > self.ttl
        ]
        for sid in expired:
            logger.info(f"Evicting sessão expirada: {sid}")
            self._remove_session(sid)
