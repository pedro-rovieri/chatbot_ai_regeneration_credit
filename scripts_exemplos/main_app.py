#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
from threading import Thread, Lock
import base64
import time as _time

import streamlit as st
from dotenv import load_dotenv

from scripts.finance_ai import (
    run_agent_turn_single_llm,
    ConversationLogger,
    ConversationMemory,
    MODEL_CHOICES,
    DEFAULT_MODEL,
)
from scripts.finance_ai_config import SYSTEM_PROMPT, LIMIT_RETRIEVER_REACHED_MSG
from scripts.finance_ai_escopo import format_escopo_message
from scripts.finance_ai_seletor_config import SYSTEM_PROMPT_SELETOR
from scripts.consultar_vector_store_retriever import (
    RETRIEVER_STEP1_PROMPT,
    RETRIEVER_STEP2_PROMPT,
)
from scripts.finance_ai_pricing import formatar_custo, formatar_tokens
from scripts.conversation_manager import (
    salvar_conversa,
    carregar_conversa_completa,
    listar_conversas,
    excluir_conversa,
    desconverte_nome_conversa,
)

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)

st.set_page_config(page_title="Analista AI", page_icon=None, layout="wide")

# Estilo: ajustar fonte dos títulos das abas e ajustes de UI
st.markdown(
    """
    <style>
    /* Ajustar fonte das tabs da SIDEBAR */
    section[data-testid="stSidebar"] button[data-baseweb="tab"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    section[data-testid="stSidebar"] button[data-baseweb="tab"] > div p {
        font-size: 1rem !important;
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
    
    /* Aumentar fonte do label do TextArea */
    label[data-testid="stTextAreaLabel"] p {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Garantir que o markdown dentro do label também aumente */
    div[data-testid="stTextArea"] label p {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _escape_markdown(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = text.replace("\\", "\\\\")
    for ch in ["$", "*", "_", "[", "]", "(", ")", "#", "`", ">", "+", "!", "|"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def _escape_md_preserving_bullets(block: str) -> str:
    if not isinstance(block, str):
        return block
    out_lines = []
    for line in block.splitlines():
        stripped = line.lstrip()
        prefix_ws = line[: len(line) - len(stripped)]
        if stripped.startswith("- "):
            content = stripped[2:]
            out_lines.append(f"{prefix_ws}- {_escape_markdown(content)}")
        else:
            out_lines.append(f"{prefix_ws}{_escape_markdown(stripped)}")
    return "\n".join(out_lines)


def _init_state() -> None:
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory()
    if "logger" not in st.session_state:
        st.session_state.logger = ConversationLogger()
    if "retriever_events" not in st.session_state:
        st.session_state.retriever_events = []
    if "escopo" not in st.session_state:
        st.session_state.escopo = ""
    if "tokens_history" not in st.session_state:
        st.session_state.tokens_history = []
    if "conversa_atual" not in st.session_state:
        st.session_state.conversa_atual = ""
    
    # Inicializa configurações com valores padrão
    if "model_key" not in st.session_state:
        option_keys = list(MODEL_CHOICES.keys())
        default_key = next((k for k, v in MODEL_CHOICES.items() if v == DEFAULT_MODEL), option_keys[-1])
        st.session_state.model_key = default_key
    if "reasoning_effort" not in st.session_state:
        st.session_state.reasoning_effort = "medium"
    if "retriever_model" not in st.session_state:
        st.session_state.retriever_model = "gpt-5-mini-2025-08-07"
    if "max_tool_calls" not in st.session_state:
        st.session_state.max_tool_calls = 3
    if "seletor_model" not in st.session_state:
        st.session_state.seletor_model = "gpt-5-mini-2025-08-07"
    if "seletor_reasoning_effort" not in st.session_state:
        st.session_state.seletor_reasoning_effort = "medium"


_init_state()


# ===== FUNÇÕES DE GERENCIAMENTO DE CONVERSAS =====

def _obter_configuracoes_atuais() -> Dict[str, Any]:
    """Captura as configurações atuais da sidebar para salvar."""
    return {
        'model_key': st.session_state.get('model_key', list(MODEL_CHOICES.keys())[-1]),
        'reasoning_effort': st.session_state.get('reasoning_effort', 'medium'),
        'retriever_model': st.session_state.get('retriever_model', 'gpt-5-mini-2025-08-07'),
        'max_tool_calls': st.session_state.get('max_tool_calls', 3),
        'seletor_model': st.session_state.get('seletor_model', 'gpt-5-mini-2025-08-07'),
        'seletor_reasoning_effort': st.session_state.get('seletor_reasoning_effort', 'medium'),
    }


def _aplicar_configuracoes(configuracoes: Dict[str, Any]) -> None:
    """Aplica configurações carregadas de uma conversa na sidebar."""
    st.session_state.model_key = configuracoes.get('model_key', list(MODEL_CHOICES.keys())[-1])
    st.session_state.reasoning_effort = configuracoes.get('reasoning_effort', 'medium')
    st.session_state.retriever_model = configuracoes.get('retriever_model', 'gpt-5-mini-2025-08-07')
    st.session_state.max_tool_calls = configuracoes.get('max_tool_calls', 3)
    st.session_state.seletor_model = configuracoes.get('seletor_model', 'gpt-5-mini-2025-08-07')
    st.session_state.seletor_reasoning_effort = configuracoes.get('seletor_reasoning_effort', 'medium')


def _salvar_conversa_atual() -> None:
    """Salva o estado atual da conversa em arquivo."""
    try:
        configuracoes = _obter_configuracoes_atuais()
        nome_arquivo = salvar_conversa(
            escopo=st.session_state.escopo,
            memory=st.session_state.memory,
            retriever_events=st.session_state.retriever_events,
            tokens_history=st.session_state.tokens_history,
            logger=st.session_state.logger,
            configuracoes=configuracoes,
            nome_arquivo_existente=st.session_state.conversa_atual if st.session_state.conversa_atual else None
        )
        # Atualiza conversa_atual se era uma nova conversa
        if not st.session_state.conversa_atual and nome_arquivo:
            st.session_state.conversa_atual = nome_arquivo
    except Exception as e:
        st.error(f"Erro ao salvar conversa: {e}")


def _selecionar_conversa(nome_arquivo: str) -> None:
    """Callback ao clicar em uma conversa na lista."""
    try:
        # 1. Salva conversa atual antes de trocar
        if st.session_state.memory.get_ui_messages() or st.session_state.escopo.strip():
            _salvar_conversa_atual()
        
        # 2. Carrega conversa selecionada
        conversa_data = carregar_conversa_completa(nome_arquivo)
        
        # 3. Restaura estado
        st.session_state.escopo = conversa_data['escopo']
        st.session_state.memory = conversa_data['memory']
        st.session_state.retriever_events = conversa_data['retriever_events']
        st.session_state.tokens_history = conversa_data['tokens_history']
        st.session_state.logger = conversa_data['logger']
        st.session_state.conversa_atual = nome_arquivo
        
        # 4. Restaura configurações
        _aplicar_configuracoes(conversa_data['configuracoes'])
        
        # 5. Força reset do widget do escopo para exibir o escopo carregado
        if "escopo_widget_key" in st.session_state:
            st.session_state.escopo_widget_key += 1
        
    except Exception as e:
        st.error(f"Erro ao carregar conversa: {e}")


def _nova_conversa() -> None:
    """Callback do botão 'Nova conversa'."""
    try:
        # 1. Salva conversa atual antes de criar nova
        if st.session_state.memory.get_ui_messages() or st.session_state.escopo.strip():
            _salvar_conversa_atual()
        
        # 2. Limpa estado (cria nova conversa)
        st.session_state.memory = ConversationMemory()
        st.session_state.logger = ConversationLogger()
        st.session_state.retriever_events = []
        st.session_state.escopo = ""
        st.session_state.tokens_history = []
        st.session_state.conversa_atual = ""
        
        # 3. Força reset do widget do escopo (incrementa key)
        if "escopo_widget_key" in st.session_state:
            st.session_state.escopo_widget_key += 1
        
    except Exception as e:
        st.error(f"Erro ao criar nova conversa: {e}")


# Sidebar com tabs (Configurações e Conversas)
with st.sidebar:
    tab_configuracoes, tab_conversas = st.tabs(["Configurações", "Conversas"])
    
    # ===== TAB CONVERSAS =====
    with tab_conversas:
        # Botão Nova Conversa
        st.button(
            '➕ Nova conversa',
            on_click=_nova_conversa,
            use_container_width=True,
            key='btn_nova_conversa'
        )
        
        st.markdown('')
        
        # Lista de conversas salvas
        conversas = listar_conversas()
        
        if conversas:
            st.markdown("**Conversas salvas:**")
            
            # Checkbox para selecionar conversa a excluir
            if 'conversa_para_excluir' not in st.session_state:
                st.session_state.conversa_para_excluir = None
            
            for nome_arquivo in conversas:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Nome da conversa (com caracteres especiais)
                    nome_conversa = desconverte_nome_conversa(nome_arquivo)
                    if len(nome_conversa) == 30:
                        nome_conversa += '...'
                    
                    # Botão da conversa (desabilitado se for a atual)
                    st.button(
                        nome_conversa,
                        on_click=_selecionar_conversa,
                        args=(nome_arquivo,),
                        disabled=(nome_arquivo == st.session_state.conversa_atual),
                        use_container_width=True,
                        key=f'btn_conv_{nome_arquivo}'
                    )
                
                with col2:
                    # Checkbox para marcar para exclusão
                    is_selected = st.checkbox(
                        '🗑️',
                        value=(st.session_state.conversa_para_excluir == nome_arquivo),
                        key=f'chk_del_{nome_arquivo}',
                        label_visibility='collapsed',
                        help='Selecionar para excluir'
                    )
                    if is_selected:
                        st.session_state.conversa_para_excluir = nome_arquivo
                    elif st.session_state.conversa_para_excluir == nome_arquivo:
                        st.session_state.conversa_para_excluir = None
            
            # Botão Excluir (só aparece se algo foi selecionado)
            if st.session_state.conversa_para_excluir:
                st.markdown('---')
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button('❌ Excluir', use_container_width=True, key='btn_excluir_confirmar'):
                        nome_para_excluir = st.session_state.conversa_para_excluir
                        if excluir_conversa(nome_para_excluir):
                            # Se era a conversa atual, manter estado mas sem arquivo associado
                            if nome_para_excluir == st.session_state.conversa_atual:
                                st.session_state.conversa_atual = ""
                            st.session_state.conversa_para_excluir = None
                            st.success('Conversa excluída!')
                            st.rerun()
                        else:
                            st.error('Erro ao excluir conversa')
                
                with col_btn2:
                    if st.button('Cancelar', use_container_width=True, key='btn_excluir_cancelar'):
                        st.session_state.conversa_para_excluir = None
                        st.rerun()
        else:
            st.info("Nenhuma conversa salva ainda")
    
    # ===== TAB CONFIGURAÇÕES =====
    with tab_configuracoes:
        st.markdown("**Modelo do Analista**")
        
        option_keys = list(MODEL_CHOICES.keys())
        default_key = next((k for k, v in MODEL_CHOICES.items() if v == DEFAULT_MODEL), option_keys[-1])
        try:
            default_index = option_keys.index(default_key)
        except ValueError:
            default_index = 0
        
        # Usar session_state para persistir valores entre tabs
        if 'model_key' not in st.session_state:
            st.session_state.model_key = default_key
        
        model_key = st.selectbox(
            "Modelo",
            options=option_keys,
            index=option_keys.index(st.session_state.model_key) if st.session_state.model_key in option_keys else default_index,
            format_func=lambda k: f"{k} - {MODEL_CHOICES.get(k, k)}",
            key='select_model'
        )
        st.session_state.model_key = model_key
        
        if 'reasoning_effort' not in st.session_state:
            st.session_state.reasoning_effort = 'medium'
        
        reasoning_effort = st.selectbox(
            "Reasoning effort",
            options=["low", "medium", "high"],
            index=["low", "medium", "high"].index(st.session_state.reasoning_effort),
            help="Controla o esforço de raciocínio do modelo (medium = balanceado)",
            key='select_reasoning'
        )
        st.session_state.reasoning_effort = reasoning_effort
        
        st.markdown("---")
        st.markdown("**Modelo do Retriever**")
        
        retriever_options = [
            "gpt-5-mini-2025-08-07",
            "gpt-5-2025-08-07",
            "gpt-5-pro-2025-10-06",
        ]
        
        if 'retriever_model' not in st.session_state:
            st.session_state.retriever_model = "gpt-5-mini-2025-08-07"
        
        try:
            retriever_default_index = retriever_options.index(st.session_state.retriever_model)
        except ValueError:
            retriever_default_index = 0
        
        retriever_model = st.selectbox(
            "Modelo do Retriever",
            options=retriever_options,
            index=retriever_default_index,
            help="Modelo usado pelo retriever (LLM interno que seleciona documentos e headings)",
            key='select_retriever'
        )
        st.session_state.retriever_model = retriever_model
        
        st.markdown("---")
        st.markdown("**Máx. chamadas de ferramentas**")
        st.caption("Controla quantas vezes o retriever pode ser chamado POR PERGUNTA (soft limit, reseta a cada turno)")
        
        if 'max_tool_calls' not in st.session_state:
            st.session_state.max_tool_calls = 3
        
        max_tool_calls = st.slider(
            "Max_tool_calls",
            min_value=0,
            max_value=5,
            value=st.session_state.max_tool_calls,
            help="0 = sem consultas ao retriever; >0 permite consultas ao retriever (soft limit)",
            key='slider_max_tools'
        )
        st.session_state.max_tool_calls = max_tool_calls
        
        st.markdown("---")
        st.markdown("**Agent Seletor**")
        st.caption("Filtra e memoriza chunks relevantes ao escopo após cada consulta ao retriever")
        
        # Usar os mesmos modelos disponíveis para o Analista_AI e Retriever
        seletor_model_options = [
            "gpt-5-mini-2025-08-07",  # Default e mais eficiente
            "gpt-5-2025-08-07",
            "gpt-5-pro-2025-10-06",
            "o3-2025-04-16",
            "o3-pro-2025-06-10",
        ]
        
        if 'seletor_model' not in st.session_state:
            st.session_state.seletor_model = "gpt-5-mini-2025-08-07"
        
        try:
            seletor_default_index = seletor_model_options.index(st.session_state.seletor_model)
        except ValueError:
            seletor_default_index = 0
        
        seletor_model = st.selectbox(
            "Modelo do Seletor",
            options=seletor_model_options,
            index=seletor_default_index,
            help="Modelo usado pelo Agent Seletor para filtrar chunks relevantes",
            key='select_seletor'
        )
        st.session_state.seletor_model = seletor_model
        
        if 'seletor_reasoning_effort' not in st.session_state:
            st.session_state.seletor_reasoning_effort = 'medium'
        
        seletor_reasoning_effort = st.selectbox(
            "Reasoning effort (Seletor)",
            options=["low", "medium", "high"],
            index=["low", "medium", "high"].index(st.session_state.seletor_reasoning_effort),
            help="Esforço de raciocínio do Agent Seletor",
            key='select_seletor_reasoning'
        )
        st.session_state.seletor_reasoning_effort = seletor_reasoning_effort
        
        st.markdown("---")
        
        # Botão Limpar conversa com confirmação
        if st.button("🗑️ Limpar conversa", use_container_width=True):
            st.session_state.confirmar_limpar = True
        
        if st.session_state.get('confirmar_limpar', False):
            st.warning("⚠️ Deseja realmente limpar a conversa atual?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sim", use_container_width=True, key='btn_limpar_sim'):
                    # Salva antes de limpar
                    if st.session_state.memory.get_ui_messages() or st.session_state.escopo.strip():
                        _salvar_conversa_atual()
                    
                    # Limpa estado (MANTÉM escopo atual)
                    escopo_atual = st.session_state.escopo  # Preserva escopo
                    st.session_state.memory = ConversationMemory()
                    st.session_state.logger = ConversationLogger()
                    st.session_state.retriever_events = []
                    st.session_state.escopo = escopo_atual  # Restaura escopo
                    st.session_state.tokens_history = []
                    st.session_state.conversa_atual = ""
                    st.session_state.confirmar_limpar = False
                    
                    # Força atualização do widget (campo volta a ficar enabled)
                    if "escopo_widget_key" in st.session_state:
                        st.session_state.escopo_widget_key += 1
                    
                    st.rerun()
            
            with col2:
                if st.button("❌ Não", use_container_width=True, key='btn_limpar_nao'):
                    st.session_state.confirmar_limpar = False
                    st.rerun()


# Cabeçalho com logo + título
try:
    logo_path = PROJECT_ROOT / "Logo_XP.png"
    with open(logo_path, "rb") as _lf:
        _logo_b64 = base64.b64encode(_lf.read()).decode("utf-8")
    st.html(
        f"""
        <div style='display:flex; align-items:center; gap:12px;'>
            <img src='data:image/png;base64,{_logo_b64}' alt='Logo' style='height:42px;'>
            <h1 style='margin:0;'>Analista_AI</h1>
        </div>
        """
    )
except Exception:
    st.title("Analista_AI")
st.markdown("<div style='font-size:1.05rem;'>Arquitetura com 1 LLM em loop (multi-hop nativo)</div>", unsafe_allow_html=True)


def _render_event_card(event: Dict[str, Any], container):
    """Renderiza um card de evento com progresso visual."""
    stage = event.get("stage")
    icon = event.get("icon", "")
    label = event.get("label", stage)
    ts = event.get("ts", 0)
    iteration = event.get("iteration")

    # Badge (quando aplicável)
    iter_badge = f" `[Iter {iteration}]`" if iteration is not None else ""

    # Tempo hh:mm:ss
    try:
        h = int(ts) // 3600
        m = (int(ts) % 3600) // 60
        s = int(ts) % 60
        hms = f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        hms = "00:00:00"

    if stage == "direct_response":
        container.info(f"{icon} **{label}** — {hms}")

    elif stage == "iteration_start":
        container.info(f"{icon} Iteração {iteration} iniciada: {hms}")

    elif stage == "iteration_end":
        tokens = event.get("tokens", {})
        container.success(f"{icon} Iteração {iteration} concluída: {hms}")
        container.caption(
            f"Tokens: {tokens.get('total', 0)} (in:{tokens.get('input',0)} out:{tokens.get('output',0)} reasoning:{tokens.get('reasoning',0)})"
        )

    elif stage == "tool_call":
        query = event.get("query", "")
        container.warning(f"{icon} **{label}**{iter_badge} — {hms}")
        with container.container(border=True):
            st.code(query[:500] + ("..." if len(query) > 500 else ""), language="text")

    elif stage == "tool_result":
        retriever_details = event.get("retriever_details", {})
        num_chunks = event.get("num_chunks", 0)
        elapsed = event.get("elapsed", 0)

        container.success(f"{icon} **{label}**{iter_badge} — {hms} (⏱️ {elapsed:.1f}s)")

        with container.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chunks", num_chunks)
                semantic = retriever_details.get("use_semantic")
                if semantic is not None:
                    st.metric("Busca", "Semântica ✓" if semantic else "Lexical")

            with col2:
                st.metric("k", retriever_details.get("k", "—"))
                filters = retriever_details.get("filters", {})
                if filters:
                    filter_items = []
                    for k, v in filters.items():
                        if v:
                            if isinstance(v, list):
                                filter_items.append(f"{k}: {', '.join(map(str, v))}")
                            else:
                                filter_items.append(f"{k}: {v}")
                    if filter_items:
                        st.caption("**Filtros:**")
                        for item in filter_items:
                            st.caption(f"• {item}")

    elif stage == "final_response":
        container.success(f"{icon} Resposta final gerada: {hms}")

    elif stage == "code_interpreter":
        files = event.get("files", [])
        container.success(f"{icon} **{label}** — {hms}")
        if files:
            container.caption(f"Arquivos: {', '.join(files)}")
    
    elif stage == "seletor_start":
        container.info(f"{icon} **{label}**{iter_badge} — {hms}")
    
    elif stage == "seletor_success":
        chunks_adicionados = event.get("chunks_adicionados", 0)
        chunks_duplicados = event.get("chunks_duplicados", 0)
        container.success(f"{icon} **{label}**{iter_badge} — {hms}")
        container.caption(f"Chunks novos: {chunks_adicionados} | Duplicados ignorados: {chunks_duplicados}")
    
    elif stage == "seletor_error":
        container.error(f"{icon} **{label}**{iter_badge} — {hms}")
    
    elif stage == "seletor_exception":
        container.error(f"{icon} **{label}**{iter_badge} — {hms}")


def _render_retriever_call_detail(retriever_event: Dict[str, Any], call_number: int):
    """Renderiza detalhes completos de uma chamada ao retriever com cards progressivos."""
    import json as _json
    
    iteration = retriever_event.get("iteration", "?")
    query = retriever_event.get("query", "")
    audit = retriever_event.get("audit", {})
    chunks = retriever_event.get("chunks", [])
    num_chunks = retriever_event.get("num_chunks", 0)
    
    # Card principal: cabeçalho da chamada
    st.info(f"📌 **Chamada #{call_number} ao Retriever** (Iteração {iteration})")
    
    # STEP 1: Input
    st.markdown("---")
    st.success("🔹 **Step 1 — Input (Seleção de Documentos)**")
    with st.container(border=True):
        st.caption("**Query recebida:**")
        st.code(audit.get("step1_input", query), language="text")
        step1_elapsed = audit.get("step1_elapsed", 0)
        st.caption(f"⏱️ Tempo: {step1_elapsed:.3f}s")
    
    # STEP 1: Output
    st.success("🔹 **Step 1 — Output (Filtros Decididos)**")
    with st.container(border=True):
        st.caption("**Resposta completa do LLM:**")
        step1_output = audit.get("step1_output", "")
        st.code(step1_output, language="json")
        
        selected_docs = audit.get("selected_docs", {})
        if selected_docs:
            st.caption("**Documentos selecionados:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                tickers = selected_docs.get("ticker", [])
                if tickers:
                    st.metric("Ticker(s)", ", ".join(tickers))
            with col2:
                reports = selected_docs.get("report", [])
                if reports:
                    st.metric("Report(s)", ", ".join(reports))
            with col3:
                periods = selected_docs.get("period", [])
                if periods:
                    st.metric("Period(s)", ", ".join(periods))
    
    # STEP 2: Input
    st.markdown("---")
    st.warning("🔹 **Step 2 — Input (Headings Disponíveis com IDs)**")
    with st.container(border=True):
        step2_input = audit.get("step2_input", {})
        doc_to_headings_with_ids = step2_input.get("doc_to_headings_with_ids", {})
        
        if doc_to_headings_with_ids:
            st.caption(f"**Headings enviados ao LLM (numerados por documento):**")
            st.caption("ℹ️ O LLM recebe IDs numéricos e deve retornar apenas os IDs desejados")
            
            for doc_key, headings_dict in doc_to_headings_with_ids.items():
                num_headings = len(headings_dict)
                with st.expander(f"📄 {doc_key} ({num_headings} headings)"):
                    # Ordenar por ID numérico
                    sorted_items = sorted(headings_dict.items(), key=lambda x: int(x[0]))
                    for heading_id, heading_text in sorted_items:
                        st.caption(f"**ID {heading_id}**: {heading_text}")
        else:
            st.caption("(Nenhum heading disponível)")
        
        step2_elapsed = audit.get("step2_elapsed", 0)
        st.caption(f"⏱️ Tempo: {step2_elapsed:.3f}s")
    
    # STEP 2: Output
    st.warning("🔹 **Step 2 — Output (Estratégia e Filtros Finais)**")
    with st.container(border=True):
        st.caption("**Resposta completa do LLM:**")
        step2_output = audit.get("step2_output", "")
        st.code(step2_output, language="json")
        
        # IDs retornados pelo LLM
        requested_ids = audit.get("step2_requested_ids", [])
        if requested_ids:
            st.caption(f"**🔢 IDs selecionados pelo LLM:** `{requested_ids}`")
        
        col1, col2 = st.columns(2)
        with col1:
            use_semantic = audit.get("use_semantic", False)
            st.metric("Estratégia de Busca", "Semântica ✓" if use_semantic else "Lexical (filtro apenas)")
            
            # Headings validados (após conversão ID → heading)
            validated_headings = audit.get("validated_headings", [])
            if validated_headings:
                st.caption("**✅ Headings validados (IDs convertidos):**")
                st.caption(f"ℹ️ {len(validated_headings)} heading(s) de {len(requested_ids)} ID(s) solicitados")
                for h in validated_headings:
                    st.caption(f"• {h}")
            elif requested_ids:
                st.caption("⚠️ Nenhum heading validado (IDs inválidos)")
        
        with col2:
            semantic_query = audit.get("semantic_query", "")
            if semantic_query:
                st.caption("**Semantic Query:**")
                st.code(semantic_query, language="text")
            
            used_or = audit.get("used_or", False)
            if used_or:
                st.caption("⚠️ Fallback: usado `$or` em vez de `$in`")
        
        where_final = audit.get("where_final", {})
        if where_final:
            with st.expander("🔍 Filtros finais aplicados (where_final)"):
                st.json(where_final)
    
    # Chunks Retornados
    st.markdown("---")
    st.success(f"🔹 **Chunks Retornados** ({num_chunks} chunk(s))")
    
    if chunks:
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            page_content = chunk.get("page_content", "")
            score = chunk.get("score")
            
            # Header do chunk
            ticker_v = metadata.get("ticker", "—")
            report_v = metadata.get("report", "—")
            period_v = metadata.get("period", "—")
            page_no_v = metadata.get("page_no", "—")
            headings_enriched_v = metadata.get("headings_enriched", "—")
            chunk_id_v = metadata.get("chunk_id", "—")
            
            score_str = f"{score:.4f}" if isinstance(score, (int, float)) else "N/A"
            
            with st.expander(
                f"**Chunk {i}/{num_chunks}** • {ticker_v} | {report_v} | {period_v} | p.{page_no_v} | score: {score_str}"
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.caption(f"**Heading:** {headings_enriched_v}")
                    st.caption(f"**Chunk ID:** {chunk_id_v}")
                with col2:
                    st.caption(f"**Page:** {page_no_v}")
                    st.caption(f"**Score:** {score_str}")
                
                st.markdown("**Conteúdo completo:**")
                st.code(page_content, language="text")
    else:
        st.caption("(Nenhum chunk retornado)")
    
    # Resumo da Chamada
    st.markdown("---")
    st.info("🔹 **Resumo da Chamada**")
    with st.container(border=True):
        total_elapsed = audit.get("elapsed_seconds", 0)
        elapsed_hms = audit.get("elapsed_hms", "00:00:00")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tempo Total", elapsed_hms)
        with col2:
            st.metric("Chunks Retornados", num_chunks)
        with col3:
            strategy = "Semântica" if audit.get("use_semantic") else "Lexical"
            st.metric("Estratégia", strategy)


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Analista AI", "Prompts", "Retriever Debug", "Chunks Memorizados", "Tokens"])

with tab1:
    # Input de Escopo e Objetivo da Análise (dentro da tab1, ANTES do chat)
    st.markdown("---")
    st.markdown('<h3 style="font-size: 1.5rem; font-weight: 600;">Escopo e Objetivo da Análise</h3>', unsafe_allow_html=True)
    
    # Campo desabilitado se conversa já iniciou (há mensagens)
    conversa_iniciada = bool(st.session_state.memory.get_ui_messages())
    
    # Inicializa widget_key se não existir (usado para forçar reset do widget)
    if "escopo_widget_key" not in st.session_state:
        st.session_state.escopo_widget_key = 0
    
    escopo_input = st.text_area(
        label="**Defina o escopo e objetivo da sua análise**",
        value=st.session_state.escopo,
        height=120,
        placeholder="Ex: Análise da rentabilidade da MULT3 no 2º trimestre de 2025, com foco em EBITDA, margens e comparação com períodos anteriores.",
        help="Este escopo norteará todas as buscas e análises do assistente.",
        key=f"escopo_input_{st.session_state.escopo_widget_key}",
        label_visibility="visible",
        disabled=conversa_iniciada
    )
    
    # Atualiza session_state quando houver mudança (apenas se não estiver desabilitado)
    if not conversa_iniciada and escopo_input != st.session_state.escopo:
        st.session_state.escopo = escopo_input
    
    st.markdown("---")
    # Áreas fixas para conteúdo acima do chat_input
    history_area = st.container()
    run_area = st.container()
    answer_placeholder = st.empty()

    # Histórico de chat (UI) fica acima
    with history_area:
        for m in st.session_state.memory.get_ui_messages():
            with st.chat_message(m["role"]):
                st.markdown(_escape_md_preserving_bullets(m["content"]))

    # Chat input sempre no final da aba
    prompt = st.chat_input("Pergunte em PT-BR")
    
    # Validação: bloqueia início de conversa sem escopo
    if prompt and not st.session_state.escopo.strip():
        st.error("⚠️ Por favor, preencha o campo 'Escopo e Objetivo da Análise' antes de iniciar a conversa.")
        st.stop()
    
    if prompt:
        with run_area:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                progress_area = st.container()
            progress_placeholders: List[Any] = []
            progress_lock = Lock()
            status_ph = st.empty()
            start_ts = _time.perf_counter()
            result_holder: Dict[str, Any] = {}
            events_holder: List[Dict[str, Any]] = []
            current_iteration_holder = {"value": 0}

            local_memory = st.session_state.memory
            local_logger = st.session_state.logger
            local_model = MODEL_CHOICES.get(model_key, DEFAULT_MODEL)
            local_reasoning = reasoning_effort
            local_retriever_model = retriever_model

            # Define escopo no memory antes de processar
            local_memory.set_escopo(st.session_state.escopo)

            def event_callback(event: Dict[str, Any]):
                with progress_lock:
                    events_holder.append(event)
                    if event.get("stage") == "iteration_start":
                        current_iteration_holder["value"] = event.get("iteration", 0)

            def _worker():
                try:
                    result_holder["result"] = run_agent_turn_single_llm(
                        memory=local_memory,
                        question=prompt,
                        logger=local_logger,
                        model=local_model,
                        reasoning_effort=local_reasoning,
                        retriever_model=local_retriever_model,
                        max_tool_calls=max_tool_calls,
                        event_callback=event_callback,
                        anotador_model=seletor_model,
                        anotador_reasoning_effort=seletor_reasoning_effort,
                    )
                except Exception as e:
                    result_holder["error"] = str(e)

            # Limpa resposta anterior enquanto processa nova
            answer_placeholder.empty()
            th = Thread(target=_worker, daemon=True)
            th.start()

            last_rendered_count = 0
            while th.is_alive():
                elapsed = int(_time.perf_counter() - start_ts)
                h = elapsed // 3600
                m = (elapsed % 3600) // 60
                s = elapsed % 60
                with progress_lock:
                    current_iter = current_iteration_holder["value"]
                if max_tool_calls == 0:
                    status_ph.info(f"⏱️ Processando (síntese sem retriever): {h:02d}:{m:02d}:{s:02d}")
                else:
                    status_ph.info(f"⏱️ Processando: {h:02d}:{m:02d}:{s:02d} | 🔄 Iteração: {current_iter}")
                with progress_lock:
                    current_count = len(events_holder)
                if current_count > last_rendered_count:
                    with progress_area:
                        for i in range(last_rendered_count, current_count):
                            with progress_lock:
                                event = events_holder[i]
                            ph = st.empty()
                            progress_placeholders.append(ph)
                            with ph.container():
                                _render_event_card(event, st)
                                if i < current_count - 1 or th.is_alive():
                                    st.markdown("<div style='text-align: center; color: #888; margin: 0.5rem 0;'>↓</div>", unsafe_allow_html=True)
                    last_rendered_count = current_count
                _time.sleep(0.2)

            th.join()
            status_ph.empty()
            with progress_lock:
                final_count = len(events_holder)
            if final_count > last_rendered_count:
                with progress_area:
                    for i in range(last_rendered_count, final_count):
                        with progress_lock:
                            event = events_holder[i]
                        ph = st.empty()
                        with ph.container():
                            _render_event_card(event, st)
            if result_holder.get("error"):
                st.error(f"Falha ao gerar resposta: {result_holder['error']}")
                st.stop()
            result = result_holder.get("result", {})
            
            # Captura audits do retriever para a aba de debug
            retriever_audits = result.get("retriever_audits", [])
            if retriever_audits:
                st.session_state.retriever_events.extend(retriever_audits)
            
            # NOVO: Captura dados de tokens para a aba de Tokens
            tokens_tracking = result.get("tokens_tracking")
            if tokens_tracking:
                from datetime import datetime
                resumo_total = tokens_tracking.get("resumo_total", {})
                resumo_componentes = tokens_tracking.get("resumo_componentes", {})
                tabela_detalhada = tokens_tracking.get("tabela_detalhada", [])
                resumo_retriever_detalhado = tokens_tracking.get("resumo_retriever_detalhado", {})
                
                # Monta entrada do histórico de tokens
                turno_entry = {
                    "turno_id": len(st.session_state.tokens_history) + 1,
                    "timestamp": datetime.now(),
                    "question": prompt,
                    "iteration_count": result.get("iteration_count", 0),
                    "total_tokens": resumo_total.get("total_tokens", 0),
                    "total_custo": resumo_total.get("total_custo", 0.0),
                    "total_chamadas": resumo_total.get("total_chamadas", 0),
                    "elapsed_seconds": resumo_total.get("total_elapsed_seconds", 0.0),
                    "componentes": resumo_componentes,
                    "tabela_detalhada": tabela_detalhada,
                    "resumo_retriever_detalhado": resumo_retriever_detalhado
                }
                st.session_state.tokens_history.append(turno_entry)
            
            # ✅ MOSTRA RESPOSTA IMEDIATAMENTE (antes de aguardar threads)
            with answer_placeholder.container():
                st.markdown("---")
                st.markdown("### ✨ Resposta")
                buffer = result.get("answer", "")
                st.markdown(_escape_md_preserving_bullets(buffer))
            
            # ✅ AGORA aguarda threads de seleção terminarem (em background, não bloqueia UI)
            seletor_threads = result.get("seletor_threads", [])
            if seletor_threads:
                with st.spinner("Finalizando seleções em background..."):
                    for thread in seletor_threads:
                        thread.join()  # Aguarda thread terminar
            
            # 🔄 AUTO-SAVE: Salva conversa automaticamente após cada resposta
            _salvar_conversa_atual()

with tab2:
    st.subheader("Prompts do Analista_AI")
    st.caption("Referência dos prompts usados pelo app")
    with st.expander("System prompt (Single LLM)", expanded=True):
        st.code(SYSTEM_PROMPT, language="markdown")
        st.download_button(
            label="Baixar system_prompt.txt",
            data=SYSTEM_PROMPT,
            file_name="system_prompt.txt",
            mime="text/plain",
        )
    with st.expander("Escopo e Objetivo da Análise (SystemMessage)", expanded=True):
        # Obtém escopo atual do memory
        escopo_atual = st.session_state.memory.get_escopo() if hasattr(st.session_state, 'memory') else ""
        
        if escopo_atual and escopo_atual.strip():
            escopo_msg = format_escopo_message(escopo_atual)
            st.code(escopo_msg.content, language="markdown")
            st.download_button(
                label="Baixar escopo_message.txt",
                data=escopo_msg.content,
                file_name="escopo_message.txt",
                mime="text/plain",
            )
        else:
            st.info("📝 Escopo ainda não foi definido. Preencha o campo na aba 'Analista AI' para iniciar uma conversa.")
    with st.expander("Mensagem de limite de ferramentas (retriever)", expanded=True):
        st.code(LIMIT_RETRIEVER_REACHED_MSG, language="markdown")
        st.download_button(
            label="Baixar limit_retriever_message.txt",
            data=LIMIT_RETRIEVER_REACHED_MSG,
            file_name="limit_retriever_message.txt",
            mime="text/plain",
        )
    with st.expander("System prompt do Agent Seletor", expanded=True):
        st.code(SYSTEM_PROMPT_SELETOR, language="markdown")
        st.download_button(
            label="Baixar seletor_system_prompt.txt",
            data=SYSTEM_PROMPT_SELETOR,
            file_name="seletor_system_prompt.txt",
            mime="text/plain",
        )
    with st.expander("Retriever — Step 1 (seleção de documentos)", expanded=True):
        st.code(RETRIEVER_STEP1_PROMPT, language="markdown")
        st.download_button(
            label="Baixar retriever_step1_prompt.txt",
            data=RETRIEVER_STEP1_PROMPT,
            file_name="retriever_step1_prompt.txt",
            mime="text/plain",
        )
    with st.expander("Retriever — Step 2 (headings + estratégia de busca)", expanded=True):
        st.code(RETRIEVER_STEP2_PROMPT, language="markdown")
        st.download_button(
            label="Baixar retriever_step2_prompt.txt",
            data=RETRIEVER_STEP2_PROMPT,
            file_name="retriever_step2_prompt.txt",
            mime="text/plain",
        )

with tab3:
    st.subheader("Retriever Debug — Histórico de Chamadas")
    st.caption("Visualização detalhada de todas as chamadas ao retriever nesta conversa")
    
    retriever_events = st.session_state.retriever_events
    
    if not retriever_events:
        st.info("👋 Nenhuma chamada ao retriever foi realizada ainda. Faça uma pergunta na aba 'Analista AI' para ver o debug do retriever aqui.")
    else:
        st.success(f"📊 Total de chamadas ao retriever: **{len(retriever_events)}**")
        st.markdown("---")
        
        # Renderiza cada chamada ao retriever
        for idx, retriever_event in enumerate(retriever_events, 1):
            _render_retriever_call_detail(retriever_event, idx)
            
            # Separador entre chamadas (exceto última)
            if idx < len(retriever_events):
                st.markdown("<div style='text-align: center; color: #888; margin: 2rem 0;'>⬇️ ⬇️ ⬇️</div>", unsafe_allow_html=True)

with tab4:
    st.subheader("📝 Chunks Relevantes Memorizados no Contexto")
    st.caption("Chunks filtrados e memorizados pelo Agent Seletor, relevantes ao Escopo e Objetivo da Análise")
    
    # Obtém o estado dos chunks do memory
    chunks_state = st.session_state.memory.get_chunks_relevantes()
    
    if not chunks_state.tem_chunks():
        st.info("👋 Nenhum chunk foi memorizado ainda. Os chunks são selecionados automaticamente após cada consulta ao retriever na aba 'Analista AI'.")
    else:
        # Estatísticas
        stats = chunks_state.obter_estatisticas()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", stats.get("total_chunks", 0))
        with col2:
            st.metric("Documentos", stats.get("total_documentos", 0))
        with col3:
            st.metric("Chamadas ao Seletor", stats.get("total_selecoes", 0))
        
        st.markdown("---")
        
        # Diagnóstico do Seletor (histórico de seleções)
        with st.expander("🔍 Diagnóstico do Seletor", expanded=False):
            historico = chunks_state.obter_historico()
            if historico:
                for idx, selecao in enumerate(historico, 1):
                    iteracao = selecao.get("iteracao", "?")
                    status = selecao.get("status", "success")
                    chunks_recebidos = selecao.get("chunks_recebidos", 0)
                    indices_validos = selecao.get("indices_validos", [])
                    indices_invalidos = selecao.get("indices_invalidos", [])
                    chunks_adicionados = selecao.get("chunks_adicionados", 0)
                    chunks_duplicados = selecao.get("chunks_duplicados", [])
                    erro_msg = selecao.get("erro_msg")
                    model = selecao.get("model", "N/A")
                    elapsed = selecao.get("elapsed_seconds", 0.0)
                    
                    # Card da chamada
                    if status == "success":
                        st.success(f"**Chamada #{idx}** — Iteração {iteracao}")
                    elif status == "warning":
                        st.warning(f"**Chamada #{idx}** — Iteração {iteracao}")
                    elif status == "info":
                        st.info(f"**Chamada #{idx}** — Iteração {iteracao}")
                    else:
                        st.error(f"**Chamada #{idx}** — Iteração {iteracao}")
                    
                    with st.container(border=True):
                        st.caption(f"**Status**: {status}")
                        st.caption(f"• Chunks recebidos do retriever: {chunks_recebidos}")
                        st.caption(f"• Índices retornados pelo LLM: {indices_validos + indices_invalidos}")
                        st.caption(f"• Chunks válidos selecionados: {len(indices_validos)}")
                        st.caption(f"• Chunks inválidos (ignorados): {len(indices_invalidos)}")
                        if indices_invalidos:
                            st.caption(f"  └─ Índices inválidos: {indices_invalidos}")
                        if chunks_duplicados:
                            st.caption(f"• Chunks duplicados (ignorados): {len(chunks_duplicados)}")
                            st.caption(f"  └─ IDs: {chunks_duplicados[:3]}{'...' if len(chunks_duplicados) > 3 else ''}")
                        st.caption(f"• Chunks adicionados à lista: {chunks_adicionados}")
                        st.caption(f"• Modelo usado: {model}")
                        st.caption(f"• Tempo de processamento: {elapsed:.2f}s")
                        if erro_msg:
                            st.error(f"**Erro**: {erro_msg}")
                    
                    if idx < len(historico):
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.caption("Nenhum histórico disponível")
        
        st.markdown("---")
        
        # Conteúdo dos chunks (hierárquico)
        st.markdown("### 📄 Chunks Memorizados")
        
        agrupados = chunks_state.obter_chunks_agrupados()
        
        # Renderiza por documento
        for doc_key in sorted(agrupados.keys()):
            doc_info = agrupados[doc_key]
            ticker = doc_info["ticker"]
            report = doc_info["report"]
            period = doc_info["period"]
            
            st.markdown("───────────────────────────────────────────────────────────────────────────")
            st.markdown(f"**{ticker} | {report} | {period}**")
            st.markdown("───────────────────────────────────────────────────────────────────────────")
            
            sections = doc_info["sections"]
            for heading in sorted(sections.keys()):
                st.markdown(f"  **{heading}**")
                st.markdown("")
                
                pages = sections[heading]["pages"]
                for page_no in sorted(pages.keys(), key=lambda x: str(x)):
                    st.markdown(f"    *Página {page_no}*")
                    st.markdown("")
                    
                    chunks_na_pagina = sorted(
                        pages[page_no],
                        key=lambda c: c.get("metadata", {}).get("chunk_id", "")
                    )
                    
                    for chunk in chunks_na_pagina:
                        chunk_id_val = chunk.get("metadata", {}).get("chunk_id", "?")
                        page_content = chunk.get("page_content", "")
                        
                        with st.expander(f"[{chunk_id_val}]", expanded=False):
                            st.code(page_content, language="text")
                        
                st.markdown("")
        
        st.markdown("═══════════════════════════════════════════════════════════════════════════")
        
        # Botão de download (JSON)
        import json as _json
        chunks_list = chunks_state.obter_chunks()
        chunks_json = _json.dumps(chunks_list, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Baixar chunks selecionados (JSON)",
            data=chunks_json,
            file_name="chunks_relevantes.json",
            mime="application/json",
        )

with tab5:
    st.subheader("💰 Uso de Tokens e Custos")
    st.caption("Rastreamento completo de todas as chamadas LLM em cada turno")
    
    tokens_history = st.session_state.get("tokens_history", [])
    
    if not tokens_history:
        st.info("👋 Nenhum dado de tokens disponível ainda. Faça uma pergunta na aba 'Analista AI' para ver as métricas aqui.")
    else:
        # Calcula totais acumulados (toda a conversa)
        total_tokens_geral = sum(t.get("total_tokens", 0) for t in tokens_history)
        total_custo_geral = sum(t.get("total_custo", 0.0) for t in tokens_history)
        total_chamadas_geral = sum(t.get("total_chamadas", 0) for t in tokens_history)
        custo_medio_turno = total_custo_geral / len(tokens_history) if len(tokens_history) > 0 else 0.0
        
        # RESUMO FINANCEIRO CUMULATIVO
        st.markdown("### 💵 Resumo Financeiro (Toda a Conversa)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tokens", formatar_tokens(total_tokens_geral))
        with col2:
            st.metric("Total Custo", formatar_custo(total_custo_geral))
        with col3:
            st.metric("Total Chamadas", f"{total_chamadas_geral} LLMs")
        with col4:
            st.metric("Custo Médio/Turno", formatar_custo(custo_medio_turno))
        
        st.markdown("---")
        st.markdown("### 📊 Histórico de Turnos")
        
        # Renderiza cada turno (mais recente ao final)
        for idx, turno in enumerate(tokens_history):
            turno_id = turno.get("turno_id", idx + 1)
            timestamp = turno.get("timestamp")
            question = turno.get("question", "")
            total_tokens = turno.get("total_tokens", 0)
            total_custo = turno.get("total_custo", 0.0)
            componentes = turno.get("componentes", {})
            tabela_detalhada = turno.get("tabela_detalhada", [])
            resumo_retriever_detalhado = turno.get("resumo_retriever_detalhado", {})
            
            # Formata timestamp
            try:
                ts_str = timestamp.strftime("%d/%m %H:%M:%S")
            except Exception:
                ts_str = "—"
            
            # Trunca pergunta para 60 chars
            question_preview = question[:60] + "..." if len(question) > 60 else question
            
            # Determina se é o último turno (deve estar expandido)
            is_last = (idx == len(tokens_history) - 1)
            
            # Header do expander
            header = f"**Turno {turno_id}** | {ts_str} | {formatar_tokens(total_tokens)} | {formatar_custo(total_custo)} — {question_preview}"
            
            with st.expander(header, expanded=is_last):
                st.markdown(f"**Pergunta completa:** {question}")
                st.markdown("")
                
                # Componentes do turno
                COMP_ICONS = {
                    "analista": "🤖",
                    "retriever": "🔍",
                    "seletor": "📝"
                }
                COMP_NAMES = {
                    "analista": "Analista_AI",
                    "retriever": "Retriever",
                    "seletor": "Agent Seletor"
                }
                
                for comp_key in ["analista", "retriever", "seletor"]:
                    comp_data = componentes.get(comp_key)
                    if not comp_data:
                        continue
                    
                    icon = COMP_ICONS.get(comp_key, "")
                    name = COMP_NAMES.get(comp_key, comp_key)
                    chamadas = comp_data.get("chamadas", 0)
                    tokens_comp = comp_data.get("tokens", {})
                    custo_comp = comp_data.get("custo", 0.0)
                    elapsed_comp = comp_data.get("elapsed_seconds", 0.0)
                    
                    input_tk = tokens_comp.get("input", 0)
                    output_tk = tokens_comp.get("output", 0)
                    reasoning_tk = tokens_comp.get("reasoning", 0)
                    
                    st.markdown(f"**{icon} {name}** ({chamadas} chamada{'s' if chamadas > 1 else ''})")
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.caption(f"**Tokens**: Input {formatar_tokens(input_tk)} | Output {formatar_tokens(output_tk)} | Reasoning {formatar_tokens(reasoning_tk)}")
                        with col2:
                            st.caption(f"**Custo**: {formatar_custo(custo_comp)}")
                            
                        # Retriever detalhado (Step 1 vs Step 2)
                        if comp_key == "retriever" and resumo_retriever_detalhado:
                            step1 = resumo_retriever_detalhado.get("step1")
                            step2 = resumo_retriever_detalhado.get("step2")
                            
                            if step1 or step2:
                                st.caption("**Detalhamento:**")
                                if step1:
                                    step1_tokens = step1.get("tokens", {})
                                    step1_custo = step1.get("custo", 0.0)
                                    st.caption(f"├─ Step 1: {formatar_tokens(step1_tokens.get('total', 0))} tokens | {formatar_custo(step1_custo)}")
                                if step2:
                                    step2_tokens = step2.get("tokens", {})
                                    step2_custo = step2.get("custo", 0.0)
                                    st.caption(f"└─ Step 2: {formatar_tokens(step2_tokens.get('total', 0))} tokens | {formatar_custo(step2_custo)}")
                    
                    st.markdown("")
                
                # Tabela detalhada (sub-expander)
                if tabela_detalhada:
                    with st.expander(f"🔬 Ver tabela detalhada ({len(tabela_detalhada)} chamadas)", expanded=False):
                        import pandas as pd
                        df_tokens = pd.DataFrame(tabela_detalhada)
                        
                        # Formata colunas numéricas
                        if not df_tokens.empty:
                            st.dataframe(
                                df_tokens,
                                column_config={
                                    "componente": st.column_config.TextColumn("Componente", width="medium"),
                                    "iteracao": st.column_config.TextColumn("Iter", width="small"),
                                    "model": st.column_config.TextColumn("Modelo", width="medium"),
                                    "input_tokens": st.column_config.NumberColumn("Input", format="%d"),
                                    "output_tokens": st.column_config.NumberColumn("Output", format="%d"),
                                    "reasoning_tokens": st.column_config.NumberColumn("Reasoning", format="%d"),
                                    "total_tokens": st.column_config.NumberColumn("Total", format="%d"),
                                    "custo": st.column_config.NumberColumn("Custo", format="$%.2f"),
                                    "elapsed_seconds": st.column_config.NumberColumn("Tempo (s)", format="%.2f")
                                },
                                hide_index=True,
                                width='stretch'
                            )
        
        # Botão de download CSV global
        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        
        # Gera CSV flat (todas as chamadas de todos os turnos)
        import pandas as pd
        from datetime import datetime as dt
        
        all_calls = []
        for turno in tokens_history:
            turno_id = turno.get("turno_id", 0)
            timestamp = turno.get("timestamp")
            ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "—"
            question = turno.get("question", "")
            tabela = turno.get("tabela_detalhada", [])
            
            for call in tabela:
                all_calls.append({
                    "turno": turno_id,
                    "timestamp": ts_str,
                    "turno_question": question,
                    "componente": call.get("componente", ""),
                    "iteracao": call.get("iteracao", ""),
                    "model": call.get("model", ""),
                    "input_tokens": call.get("input_tokens", 0),
                    "output_tokens": call.get("output_tokens", 0),
                    "reasoning_tokens": call.get("reasoning_tokens", 0),
                    "total_tokens": call.get("total_tokens", 0),
                    "custo": call.get("custo", 0.0),
                    "tempo_segundos": call.get("elapsed_seconds", 0.0)
                })
        
        if all_calls:
            df_export = pd.DataFrame(all_calls)
            csv_data = df_export.to_csv(index=False)
            
            st.download_button(
                label="📥 Baixar todos os dados de tokens (CSV)",
                data=csv_data,
                file_name=f"tokens_usage_{dt.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


