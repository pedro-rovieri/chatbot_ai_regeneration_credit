"""
Aplicação FastAPI — ponto de entrada da API do Regeneration Credit AI Assistant.

Inicialização:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    
Ou via script:
    python run_api.py
"""
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Garante que o diretório raiz do projeto está no sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.routers import health, sessions, chat
from api.services.agent_manager import AgentManager
from config.settings import settings, setup_directories

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

ALLOWED_ORIGINS = [
    "https://regenerationcredit.org",
    "https://www.regenerationcredit.org",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"


# ============================================================================
# LIFESPAN (startup / shutdown)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # --- STARTUP ---
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Iniciando Regeneration Credit AI Assistant API...")

    setup_directories()

    agent_manager = AgentManager(max_sessions=100, ttl_minutes=60)
    app.state.agent_manager = agent_manager

    logger.info(f"API v{API_VERSION} pronta em {API_PREFIX}")
    yield

    # --- SHUTDOWN ---
    logger.info("Encerrando API...")
    agent_manager.cleanup()
    logger.info("API encerrada.")


# ============================================================================
# APP FASTAPI
# ============================================================================

app = FastAPI(
    title="Regeneration Credit AI Assistant API",
    description=(
        "API REST para o chatbot de IA do projeto Regeneration Credit. "
        "Utiliza RAG (Retrieval-Augmented Generation) com Claude Haiku "
        "para responder perguntas sobre o ecossistema Regeneration Credit."
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# CORS — permite que o frontend Next.js acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix=API_PREFIX, tags=["Health"])
app.include_router(sessions.router, prefix=API_PREFIX, tags=["Sessions"])
app.include_router(chat.router, prefix=API_PREFIX, tags=["Chat"])


@app.get("/", include_in_schema=False)
async def root():
    """Redireciona para a documentação interativa."""
    return {
        "service": "Regeneration Credit AI Assistant API",
        "version": API_VERSION,
        "docs": f"{API_PREFIX}/docs",
    }
