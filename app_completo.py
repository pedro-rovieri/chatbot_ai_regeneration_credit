"""
Regeneration Credit AI Assistant - Interface Streamlit
"""
import sys
from pathlib import Path

# Adicionar diretório chatbot-ia ao sys.path
chatbot_dir = Path(__file__).parent
if str(chatbot_dir) not in sys.path:
    sys.path.insert(0, str(chatbot_dir))

import streamlit as st
from datetime import datetime
import json
import logging
import pandas as pd
import uuid
from streamlit.runtime.scriptrunner import get_script_run_ctx

from agents.main_agent import RegenerationCreditAgent
from config.settings import settings, CONVERSATIONS_DIR
from utils.pricing import formatar_custo, formatar_tokens

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURAÇÃO DA PÁGINA ====================

st.set_page_config(
    page_title="Regeneration Credit AI Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== CSS CUSTOMIZADO ====================

st.markdown("""
<style>
    /* Ajustes para tema escuro */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }
    
    /* Aumentar fonte das tabs do CONTEÚDO PRINCIPAL */
    section[data-testid="stMain"] button[data-baseweb="tab"] {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }
    
    section[data-testid="stMain"] button[data-baseweb="tab"] > div p {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }
    
    /* Título principal */
    .main-title {
        text-align: center;
        color: #4caf50;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
    }
    
    .main-subtitle {
        text-align: center;
        color: #e8e8e8;
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
    }
    
    .beta-disclaimer {
        text-align: center;
        color: #ffa726;
        font-size: 0.9rem;
        background: rgba(255, 167, 38, 0.1);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0 auto 1.5rem auto;
        max-width: 700px;
        border: 1px solid rgba(255, 167, 38, 0.3);
    }
    
    /* Mensagens do chat */
    .user-message {
        background: linear-gradient(135deg, #1e3a5f 0%, #2a5298 100%);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 4px solid #4fc3f7;
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1a3a1a 0%, #2d5a2d 100%);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 4px solid #66bb6a;
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .user-message strong, .assistant-message strong {
        color: #4fc3f7;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .assistant-message strong {
        color: #66bb6a;
    }
    
    /* Badge de tempo de resposta */
    .time-badge {
        background: rgba(76, 175, 80, 0.2);
        color: #66bb6a;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d24;
    }
    
    .sidebar-info {
        background: linear-gradient(135deg, #1a3a1a 0%, #2d5a2d 100%);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #4caf50;
        color: #e0e0e0;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #262b36 0%, #1e232e 100%);
        padding: 0.9rem;
        border-radius: 8px;
        margin: 0.6rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        border: 1px solid #333a47;
        color: #ffffff;
        font-size: 0.9rem;
    }
    
    .stat-box strong {
        color: #4fc3f7;
        font-weight: 600;
    }
    
    /* Botões */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    /* Caixa de boas-vindas */
    .welcome-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #4fc3f7;
        margin: 1rem 0 2rem 0;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .welcome-box strong {
        color: #4fc3f7;
        font-size: 1.1rem;
    }
    
    /* Remover padding extra do container principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        max-width: 900px;
    }
    
    /* Input de texto */
    .stTextInput input {
        border-radius: 8px;
        background-color: #262b36;
        border: 1px solid #4caf50;
        color: #ffffff;
    }
    
    .stTextInput input:focus {
        border-color: #66bb6a;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.3);
    }
    
    /* Ajustar spinner */
    .stSpinner > div {
        border-top-color: #4caf50 !important;
    }
    
    /* Expanders na sidebar */
    .streamlit-expanderHeader {
        background-color: #262b36;
        border-radius: 8px;
        color: #4caf50 !important;
        font-weight: 600;
    }
    
    /* Divisor */
    hr {
        border-color: #333a47;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== FUNÇÕES AUXILIARES ====================

def get_session_id():
    """Obtém Session ID único do Streamlit"""
    try:
        ctx = get_script_run_ctx()
        return ctx.session_id if ctx else f"session_{uuid.uuid4().hex[:8]}"
    except Exception:
        return f"session_{uuid.uuid4().hex[:8]}"


def get_user_agent():
    """Obtém User-Agent do navegador"""
    try:
        return st.context.headers.get("User-Agent", "Unknown")
    except Exception:
        return "Unknown"


def initialize_session_state():
    """Inicializa variáveis de sessão"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    
    if 'tokens_history' not in st.session_state:
        st.session_state.tokens_history = []
    
    if 'retriever_audits' not in st.session_state:
        st.session_state.retriever_audits = []
    
    # Novos: conversation_id e user_id únicos
    if 'conversation_id' not in st.session_state:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.session_state.conversation_id = f"conv_{timestamp}_{uuid.uuid4().hex[:6]}"
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = get_session_id()


def get_agent():
    """Retorna ou cria instância do agente"""
    if st.session_state.agent is None:
        with st.spinner("Inicializando assistente..."):
            try:
                st.session_state.agent = RegenerationCreditAgent()
                logger.info("Agente inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar agente: {e}")
                st.error(f"Erro ao inicializar o assistente: {str(e)}")
                return None
    
    return st.session_state.agent


def save_conversation():
    """Salva conversa atual em arquivo JSON com dados enriquecidos"""
    try:
        # Usar conversation_id existente ou gerar novo
        conversation_id = st.session_state.get('conversation_id', f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}")
        
        # Nome do arquivo baseado no conversation_id
        filename = CONVERSATIONS_DIR / f"{conversation_id}.json"
        
        # Serializar tokens_history (converter datetime para str)
        tokens_history_serializable = []
        for entry in st.session_state.tokens_history:
            serialized = entry.copy()
            if 'timestamp' in serialized and isinstance(serialized['timestamp'], datetime):
                serialized['timestamp'] = serialized['timestamp'].isoformat()
            tokens_history_serializable.append(serialized)
        
        # Calcular analytics
        total_tokens = sum(t.get("total_tokens", 0) for t in st.session_state.tokens_history)
        total_cost = sum(t.get("total_custo", 0.0) for t in st.session_state.tokens_history)
        total_chamadas = sum(t.get("stats", {}).get("total_chamadas_llm", 0) for t in st.session_state.tokens_history)
        
        # Contagem de ferramentas usadas
        tools_usage = {}
        for audit in st.session_state.retriever_audits:
            tool_name = audit.get("tool_name", "unknown")
            tools_usage[tool_name] = tools_usage.get(tool_name, 0) + 1
        
        # Dados enriquecidos
        conversation_data = {
            "conversation_id": conversation_id,
            "user_id": st.session_state.get('user_id', get_session_id()),
            "timestamp": datetime.now().isoformat(),
            "session_info": {
                "session_id": st.session_state.get('user_id', get_session_id()),
                "start_time": st.session_state.session_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - st.session_state.session_start).total_seconds(),
                "user_agent": get_user_agent()
            },
            "messages": st.session_state.messages,
            "tokens_history": tokens_history_serializable,
            "retriever_audits": st.session_state.retriever_audits,
            "analytics": {
                "total_messages": st.session_state.message_count,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "total_llm_calls": total_chamadas,
                "tools_usage": tools_usage,
                "avg_response_time": sum(msg.get("response_time", 0) for msg in st.session_state.messages if msg.get("role") == "assistant") / max(sum(1 for msg in st.session_state.messages if msg.get("role") == "assistant"), 1)
            },
            "metadata": {
                "model": settings.llm_model,
                "rag_enabled": True,
                "app_version": "1.0.0-beta",
                "top_k_results": settings.top_k_results
            }
        }
        
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Conversa salva: {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"❌ Erro ao salvar conversa: {e}")
        return None


def auto_save_conversation():
    """
    Salva conversa automaticamente após cada interação.
    Silencioso - não mostra erros ao usuário para não interromper fluxo.
    """
    try:
        # Só salva se houver mensagens
        if not st.session_state.messages:
            return
        
        save_conversation()
        
    except Exception as e:
        logger.error(f"Erro no auto-save: {e}", exc_info=True)
        # Não mostrar erro ao usuário


def clear_conversation():
    """Limpa conversa e reinicia agente"""
    st.session_state.messages = []
    st.session_state.message_count = 0
    st.session_state.session_start = datetime.now()
    st.session_state.tokens_history = []
    st.session_state.retriever_audits = []
    
    # Gerar novo conversation_id para nova conversa
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    st.session_state.conversation_id = f"conv_{timestamp}_{uuid.uuid4().hex[:6]}"
    
    if st.session_state.agent:
        st.session_state.agent.clear_memory()
    
    logger.info("Conversa limpa - novo conversation_id gerado")


def get_model_display_name():
    """Retorna nome amigável do modelo LLM"""
    model = settings.llm_model
    
    # Mapear modelos técnicos para nomes amigáveis
    if "haiku" in model.lower():
        return "Claude Haiku 4.5"
    elif "sonnet" in model.lower():
        return "Claude Sonnet 4.5"
    elif "opus" in model.lower():
        return "Claude Opus 4.5"
    else:
        return model  # Retorna o nome técnico se não reconhecer


def format_message(role: str, content: str, response_time: float = None):
    """Formata mensagem para exibição"""
    if role == "user":
        return f"""
        <div class="user-message">
            <strong>Você:</strong><br>
            {content}
        </div>
        """
    else:
        time_badge = ""
        if response_time is not None:
            time_badge = f'<span class="time-badge">⏱️ {response_time:.1f}s</span>'
        
        return f"""
        <div class="assistant-message">
            <strong>Assistente:</strong> {time_badge}<br>
            {content}
        </div>
        """


# ==================== SIDEBAR ====================

def render_sidebar():
    """Renderiza sidebar com controles e estatísticas"""
    with st.sidebar:
        # Logo no topo
        logo_path = Path(__file__).parent / "documents" / "logo.jpg"
        if logo_path.exists():
            st.image(str(logo_path), width=150)
        
        st.markdown("## 🌱 Regeneration Credit")
        st.markdown("#### AI Assistant")
        
        st.markdown("---")
        
        # Botão Nova Conversa
        if st.button("🔄 Nova Conversa", use_container_width=True):
            clear_conversation()
            st.rerun()
        
        st.markdown("---")
        
        # Estatísticas da sessão
        st.markdown("### 📊 Estatísticas")
        
        message_count = st.session_state.message_count
        session_duration = datetime.now() - st.session_state.session_start
        minutes = int(session_duration.total_seconds() / 60)
        
        # Calcular tempo médio de resposta
        response_times = [msg.get("response_time", 0) for msg in st.session_state.messages if msg["role"] == "assistant" and "response_time" in msg]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        st.markdown(f"""
        <div class="stat-box">
            <strong>💬 Mensagens:</strong> {message_count}
        </div>
        <div class="stat-box">
            <strong>⏱️ Tempo de sessão:</strong> {minutes} min
        </div>
        <div class="stat-box">
            <strong>⚡ Tempo médio:</strong> {avg_response_time:.1f}s
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Informações sobre o sistema
        st.markdown("### ℹ️ Sobre")
        
        model_name = get_model_display_name()
        st.markdown(f"""
        <div class="sidebar-info">
        <strong>🎯 Modo:</strong> Iniciante<br>
        <strong>🌐 Idioma:</strong> PT-BR<br>
        <strong>🤖 Modelo:</strong> {model_name}<br>
        <strong>🔍 RAG:</strong> Ativo
        </div>
        """, unsafe_allow_html=True)
        
        # Informações do projeto
        with st.expander("📖 Sobre o Projeto"):
            st.markdown("""
            O **Regeneration Credit** é um sistema peer-to-peer de regeneração 
            da natureza baseado em blockchain.
            
            Este assistente pode ajudar você a entender:
            - Como o sistema funciona
            - Tipos de usuários e seus papéis
            - Sistema de eras e epochs
            - Contratos inteligentes
            - Tokenomics e distribuição
            - E muito mais!
            
            **Dica:** Faça perguntas em linguagem natural!
            """)
        
        # Exemplos de perguntas
        with st.expander("💡 Exemplos de Perguntas"):
            st.markdown("""
            - O que é o Regeneration Credit?
            - Quais são os tipos de usuário?
            - Como funciona o sistema de eras?
            - O que são pools e rules contracts?
            - Como é feita a distribuição de tokens?
            - Explique o sistema de níveis
            """)


# ==================== FUNÇÕES DAS ABAS ====================

def render_tab_chat(agent):
    """Renderiza a aba principal de Chat"""
    
    # Exibir mensagem de boas-vindas se não houver histórico
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-box">
        <strong>Bem-vindo!</strong><br><br>
        Sou o assistente do Regeneration Credit. Estou aqui para ajudar você a entender 
        nosso projeto de regeneração da natureza baseado em blockchain.<br><br>
        <strong>Faça qualquer pergunta sobre o projeto</strong> e responderei da forma mais clara possível!
        </div>
        """, unsafe_allow_html=True)
    
    # Container para histórico de mensagens
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            response_time = message.get("response_time", None)
            st.markdown(
                format_message(message["role"], message["content"], response_time),
                unsafe_allow_html=True
            )
    
    # Input do usuário (fixo na parte inferior)
    st.markdown("---")
    
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Digite sua pergunta:",
                placeholder="Ex: O que é o Regeneration Credit?",
                label_visibility="collapsed",
                key="user_input"
            )
        
        with col2:
            submit_button = st.form_submit_button("Enviar", use_container_width=True)
    
    # Processar mensagem do usuário
    if submit_button and user_input:
        # Adicionar mensagem do usuário
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        st.session_state.message_count += 1
        
        # Marcar início do processamento
        start_time = datetime.now()
        
        # Exibir mensagem do usuário
        st.markdown(
            format_message("user", user_input),
            unsafe_allow_html=True
        )
        
        # Gerar resposta do assistente
        with st.spinner("Pensando..."):
            try:
                response = agent.chat(user_input)
                
                # Calcular tempo de resposta
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                if response["success"]:
                    assistant_message = response["response"]
                    
                    # Capturar tokens_history
                    tokens_data = response.get("tokens", {})
                    turno_entry = {
                        "turno_id": len(st.session_state.tokens_history) + 1,
                        "timestamp": datetime.now(),
                        "question": user_input,
                        "response": assistant_message[:100] + "..." if len(assistant_message) > 100 else assistant_message,
                        "elapsed_seconds": response.get("elapsed_seconds", response_time),
                        "total_tokens": tokens_data.get("total", 0),
                        "total_custo": tokens_data.get("custo", 0.0),
                        "por_componente": tokens_data.get("por_componente", {}),
                        "stats": response.get("stats", {})
                    }
                    st.session_state.tokens_history.append(turno_entry)
                    
                    # Capturar retriever_audits
                    retriever_audits = response.get("retriever_audits", [])
                    if retriever_audits:
                        st.session_state.retriever_audits.extend(retriever_audits)
                    
                else:
                    assistant_message = "Desculpe, ocorreu um erro ao processar sua pergunta. Tente reformular ou perguntar algo diferente."
                
                # Adicionar resposta do assistente com tempo de resposta
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": datetime.now().isoformat(),
                    "response_time": response_time
                })
                st.session_state.message_count += 1
                
                # Salvar conversa automaticamente
                auto_save_conversation()
                
                # Exibir resposta com tempo
                st.markdown(
                    format_message("assistant", assistant_message, response_time),
                    unsafe_allow_html=True
                )
                
                # Rerun para limpar input
                st.rerun()
                
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
                st.error(f"Erro ao processar mensagem: {str(e)}")


def render_tab_prompts(agent):
    """Renderiza a aba de Prompts"""
    st.subheader("Prompts do Sistema")
    st.caption("Referência dos prompts usados pelo assistente (atualizado em tempo real)")
    
    with st.expander("System Prompt do Agente", expanded=True):
        # Busca o prompt diretamente do agente (sempre atualizado)
        system_prompt = agent._get_system_prompt()
        st.code(system_prompt, language="markdown")
        st.download_button(
            label="Baixar system_prompt.txt",
            data=system_prompt,
            file_name="system_prompt_regeneration_credit.txt",
            mime="text/plain",
        )
    
    st.markdown("---")
    st.info("Este prompt define o comportamento e estilo do assistente, incluindo regras de resposta, uso de ferramentas e limitações.")


def render_tab_retriever_debug():
    """Renderiza a aba de Retriever Debug"""
    st.subheader("Retriever Debug - Histórico de Buscas")
    st.caption("Visualização detalhada de todas as buscas realizadas no vector store")
    
    retriever_audits = st.session_state.retriever_audits
    
    if not retriever_audits:
        st.info("Nenhuma busca no retriever foi realizada ainda. Faça uma pergunta na aba 'Chat' para ver o debug aqui.")
    else:
        st.success(f"Total de buscas: **{len(retriever_audits)}**")
        st.markdown("---")
        
        # Renderiza cada busca
        for idx, audit in enumerate(retriever_audits, 1):
            tool_name = audit.get("tool_name", "search")
            query = audit.get("query", "")
            num_results = audit.get("num_results", 0)
            elapsed_seconds = audit.get("elapsed_seconds", 0.0)
            filters = audit.get("filter", {})  # Corrigido: 'filter' não 'filters'
            metadata_summary = audit.get("metadata_summary", {})
            chunks = audit.get("chunks", [])
            
            # Header do card
            st.info(f"**Busca #{idx}** - Ferramenta: `{tool_name}`")
            
            with st.container(border=True):
                # Query
                st.markdown("**Query:**")
                st.code(query[:300] + ("..." if len(query) > 300 else ""), language="text")
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Resultados", num_results)
                with col2:
                    st.metric("Tempo", f"{elapsed_seconds:.2f}s")
                with col3:
                    st.metric("Filtros", len(filters) if filters else 0)
                
                # Filtros aplicados
                if filters:
                    st.markdown("**Filtros aplicados:**")
                    for key, value in filters.items():
                        st.caption(f"• {key}: {value}")
                
                # Resumo dos metadados encontrados
                if metadata_summary:
                    st.markdown("**Resumo dos metadados:**")
                    for key, values in metadata_summary.items():
                        if values:
                            # Verifica se values é uma lista/set antes de fazer slicing
                            if isinstance(values, (list, set, tuple)):
                                values_list = list(values)
                                st.caption(f"• {key}: {', '.join(map(str, values_list[:5]))}{' ...' if len(values_list) > 5 else ''}")
                            else:
                                # Se for um valor único (float, int, str), exibe diretamente
                                st.caption(f"• {key}: {values}")
            
            # Chunks retornados (NOVO - com conteúdo completo e metadados)
            if chunks:
                st.markdown("---")
                st.success(f"**Chunks Retornados** ({len(chunks)} chunk{'s' if len(chunks) > 1 else ''})")
                
                for chunk in chunks:
                    chunk_idx = chunk.get("index", 0)
                    score = chunk.get("score", 0.0)
                    content = chunk.get("content", "")
                    metadata = chunk.get("metadata", {})
                    
                    # Metadados principais para o header
                    source = metadata.get("source", "unknown")
                    source_type = metadata.get("source_type", "unknown")
                    
                    # Expander para cada chunk
                    with st.expander(f"**Chunk {chunk_idx}** | Score: {score:.4f} | {source_type} | {source}"):
                        # Metadados completos
                        st.markdown("**Metadados:**")
                        metadata_cols = st.columns(2)
                        
                        for i, (key, value) in enumerate(metadata.items()):
                            with metadata_cols[i % 2]:
                                st.caption(f"**{key}:** {value}")
                        
                        st.markdown("---")
                        
                        # Conteúdo completo
                        st.markdown("**Conteúdo:**")
                        st.code(content, language="text")
            
            # Separador entre buscas
            if idx < len(retriever_audits):
                st.markdown("<div style='text-align: center; color: #888; margin: 2rem 0;'>⬇️ ⬇️ ⬇️</div>", unsafe_allow_html=True)


def render_tab_tokens():
    """Renderiza a aba de Tokens e Custos"""
    st.subheader("Uso de Tokens e Custos")
    st.caption("Rastreamento completo de tokens e custos por turno")
    
    tokens_history = st.session_state.tokens_history
    
    if not tokens_history:
        st.info("Nenhum dado de tokens disponível ainda. Faça uma pergunta na aba 'Chat' para ver as métricas aqui.")
    else:
        # Calcula totais acumulados
        total_tokens_geral = sum(t.get("total_tokens", 0) for t in tokens_history)
        total_custo_geral = sum(t.get("total_custo", 0.0) for t in tokens_history)
        total_chamadas_geral = sum(t.get("stats", {}).get("total_chamadas_llm", 0) for t in tokens_history)
        custo_medio_turno = total_custo_geral / len(tokens_history) if len(tokens_history) > 0 else 0.0
        
        # Resumo financeiro
        st.markdown("### Resumo Financeiro (Toda a Conversa)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tokens", formatar_tokens(total_tokens_geral))
        with col2:
            st.metric("Total Custo", formatar_custo(total_custo_geral))
        with col3:
            st.metric("Total Chamadas LLM", total_chamadas_geral)
        with col4:
            st.metric("Custo Médio/Turno", formatar_custo(custo_medio_turno))
        
        st.markdown("---")
        st.markdown("### Histórico de Turnos")
        
        # Renderiza cada turno
        for idx, turno in enumerate(tokens_history):
            turno_id = turno.get("turno_id", idx + 1)
            timestamp = turno.get("timestamp")
            question = turno.get("question", "")
            total_tokens = turno.get("total_tokens", 0)
            total_custo = turno.get("total_custo", 0.0)
            elapsed_seconds = turno.get("elapsed_seconds", 0.0)
            por_componente = turno.get("por_componente", {})
            stats = turno.get("stats", {})
            
            # Formata timestamp
            try:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                ts_str = timestamp.strftime("%d/%m %H:%M:%S")
            except Exception:
                ts_str = "—"
            
            # Trunca pergunta
            question_preview = question[:60] + "..." if len(question) > 60 else question
            
            # Determina se é o último turno (expandido)
            is_last = (idx == len(tokens_history) - 1)
            
            # Header do expander
            header = f"**Turno {turno_id}** | {ts_str} | {formatar_tokens(total_tokens)} | {formatar_custo(total_custo)} — {question_preview}"
            
            with st.expander(header, expanded=is_last):
                st.markdown(f"**Pergunta completa:** {question}")
                st.markdown(f"**Tempo de resposta:** {elapsed_seconds:.2f}s")
                st.markdown("")
                
                # Breakdown por componente
                if por_componente:
                    st.markdown("**Breakdown por Componente:**")
                    
                    for comp_name, comp_data in por_componente.items():
                        chamadas = comp_data.get("chamadas", 0)
                        tokens_comp = comp_data.get("tokens", {})
                        custo_comp = comp_data.get("custo", 0.0)
                        
                        input_tk = tokens_comp.get("input", 0)
                        output_tk = tokens_comp.get("output", 0)
                        
                        st.markdown(f"**{comp_name.capitalize()}** ({chamadas} chamada{'s' if chamadas > 1 else ''})")
                        
                        with st.container(border=True):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.caption(f"Tokens: Input {formatar_tokens(input_tk)} | Output {formatar_tokens(output_tk)}")
                            with col2:
                                st.caption(f"Custo: {formatar_custo(custo_comp)}")
                        
                        st.markdown("")
                
                # Estatísticas adicionais
                if stats:
                    with st.expander("Ver estatísticas detalhadas"):
                        st.json(stats)
        
        # Botão de download CSV
        st.markdown("---")
        st.markdown("### Exportar Dados")
        
        # Gera CSV flat
        all_data = []
        for turno in tokens_history:
            turno_id = turno.get("turno_id", 0)
            timestamp = turno.get("timestamp")
            if isinstance(timestamp, datetime):
                ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(timestamp, str):
                try:
                    ts_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    ts_str = timestamp
            else:
                ts_str = "—"
            
            question = turno.get("question", "")
            total_tokens = turno.get("total_tokens", 0)
            total_custo = turno.get("total_custo", 0.0)
            elapsed_seconds = turno.get("elapsed_seconds", 0.0)
            
            all_data.append({
                "turno": turno_id,
                "timestamp": ts_str,
                "question": question,
                "total_tokens": total_tokens,
                "total_custo": total_custo,
                "tempo_segundos": elapsed_seconds
            })
        
        if all_data:
            df_export = pd.DataFrame(all_data)
            csv_data = df_export.to_csv(index=False)
            
            st.download_button(
                label="Baixar dados de tokens (CSV)",
                data=csv_data,
                file_name=f"tokens_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


# ==================== ÁREA PRINCIPAL ====================

def render_main():
    """Renderiza área principal com sistema de tabs"""
    
    # Cabeçalho
    st.markdown('<h1 class="main-title">Regeneration Credit AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #e8e8e8; font-size: 1.8rem; margin-bottom: 0.8rem; font-weight: 400;">Tire suas dúvidas sobre o projeto em linguagem natural</p>', unsafe_allow_html=True)
    st.markdown('<div class="beta-disclaimer">⚠️ Versão Beta: Este assistente está em desenvolvimento e pode gerar informações incorretas ou incompletas. Sempre valide informações críticas consultando a documentação oficial do projeto.</div>', unsafe_allow_html=True)
    
    # Inicializar agente
    agent = get_agent()
    
    if agent is None:
        st.error("Não foi possível inicializar o assistente. Recarregue a página.")
        return
    
    # Sistema de Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Prompts", "Retriever Debug", "Tokens e Custos"])
    
    with tab1:
        render_tab_chat(agent)
    
    with tab2:
        render_tab_prompts(agent)
    
    with tab3:
        render_tab_retriever_debug()
    
    with tab4:
        render_tab_tokens()


# ==================== MAIN ====================

def main():
    """Função principal"""
    initialize_session_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()

