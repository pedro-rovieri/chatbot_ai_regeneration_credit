"""
Regeneration Credit AI Assistant - Interface Streamlit (Versão Enxuta)
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
import uuid
from streamlit.runtime.scriptrunner import get_script_run_ctx

from agents.main_agent import RegenerationCreditAgent
from config.settings import settings, CONVERSATIONS_DIR

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
    initial_sidebar_state="collapsed",
)


# ==================== CSS CUSTOMIZADO ====================

st.markdown("""
<style>
    /* Ajustes para tema escuro */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
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
        font-size: 1.1rem;
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
        max-width: 1400px;
    }
    
    /* Centralizar logo na sidebar */
    [data-testid="stSidebar"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
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
                "app_version": "1.0.0-beta-enxuto",
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
        # Logo no topo (centralizado)
        logo_path = Path(__file__).parent / "documents" / "logo.jpg"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        
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
        
        st.markdown(f"""
        <div class="sidebar-info">
        <strong>🎯 Modo:</strong> Iniciante<br>
        <strong>🌐 Idioma:</strong> PT-BR<br>
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


# ==================== ÁREA PRINCIPAL - CHAT ====================

def render_chat(agent):
    """Renderiza o chat principal"""
    
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


def render_main():
    """Renderiza área principal"""
    
    # Cabeçalho
    st.markdown('<h1 class="main-title">Regeneration Credit AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #e8e8e8; font-size: 1.8rem; margin-bottom: 0.8rem; font-weight: 400;">Tire suas dúvidas sobre o projeto em linguagem natural</p>', unsafe_allow_html=True)
    st.markdown('<div class="beta-disclaimer">⚠️ Versão Beta: Este assistente está em desenvolvimento e pode gerar informações incorretas ou incompletas. Sempre valide informações críticas consultando a documentação oficial do projeto.</div>', unsafe_allow_html=True)
    
    # Link para o site oficial
    st.markdown("""
    <div style="text-align: center; margin: 1rem auto 2rem auto; max-width: 600px;">
        <div style="background: rgba(76, 175, 80, 0.15); padding: 1rem 1.5rem; 
                    border-radius: 8px; border: 2px solid #4caf50;">
            <span style="color: #e8e8e8; font-size: 1.3rem;">Site oficial do projeto: </span>
            <a href="https://regenerationcredit.org/pt" target="_blank" 
               style="color: #4caf50; font-size: 1.3rem; font-weight: 600; text-decoration: none;">
                https://regenerationcredit.org/pt
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar agente
    agent = get_agent()
    
    if agent is None:
        st.error("Não foi possível inicializar o assistente. Recarregue a página.")
        return
    
    # Renderizar chat
    render_chat(agent)


# ==================== MAIN ====================

def main():
    """Função principal"""
    initialize_session_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()

