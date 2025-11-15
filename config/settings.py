"""
Configurações centralizadas do projeto
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
CONVERSATIONS_DIR = DATA_DIR / "conversations"

# Fontes de dados
CONTRACTS_DIR = BASE_DIR / "vector_database" / "contracts"
DOCS_DIR = BASE_DIR / "vector_database" / "docs-site" / "docs"
README_PATH = BASE_DIR / "vector_database" / "README.md"
CHANGELOG_PATH = BASE_DIR / "vector_database" / "CHANGELOG.md"
WHITEPAPER_PATH = BASE_DIR / "documents" / "credito-de-regeneracao_docling.md"

# Novos documentos
MANUAL_CORE_PATH = BASE_DIR / "documents" / "manual_core_credito_regeneracao_docling.md"
TUTORIAL_WALLET_PATH = BASE_DIR / "documents" / "how_to_create_a_wallet_on_the_blockchain_docling.md"
GUIA_MINERACAO_PATH = BASE_DIR / "documents" / "sintrop_node_e_guia_de_mineracao_docling.md"
WHITEPAPER_SINTROP_PATH = BASE_DIR / "documents" / "Whitepaper_Sintrop_uma_blockchain_para_aplicacoes_de_impacto_socioambiental_docling.md"


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Keys (única variável que DEVE estar no .env)
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # LangSmith (Rastreamento e Observabilidade)
    langchain_tracing_v2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "regeneration-credit-chatbot")
    langchain_endpoint: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    
    # LLM - Valores fixos no código
    llm_model: str = "claude-haiku-4-5-20251001"
    llm_temperature: float = 0.0  # Temperatura 0 para máxima determinismo
    llm_max_tokens: int = 4096
    
    # Embeddings - Valores fixos no código
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG - Valores fixos no código
    vector_store_path: str = str(VECTOR_STORE_DIR)
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # Agent - Valores fixos no código
    max_iterations: int = 10
    verbose: bool = False
    
    # Streamlit - Valores fixos no código
    streamlit_port: int = 8501
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global
settings = Settings()


def setup_directories():
    """Cria diretórios necessários"""
    directories = [
        DATA_DIR,
        VECTOR_STORE_DIR,
        CONVERSATIONS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    setup_directories()
    print("✅ Diretórios criados com sucesso!")

