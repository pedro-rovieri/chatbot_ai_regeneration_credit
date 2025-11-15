#!/usr/bin/env python3
"""
Agente Finance_AI (PT-BR) com 1 LLM multi-hop, Agent Seletor e memória de chunks relevantes.

Arquitetura:
- 1 LLM em loop (multi-hop nativo): permite múltiplas consultas ao retriever antes de responder.
- Agent Seletor: filtra e memoriza chunks relevantes ao escopo após cada consulta ao retriever.
- Retriever RAG: dados factuais (DF, Release, Planilha) com k=40 chunks por consulta.
- Code Interpreter: disponível para cálculos e formatação de dados.

Runner único:
- run_agent_turn_single_llm(): runner principal usado por CLI e Streamlit (main_app.py)
  * Multi-hop nativo (múltiplas iterações antes de responder)
  * Agent Seletor automático para memorização de chunks
  * Tracking completo de tokens por componente
  * Timeline de eventos em tempo real

Escopo e Objetivo da Análise:
- Definido no início da conversa (obrigatório)
- Usado para direcionar buscas e análises em toda a conversa
- Contexto passado ao Agent Seletor para filtragem de chunks

CLI (main()):
- Prompt inicial: Escopo e Objetivo da Análise
- Seleção de modelo por mensagem: "N | sua pergunta" (1=o3, 2=o3-pro, 3=gpt-5)
- Configurações via argparse:
  --max-tool-calls      : Limite soft de chamadas ao retriever (padrão: 3)
  --retriever-model     : Modelo do retriever (padrão: gpt-5-mini)
  --seletor-model       : Modelo do Agent Seletor (padrão: gpt-5-mini)
  --reasoning-effort    : Esforço de raciocínio Analista (low|medium|high)
  --seletor-reasoning   : Esforço de raciocínio Seletor (low|medium|high)

Memória conversacional:
- Histórico dual: LLM (com prefixos de tool memory) e UI (limpa)
- Chunks relevantes memorizados via ChunksRelevantesState (deduplicação automática)
- Persistência: logs/conversations/*.jsonl (mensagens + metadados)

Observabilidade:
- Timeline de eventos: iterações, tool calls, seletor
- Tracking de tokens: Analista, Retriever (Step1/2), Seletor
- Audits do retriever: logs/retriever_audit.jsonl
- LangSmith: compatível (via LANGSMITH_* no .env)

Métricas CLI:
- Tempo total, tokens, iterações, chamadas LLM
- Custo estimado (quando disponível)
- Chunks memorizados (total e documentos)

Uso:
python scripts/finance_ai.py
python scripts/finance_ai.py --max-tool-calls 5 --retriever-model gpt-5-2025-08-07

Notas técnicas:
- Tool: consultar_vector_store_retriever (k=40 fixo)
- Agent Seletor: executa em threads paralelas (não bloqueia agente)
- Soft limit: SystemMessage quando max_tool_calls é atingido
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
import time
from pydantic import BaseModel, Field
import re
from dataclasses import dataclass, field

# Garante que o pacote de nível do projeto esteja importável antes de importar modules 'scripts.*'
import sys as _sys  # noqa: E402
if str(Path(__file__).resolve().parent.parent) not in _sys.path:
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from scripts.finance_ai_config import (
    PROJECT_ROOT,
    DOWNLOADS_DIR,
    K_TOOL_RESULTS,
    CODE_INTERPRETER_TOOL,
    MODEL_CHOICES,
    DEFAULT_MODEL,
    SYSTEM_PROMPT,
    LIMIT_RETRIEVER_REACHED_MSG,
)
from scripts.finance_ai_logger import ConversationLogger, log_retriever_audit as _log_retriever_audit
from scripts.finance_ai_utils import (
    extract_token_usage as _extract_token_usage,
    content_to_text as _content_to_text,
    fmt_hms as _fmt_hms,
    start_turn as _start_turn,
)
from scripts.finance_ai_ci import (
    extract_output_files as _extract_output_files,
    extract_annotation_files as _extract_annotation_files,
    download_openai_file as _download_openai_file,
    collect_and_download_ci_artifacts as _collect_ci,
)
from scripts.finance_ai_escopo import (
    format_escopo_message,
)
from scripts.finance_ai_chunks_state import ChunksRelevantesState
from scripts.finance_ai_seletor import executar_seletor
from scripts.finance_ai_tokens_tracker import TokensTracker


class ConversationMemory:
    """Gerencia histórico dual: versão para LLM (com prefixos de tool memory) e versão para UI (limpa).
    
    O LLM recebe mensagens com prefixos estruturados indicando quais tools foram usadas,
    permitindo consciência de buscas anteriores sem re-enviar chunks completos.
    
    A UI recebe mensagens limpas para melhor experiência do usuário.
    
    Também gerencia o Escopo e Objetivo da Análise definido pelo usuário e os Chunks Relevantes Memorizados.
    """
    
    def __init__(self):
        self.llm_history: List[Any] = []       # Para LLM (AIMessage/HumanMessage com prefixos)
        self.ui_messages: List[Dict[str, str]] = []  # Para UI (dicts simples sem prefixos)
        self.escopo: str = ""  # Escopo e objetivo da análise (definido pelo usuário)
        self.chunks_state = ChunksRelevantesState()  # Chunks relevantes memorizados
    
    def add_user_message(self, content: str) -> None:
        """Adiciona mensagem do usuário (idêntica em ambos históricos)."""
        self.llm_history.append(HumanMessage(content=content))
        self.ui_messages.append({"role": "user", "content": content})
    
    def add_assistant_message(
        self,
        content: str,
        tools_metadata: Dict[str, Any] | None = None
    ) -> None:
        """Adiciona resposta do assistente.
        
        Args:
            content: Resposta completa e limpa (sem prefixos)
            tools_metadata: Opcional. Estrutura:
                {
                    "retriever": {
                        "query": str,
                        "chunks": List[Dict],
                        "num_chunks": int
                    },
                    "code_interpreter": {
                        "files": List[str]  # nomes dos arquivos gerados
                    }
                }
        """
        # Para UI: versão limpa (sempre sem prefixo)
        self.ui_messages.append({"role": "assistant", "content": content})
        
        # Para LLM: com prefixo se houver tools
        if tools_metadata:
            prefix = self._create_tool_memory_prefix(tools_metadata)
            llm_content = f"{prefix}\n\n{content}"
        else:
            llm_content = content
        
        self.llm_history.append(AIMessage(content=llm_content))
    
    def _create_tool_memory_prefix(self, tools_metadata: Dict[str, Any]) -> str:
        """Cria prefixo estruturado e legível com metadados de tools usadas."""
        parts = []
        
        # Retriever
        retriever_info = tools_metadata.get("retriever")
        if retriever_info:
            # Nova estrutura: lista de chamadas separadas
            calls = retriever_info.get("calls", [])
            if calls:
                # Processa cada chamada ao retriever separadamente
                for call_data in calls:
                    chunks = call_data.get("chunks", [])
                    num_chunks = call_data.get("num_chunks", len(chunks))
                    
                    # Extrai metadados únicos dos chunks DESTA chamada
                    tickers = set()
                    periods = set()
                    reports = set()
                    pages = set()
                    
                    for chunk in chunks[:10]:  # Analisa primeiros 10 chunks desta chamada
                        md = chunk.get("metadata", {}) or {}
                        if md.get("ticker"):
                            tickers.add(md["ticker"])
                        if md.get("period"):
                            periods.add(md["period"])
                        if md.get("report"):
                            reports.add(md["report"])
                        if md.get("page_no"):
                            pages.add(md["page_no"])
                    
                    ticker_str = ", ".join(sorted(tickers)) if tickers else "—"
                    period_str = ", ".join(sorted(periods)) if periods else "—"
                    report_str = ", ".join(sorted(reports)) if reports else "—"
                    pages_list = sorted(pages)[:5]
                    pages_str = ", ".join(map(str, pages_list))
                    if len(pages) > 5:
                        pages_str += "..."
                    
                    parts.append(
                        f"Consultei Retriever: {ticker_str} {report_str} {period_str} "
                        f"({num_chunks} chunks, páginas {pages_str})"
                    )
            else:
                # Estrutura antiga (compatibilidade): chunks e num_chunks diretos
                chunks = retriever_info.get("chunks", [])
                num_chunks = retriever_info.get("num_chunks", len(chunks))
                
                # Extrai metadados únicos dos chunks
                tickers = set()
                periods = set()
                reports = set()
                pages = set()
                
                for chunk in chunks[:10]:  # Analisa primeiros 10 chunks
                    md = chunk.get("metadata", {}) or {}
                    if md.get("ticker"):
                        tickers.add(md["ticker"])
                    if md.get("period"):
                        periods.add(md["period"])
                    if md.get("report"):
                        reports.add(md["report"])
                    if md.get("page_no"):
                        pages.add(md["page_no"])
                
                ticker_str = ", ".join(sorted(tickers)) if tickers else "—"
                period_str = ", ".join(sorted(periods)) if periods else "—"
                report_str = ", ".join(sorted(reports)) if reports else "—"
                pages_list = sorted(pages)[:5]
                pages_str = ", ".join(map(str, pages_list))
                if len(pages) > 5:
                    pages_str += "..."
                
                parts.append(
                    f"Consultei Retriever: {ticker_str} {report_str} {period_str} "
                    f"({num_chunks} chunks, páginas {pages_str})"
                )
        
        # Code Interpreter
        ci_info = tools_metadata.get("code_interpreter")
        if ci_info:
            files = ci_info.get("files", [])
            if files:
                files_str = ", ".join(files)
                parts.append(f"Gerei arquivos: {files_str}")
        
        if parts:
            return f"[{' | '.join(parts)}]"
        return ""
    
    def get_llm_history(self) -> List[Any]:
        """Retorna histórico para enviar ao LLM (AIMessage/HumanMessage, com prefixos)."""
        return self.llm_history
    
    def get_ui_messages(self) -> List[Dict[str, str]]:
        """Retorna mensagens para renderizar na UI (dicts simples, sem prefixos)."""
        return self.ui_messages
    
    def set_escopo(self, escopo: str) -> None:
        """Define o escopo e objetivo da análise.
        
        Args:
            escopo: Texto do escopo/objetivo definido pelo usuário
        """
        self.escopo = escopo if escopo else ""
    
    def get_escopo(self) -> str:
        """Retorna o escopo e objetivo da análise atual.
        
        Returns:
            str: Texto do escopo (ou string vazia se não definido)
        """
        return self.escopo
    
    def get_chunks_relevantes(self) -> ChunksRelevantesState:
        """Retorna o estado dos chunks relevantes memorizados.
        
        Returns:
            ChunksRelevantesState: Objeto gerenciador dos chunks relevantes
        """
        return self.chunks_state
    
    def clear(self) -> None:
        """Limpa ambos os históricos, reseta o escopo e limpa os chunks memorizados."""
        self.llm_history = []
        self.ui_messages = []
        self.escopo = ""
        self.chunks_state.limpar()


def _retriever_query(query: str, k: int, retriever_model: str | None = None) -> Dict[str, Any]:
    """Consulta o retriever (import tardio) para evitar custos de import no cold start."""
    from scripts.consultar_vector_store_retriever import retriever_query  # type: ignore
    return retriever_query(query_nl=query, k=k, debug=False, retriever_model=retriever_model)


class RetrieverArgs(BaseModel):
    """Schema Pydantic para a tool do retriever (campo único: query)."""
    query: str = Field(..., description="Pergunta em linguagem natural (PT-BR) que descreve o que deve ser buscado nas DFs, Releases e/ou Planilhas.")


@tool("consultar_vector_store_retriever", args_schema=RetrieverArgs)
def consultar_vector_store_retriever_tool(args: RetrieverArgs) -> str:
    """Busca chunks nos documentos (DFs, Releases e Planilhas) baseado na consulta.

    Argumentos:
    - query: Pergunta em linguagem natural. Deve ser claro e específico sobre os tickers, datas, tipos de documentos e informações desejadas.

    Política: retorna até 40 resultados fixos.

    Retorno (string JSON): lista de objetos { page_content, metadata, score } (até 40 itens).
    """
    # Opcionalmente, usar modelo de retriever passado via RunnableConfig.metadata["retriever_model"]
    # Quando não informado, o retriever usará o padrão (gpt-5-2025-08-07)
    retriever_model: str | None = None
    try:
        from langchain_core.runnables import get_current_config  # type: ignore
        cfg = get_current_config()
        if isinstance(cfg, dict):
            meta = cfg.get("metadata") or {}
            rm = meta.get("retriever_model")
            if isinstance(rm, str):
                retriever_model = rm
    except Exception:
        pass

    result = _retriever_query(query=args.query, k=K_TOOL_RESULTS, retriever_model=retriever_model)
    chunks = result.get("chunks", [])
    audit = result.get("audit", {})
    # Log local de auditoria
    _log_retriever_audit({"query": args.query, "k": K_TOOL_RESULTS, "audit": audit})
    # Retornar somente os chunks ao LLM
    return json.dumps(chunks, ensure_ascii=False)


def build_llm(model: str | None = None, reasoning_effort: str = "high") -> ChatOpenAI:
    """Cria o ChatOpenAI com esforço de raciocínio configurável."""
    return ChatOpenAI(
        model=(model or DEFAULT_MODEL),
        reasoning={"effort": reasoning_effort},
        output_version="responses/v1",
        use_responses_api=True,
    )


@dataclass
class TurnState:
    """Estado de um turno: timeline, eventos, métricas e metadados."""
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    tools_events: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    tools_metadata: Dict[str, Any] = field(default_factory=dict)


def _call_retriever_and_log(
    query: str,
    base_config: RunnableConfig,
    logger: ConversationLogger,
    timeline: List[Dict[str, Any]],
    tools_events: List[Dict[str, Any]],
    label: str,
    iteration: int | None = None,
    t0: float | None = None,
) -> tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """Executa o retriever, registra timeline/logger e retorna (chunks, audit completo, métricas)."""
    import time as _time
    from scripts.consultar_vector_store_retriever import retriever_query as _rq  # type: ignore

    evt_tool_call = {
        "stage": "tool_call",
        "ts": (_time.perf_counter() - t0) if (t0 is not None) else _time.perf_counter(),
        "tool": "retriever",
        "label": label,
        "icon": "🔧",
        "query": query,
    }
    if iteration is not None:
        evt_tool_call["iteration"] = iteration
    timeline.append(evt_tool_call)

    retriever_config: RunnableConfig = {
        **base_config,
        "run_name": "retriever_query",
        "tags": [*(base_config.get("tags", []) if isinstance(base_config, dict) else []), "retriever"],
        "metadata": {**(base_config.get("metadata", {}) if isinstance(base_config, dict) else {})},
    }

    t0 = _time.perf_counter()
    tool_dict = _rq(
        query_nl=query,
        k=K_TOOL_RESULTS,
        debug=False,
        config=retriever_config,
        retriever_model=(retriever_config.get("metadata", {}) or {}).get("retriever_model"),
    )
    t1 = _time.perf_counter()
    chunks_list = tool_dict.get("chunks", [])
    audit = tool_dict.get("audit", {}) or {}

    # Auditoria persistente local (padronização com a tool)
    try:
        _log_retriever_audit({"query": query, "k": K_TOOL_RESULTS, "audit": audit})
    except Exception:
        pass

    evt_tool_result = {
        "stage": "tool_result",
        "ts": (_time.perf_counter() - t0) if (t0 is not None) else _time.perf_counter(),
        "tool": "retriever",
        "label": f"Retriever retorna chunks",
        "icon": "✅",
        "elapsed": (t1 - t0) if (t0 is not None) else (t1),
        "num_chunks": len(chunks_list),
        "retriever_details": {
            "use_semantic": audit.get("use_semantic"),
            "k": K_TOOL_RESULTS,
            "filters": audit.get("selected_docs", {}),
            "validated_headings": audit.get("validated_headings", []),
            "semantic_query": audit.get("semantic_query"),
            "used_or": audit.get("used_or", False),
        },
    }
    if iteration is not None:
        evt_tool_result["iteration"] = iteration
    timeline.append(evt_tool_result)

    retriever_metrics = {
        "use_semantic": audit.get("use_semantic"),
        "k": K_TOOL_RESULTS,
        "elapsed_hms": _fmt_hms((t1 - t0) if (t0 is not None) else t1),
        "num_chunks": (len(chunks_list) if isinstance(chunks_list, list) else 0),
    }
    tools_events.append({"type": "tool_result", "name": "consultar_vector_store_retriever", "data": retriever_metrics})

    logger.tool_event(
        name="consultar_vector_store_retriever",
        args_summary={"query": query, **({"iteration": iteration} if iteration is not None else {})},
        result_summary={"num_chunks": retriever_metrics["num_chunks"]},
    )

    return chunks_list, audit, retriever_metrics


def run_agent_turn_single_llm(
    memory: ConversationMemory,
    question: str,
    logger: ConversationLogger,
    model: str | None = None,
    reasoning_effort: str = "high",
    retriever_model: str | None = None,
    max_tool_calls: int | None = None,
    event_callback: Any = None,
    anotador_model: str | None = None,
    anotador_reasoning_effort: str = "medium"
) -> Dict[str, Any]:
    """Executa um turno com 1 LLM em loop (multi-hop), retornando resposta e métricas.
    
    Args:
        memory: ConversationMemory que gerencia histórico dual
        question: Pergunta do usuário
        logger: ConversationLogger para persistir logs
        model: Modelo a usar (opcional)
        max_tool_calls: Limite "soft" de chamadas ao retriever POR TURNO/PERGUNTA. Se 0, uma
            SystemMessage é adicionada desde o início orientando a síntese final; quando o
            limite é atingido (>0), adiciona-se a mesma instrução. Este contador reseta a cada nova pergunta.
        event_callback: função opcional que recebe eventos de timeline em tempo real
    
    Retorno: {
      answer: str,
      metrics: { per_iteration: [{tokens, elapsed_hms, iteration}], total_elapsed_hms }
      tools: [ eventos sintéticos para UI ]
      timeline: [ eventos de timeline ]
      iteration_count: int (quantas iterações COM TOOL CALLS foram executadas)
      llm_call_count: int (total de chamadas ao LLM)
    }
    """
    import time as _time
    
    
    
    t0 = _time.perf_counter()
    timeline: List[Dict[str, Any]] = []
    
    # Adiciona pergunta do usuário
    memory.add_user_message(question)
    logger.user(question)
    
    # Pega histórico do LLM
    history = memory.get_llm_history()
    
    # Estado padronizado do turno
    state = TurnState()
    timeline = state.timeline
    tools_events = state.tools_events
    metrics = state.metrics
    tools_metadata = state.tools_metadata

    all_chunks: List[Dict[str, Any]] = []  # Acumula chunks de todas as iterações
    retriever_queries: List[str] = []
    retriever_audits: List[Dict[str, Any]] = []  # Acumula audits de todas as chamadas ao retriever
    retriever_calls_metadata: List[Dict[str, Any]] = []  # NOVO: Metadados separados de cada chamada ao retriever
    retriever_call_count = 0  # Contador de chamadas ao retriever
    code_interpreter_called = False
    artifacts: List[Dict[str, Any]] = []
    anotador_threads: List[Any] = []  # Lista para rastrear threads do anotador
    anotador_count = 0  # Contador de threads de anotação criadas
    
    # NOVO: Inicializa TokensTracker para rastreamento de todas as chamadas LLM
    tokens_tracker = TokensTracker()
    
    # Obtém escopo do memory (ou usa padrão se não definido)
    escopo_atual = memory.get_escopo() or ""
    
    # Helper para gerar ordinais em português
    def _ordinal_pt(n: int) -> str:
        """Converte número em ordinal português (1ª, 2ª, 3ª, etc.)"""
        return f"{n}ª"
    
    # Configuração
    config: RunnableConfig = {
        "run_name": "finance_ai_single_llm",
        "tags": ["finance_ai", "retriever", "single_llm"],
        "metadata": {"k": K_TOOL_RESULTS, "retriever_model": retriever_model, "max_tool_calls": max_tool_calls, "escopo": escopo_atual},
    }
    
    # LLM com tools (retriever + CI)
    llm = build_llm(model, reasoning_effort).bind_tools([consultar_vector_store_retriever_tool, CODE_INTERPRETER_TOOL])
    
    # Contexto local do turno (cresce a cada iteração)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        format_escopo_message(escopo_atual),
    ]
    
    # Injeta chunks relevantes memorizados se existirem
    chunks_msg = memory.get_chunks_relevantes().format_for_llm()
    if chunks_msg:
        messages.append(chunks_msg)
    
    # Adiciona histórico
    messages.extend(history)
    # Se max_tool_calls == 0, já orientar síntese (soft limit)
    limit_announced = False
    if isinstance(max_tool_calls, int) and max_tool_calls == 0:
        messages.append(SystemMessage(content=LIMIT_RETRIEVER_REACHED_MSG))
        limit_announced = True
    
    iteration = 0
    metrics_per_iteration: List[Dict[str, Any]] = []
    
    # Contadores
    llm_call_count = 0  # Total de chamadas ao LLM
    tool_call_count = 0  # Chamadas que resultaram em tool execution
    
    # Loop de iterações
    while True:
        iteration += 1
        llm_call_count += 1
        
        evt_iter_start = {
            "stage": "iteration_start",
            "ts": _time.perf_counter() - t0,
            "iteration": iteration,
            "label": f"Iteração {iteration}",
            "icon": "🔄"
        }
        timeline.append(evt_iter_start)
        if event_callback:
            event_callback(evt_iter_start)
        
        # Chama LLM
        t_llm_0 = _time.perf_counter()
        response = llm.invoke(messages, config=config)
        t_llm_1 = _time.perf_counter()
        
        u = _extract_token_usage(response)
        metrics_per_iteration.append({
            "iteration": iteration,
            "tokens": u,
            "elapsed_hms": _fmt_hms(t_llm_1 - t_llm_0)
        })
        
        # NOVO: Registra tokens do Analista no tracker
        tokens_tracker.registrar_chamada(
            componente="analista",
            iteracao=iteration,
            model=(model or DEFAULT_MODEL),
            tokens=u,
            elapsed_seconds=(t_llm_1 - t_llm_0)
        )
        
        evt_iter_end = {
            "stage": "iteration_end",
            "ts": _time.perf_counter() - t0,
            "iteration": iteration,
            "label": f"Iteração {iteration} concluída",
            "icon": "✅",
            "tokens": u
        }
        timeline.append(evt_iter_end)
        if event_callback:
            event_callback(evt_iter_end)
        
        # Detectar CI via blocos code_interpreter_call em content
        try:
            content = getattr(response, "content", None)
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "code_interpreter_call":
                        code_interpreter_called = True
                        break
        except Exception:
            pass
        
        # Verificar tool_calls
        tool_calls = getattr(response, "tool_calls", None) or []
        
        if not tool_calls:
            # Sem tool calls → resposta final
            evt_final = {
                "stage": "final_response",
                "ts": _time.perf_counter() - t0,
                "label": "Resposta final gerada",
                "icon": "🎯",
                "iteration": iteration
            }
            timeline.append(evt_final)
            if event_callback:
                event_callback(evt_final)
            
            # Baixar arquivos se CI foi usado
            if code_interpreter_called:
                try:
                    default_container_id = None
                    content = getattr(response, "content", None)
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "code_interpreter_call":
                                default_container_id = block.get("container_id")
                                if default_container_id:
                                    break
                    
                    out_files = _extract_output_files(response)
                    ann_files = _extract_annotation_files(response)
                    
                    merged: Dict[str, Dict[str, str]] = {}
                    for f in out_files:
                        key = f"{default_container_id}:{f['file_id']}"
                        merged[key] = {"container_id": default_container_id, "file_id": f["file_id"], "display_name": f["display_name"]}
                    for f in ann_files:
                        key = f"{f.get('container_id')}:{f['file_id']}"
                        merged[key] = {"container_id": f.get("container_id") or default_container_id, "file_id": f["file_id"], "display_name": f["display_name"]}
                    
                    files_to_download = list(merged.values())
                    if files_to_download:
                        from datetime import datetime
                        ts_dir = DOWNLOADS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
                        for of in files_to_download:
                            cid = of.get("container_id")
                            fid = of.get("file_id")
                            if cid and fid:
                                info = _download_openai_file(cid, fid, ts_dir)
                                if "path" in info:
                                    artifacts.append(info)
                                else:
                                    artifacts.append({"error": info.get("error"), "file_id": fid, "container_id": cid})
                except Exception as e:
                    artifacts.append({"error": f"Exceção ao processar arquivos: {str(e)}", "file_id": "unknown"})
                
                if artifacts:
                    file_names = [art.get("name") for art in artifacts if "path" in art]
                    tools_metadata["code_interpreter"] = {"files": file_names}
                    
                    evt_ci = {
                        "stage": "code_interpreter",
                        "ts": _time.perf_counter() - t0,
                        "label": "Code Interpreter executado",
                        "icon": "🧮",
                        "files": file_names
                    }
                    timeline.append(evt_ci)
                    if event_callback:
                        event_callback(evt_ci)
            
            answer = _content_to_text(getattr(response, "content", response))
            
            # Captura metadados do retriever se foi usado
            if retriever_calls_metadata:
                # NOVO: Passa lista de chamadas separadas em vez de dict agregado
                tools_metadata["retriever"] = {
                    "calls": retriever_calls_metadata,  # Lista de chamadas individuais
                    "total_chunks": len(all_chunks)
                }
            
            memory.add_assistant_message(content=answer, tools_metadata=tools_metadata if tools_metadata else None)
            logger.assistant(answer, meta={"model": (model or DEFAULT_MODEL)})
            
            # ✅ NÃO aguarda threads aqui - retorna imediatamente com referências às threads
            # A UI pode mostrar a resposta e aguardar threads em background
            out: Dict[str, Any] = {
                "answer": answer,
                "metrics": {
                    "per_iteration": metrics_per_iteration,
                    "total_elapsed_hms": _fmt_hms(_time.perf_counter() - t0)
                },
                "tools": [],
                "timeline": timeline,
                "iteration_count": tool_call_count,  # Número de iterações com tool calls
                "llm_call_count": llm_call_count,  # Total de chamadas ao LLM
                "tools_summary": {
                    "retriever_called": len(retriever_queries) > 0,
                    "code_interpreter_called": code_interpreter_called
                },
                "retriever_audits": retriever_audits,  # Audits completos de todas as chamadas ao retriever
                "seletor_threads": anotador_threads,  # ✅ Retorna threads para UI aguardar
                "tokens_tracking": {  # NOVO: Dados completos de tokens para UI
                    "resumo_componentes": tokens_tracker.obter_resumo_por_componente(),
                    "resumo_total": tokens_tracker.obter_resumo_total(),
                    "tabela_detalhada": tokens_tracker.obter_tabela_detalhada(),
                    "resumo_retriever_detalhado": tokens_tracker.obter_resumo_retriever_detalhado()
                }
            }
            if artifacts:
                out["artifacts"] = artifacts
            return out
        
        # Processar tool calls
        messages.append(response)  # Adiciona AIMessage com tool_calls
        tool_call_count += 1  # Incrementa contador de tool calls executadas
        
        for call in tool_calls:
            name = call.get("name")
            args = call.get("args", {}) or {}
            
            if name == "consultar_vector_store_retriever":
                retriever_call_count += 1  # Incrementa contador de chamadas do retriever
                evt_tool_call = {
                    "stage": "tool_call",
                    "ts": _time.perf_counter() - t0,
                    "tool": "retriever",
                    "iteration": iteration,
                    "label": f"{_ordinal_pt(retriever_call_count)} chamada do retriever",
                    "icon": "🔧",
                    "query": args.get("query")
                }
                timeline.append(evt_tool_call)
                if event_callback:
                    event_callback(evt_tool_call)
                
                retriever_query_used = args.get("query")
                retriever_queries.append(retriever_query_used)
                chunks, audit, retriever_metrics = _call_retriever_and_log(
                    query=retriever_query_used or "",
                    base_config=config,
                    logger=logger,
                    timeline=timeline,
                    tools_events=tools_events,
                    label=f"{_ordinal_pt(retriever_call_count)} chamada do retriever",
                    iteration=iteration,
                    t0=t0,
                )
                # Acumula audit completo para debug do retriever
                retriever_audits.append({
                    "iteration": iteration,
                    "query": retriever_query_used,
                    "audit": audit,
                    "chunks": chunks,
                    "num_chunks": len(chunks),
                })
                
                # NOVO: Registra tokens do Retriever (Steps 1 e 2) no tracker
                retriever_model_used = audit.get("retriever_model", retriever_model or "gpt-5-mini")
                step1_tokens = audit.get("step1_tokens", {"input": 0, "output": 0, "reasoning": 0, "total": 0})
                step2_tokens = audit.get("step2_tokens", {"input": 0, "output": 0, "reasoning": 0, "total": 0})
                step1_elapsed = audit.get("step1_elapsed", 0.0)
                step2_elapsed = audit.get("step2_elapsed", 0.0)
                
                tokens_tracker.registrar_chamada(
                    componente="retriever_step1",
                    iteracao=iteration,
                    model=retriever_model_used,
                    tokens=step1_tokens,
                    elapsed_seconds=step1_elapsed
                )
                tokens_tracker.registrar_chamada(
                    componente="retriever_step2",
                    iteracao=iteration,
                    model=retriever_model_used,
                    tokens=step2_tokens,
                    elapsed_seconds=step2_elapsed
                )
                tool_call_id = call.get("id") or call.get("tool_call_id") or f"tool_call_{iteration}"
                tool_result_json = json.dumps(chunks, ensure_ascii=False)
                messages.append(ToolMessage(content=tool_result_json, tool_call_id=tool_call_id))
                all_chunks.extend(chunks)
                
                # NOVO: Armazena metadados desta chamada específica
                retriever_calls_metadata.append({
                    "query": retriever_query_used,
                    "chunks": chunks,  # Chunks DESTA chamada (não misturados)
                    "num_chunks": len(chunks),
                    "iteration": iteration,
                    "call_number": retriever_call_count
                })
                
                # ====== CHAMADA EM BACKGROUND AO AGENT SELETOR ======
                # Após cada chamada do retriever, executa o seletor EM PARALELO para filtrar chunks relevantes
                if chunks:  # Apenas se houver chunks
                    anotador_count += 1  # Incrementa contador de seleções
                    
                    # ✅ Captura valores no momento da criação da thread (closure seguro)
                    # IMPORTANTE: Capturar ANTES de criar eventos para evitar race conditions
                    previous_thread = anotador_threads[-1] if anotador_threads else None
                    current_iteration = iteration  # ✅ Captura valor AGORA (não mudará)
                    current_selecao_num = anotador_count  # ✅ Captura número da seleção
                    current_chunks = chunks  # ✅ Captura chunks desta iteração
                    current_escopo = escopo_atual  # ✅ Captura escopo atual
                    
                    evt_seletor_start = {
                        "stage": "seletor_start",
                        "ts": _time.perf_counter() - t0,
                        "iteration": iteration,
                        "label": f"Seletor processando chunks (seleção {current_selecao_num})",
                        "icon": "📝"
                    }
                    timeline.append(evt_seletor_start)
                    if event_callback:
                        event_callback(evt_seletor_start)
                    
                    # Função que será executada em background
                    def _run_seletor_background(
                        previous_thread=previous_thread,
                        current_iteration=current_iteration,
                        current_selecao_num=current_selecao_num,
                        current_chunks=current_chunks,
                        current_escopo=current_escopo,
                    ):
                        import asyncio
                        import sys
                        
                        try:
                            # ✅ SINCRONIZAÇÃO INTERNA: Aguarda thread anterior DENTRO desta thread
                            # Isso NÃO bloqueia o agente principal!
                            if previous_thread:
                                print(f"[SELETOR] Seleção {current_selecao_num} (Iter {current_iteration}) aguardando seleção anterior terminar...", file=sys.stderr)
                                previous_thread.join()  # Aguarda sem timeout (mas em background!)
                                print(f"[SELETOR] Seleção {current_selecao_num} (Iter {current_iteration}) - seleção anterior concluída ✓", file=sys.stderr)
                            
                            # Obter histórico da conversa (para contexto)
                            conversation_history = memory.get_llm_history()
                            
                            # Executar seletor (medir tempo)
                            t_seletor_start = _time.perf_counter()
                            resultado_seletor = asyncio.run(executar_seletor(
                                chunks=current_chunks,
                                conversation_history=conversation_history,
                                escopo=current_escopo,
                                model=anotador_model or "gpt-5-mini-2025-08-07",
                                reasoning_effort=anotador_reasoning_effort,
                            ))
                            t_seletor_end = _time.perf_counter()
                            elapsed_seletor = t_seletor_end - t_seletor_start
                            
                            if resultado_seletor.get("success"):
                                chunks_selecionados = resultado_seletor.get("selected_chunks", [])
                                indices_validos = resultado_seletor.get("selected_indices", [])
                                indices_invalidos = resultado_seletor.get("invalid_indices", [])
                                status_selecao = resultado_seletor.get("status", "success")
                                
                                # NOVO: Registra tokens do Seletor no tracker
                                seletor_tokens = resultado_seletor.get("tokens", {"input": 0, "output": 0, "reasoning": 0, "total": 0})
                                seletor_model_used = resultado_seletor.get("model_used", anotador_model or "gpt-5-mini")
                                tokens_tracker.registrar_chamada(
                                    componente="seletor",
                                    iteracao=current_iteration,
                                    model=seletor_model_used,
                                    tokens=seletor_tokens,
                                    elapsed_seconds=elapsed_seletor
                                )
                                
                                # Adiciona chunks ao estado (com deduplicação automática)
                                stats = memory.get_chunks_relevantes().adicionar_chunks(
                                    chunks_selecionados=chunks_selecionados,
                                    iteracao=current_iteration,
                                    chunks_recebidos=len(current_chunks),
                                    indices_retornados=indices_validos + indices_invalidos,
                                    indices_invalidos=indices_invalidos,
                                    status=status_selecao,
                                    erro_msg=None,
                                    model=anotador_model or "gpt-5-mini-2025-08-07",
                                    elapsed_seconds=elapsed_seletor
                                )
                                
                                evt_seletor_success = {
                                    "stage": "seletor_success",
                                    "ts": _time.perf_counter() - t0,
                                    "iteration": current_iteration,
                                    "label": f"Chunks selecionados (seleção {current_selecao_num}): {stats['chunks_adicionados']} novos",
                                    "icon": "✅",
                                    "chunks_adicionados": stats["chunks_adicionados"],
                                    "chunks_duplicados": stats["chunks_duplicados"]
                                }
                                timeline.append(evt_seletor_success)
                                if event_callback:
                                    event_callback(evt_seletor_success)
                            else:
                                error_msg = resultado_seletor.get("error", "Erro desconhecido")
                                evt_seletor_error = {
                                    "stage": "seletor_error",
                                    "ts": _time.perf_counter() - t0,
                                    "iteration": current_iteration,
                                    "label": f"Erro no seletor (seleção {current_selecao_num}): {error_msg}",
                                    "icon": "⚠️"
                                }
                                timeline.append(evt_seletor_error)
                                if event_callback:
                                    event_callback(evt_seletor_error)
                        except Exception as e:
                            evt_seletor_exception = {
                                "stage": "seletor_exception",
                                "ts": _time.perf_counter() - t0,
                                "iteration": current_iteration,
                                "label": f"Exceção no seletor (seleção {current_selecao_num}): {str(e)}",
                                "icon": "❌"
                            }
                            timeline.append(evt_seletor_exception)
                            if event_callback:
                                event_callback(evt_seletor_exception)
                    
                    # Inicia o seletor em uma thread separada (não bloqueia)
                    import threading
                    seletor_thread = threading.Thread(target=_run_seletor_background, daemon=True)  # daemon=True: encerra com o processo principal
                    seletor_thread.start()
                    anotador_threads.append(seletor_thread)  # Adiciona à lista para aguardar depois
                    # A thread roda em paralelo, mas aguardaremos no final
            else:
                # Outras tools (ignoradas ou CI executado pelo provedor)
                tool_call_id = call.get("id") or call.get("tool_call_id") or f"tool_call_{iteration}_other"
                messages.append(ToolMessage(content=json.dumps({"status": "ignored"}), tool_call_id=tool_call_id))

        # Se atingiu o limite de chamadas do retriever neste turno, orientar síntese final (soft limit)
        if isinstance(max_tool_calls, int) and max_tool_calls >= 0:
            if (len(retriever_queries) >= max_tool_calls) and (not limit_announced):
                messages.append(SystemMessage(content=LIMIT_RETRIEVER_REACHED_MSG))
                limit_announced = True
    # Nota: o loop encerra quando o LLM não solicita tools e gera a resposta final


def _print_event_cli(event: Dict[str, Any]) -> None:
    """Callback simples para imprimir eventos no terminal."""
    stage = event.get("stage")
    iteration = event.get("iteration")
    
    if stage == "iteration_start":
        print(f"\n🔄 Iteração {iteration} iniciada...")
    
    elif stage == "iteration_end":
        tokens = event.get("tokens", {})
        print(f"✅ Iteração {iteration} concluída — Tokens: {tokens.get('total', 0)}")
    
    elif stage == "tool_call":
        query = event.get("query", "")
        print(f"\n🔧 Retriever chamado:")
        print(f"   Query: {query[:80]}{'...' if len(query) > 80 else ''}")
    
    elif stage == "tool_result":
        num_chunks = event.get("num_chunks", 0)
        print(f"✅ Retriever retornou {num_chunks} chunk(s)")
    
    elif stage == "seletor_start":
        print(f"📝 Agent Seletor processando chunks...")
    
    elif stage == "seletor_success":
        chunks_add = event.get("chunks_adicionados", 0)
        chunks_dup = event.get("chunks_duplicados", 0)
        print(f"✅ Seletor: {chunks_add} novos, {chunks_dup} duplicados")
    
    elif stage == "final_response":
        print(f"\n🎯 Gerando resposta final...")


def main() -> None:
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)
    
    parser = argparse.ArgumentParser(description="Finance_AI agent (PT-BR) com multi-hop e Agent Seletor")
    parser.add_argument("--max-tool-calls", type=int, default=3, help="Máximo de chamadas ao retriever por turno (padrão: 3)")
    parser.add_argument("--retriever-model", type=str, default="gpt-5-mini-2025-08-07", help="Modelo do retriever (padrão: gpt-5-mini)")
    parser.add_argument("--seletor-model", type=str, default="gpt-5-mini-2025-08-07", help="Modelo do Agent Seletor (padrão: gpt-5-mini)")
    parser.add_argument("--reasoning-effort", type=str, default="medium", choices=["low", "medium", "high"], help="Esforço de raciocínio do Analista (padrão: medium)")
    parser.add_argument("--seletor-reasoning", type=str, default="medium", choices=["low", "medium", "high"], help="Esforço de raciocínio do Seletor (padrão: medium)")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("  Finance_AI (CLI) — 1 LLM Multi-hop + Agent Seletor")
    print("="*70)
    
    # Configurações
    print(f"\n⚙️  Configurações:")
    print(f"   • Max tool calls: {args.max_tool_calls}")
    print(f"   • Retriever model: {args.retriever_model}")
    print(f"   • Seletor model: {args.seletor_model}")
    print(f"   • Reasoning effort: {args.reasoning_effort}")
    
    # Prompt de Escopo
    print("\n" + "-"*70)
    print("📋 ESCOPO E OBJETIVO DA ANÁLISE")
    print("-"*70)
    print("Defina o escopo da sua análise (será usado em toda a conversa):")
    print("Exemplo: 'Análise da rentabilidade da MULT3 no 2T25, foco em EBITDA'")
    escopo = input("\nEscopo: ").strip()
    
    if not escopo:
        print("⚠️  Escopo vazio. Usando escopo genérico.")
        escopo = "Análise financeira geral dos documentos disponíveis."
    
    print("\n" + "="*70)
    print("  Modelos disponíveis para cada pergunta:")
    print("="*70)
    print("  1 - o3-2025-04-16")
    print("  2 - o3-pro-2025-06-10")
    print("  3 - gpt-5-2025-08-07 (padrão)")
    print("\n  Use o formato: 'N | sua pergunta'")
    print("  Exemplo: 1 | Qual foi o Lucro Líquido?")
    print("\n  Digite 'sair' para encerrar.")
    print("="*70)
    
    memory = ConversationMemory()
    memory.set_escopo(escopo)  # Define escopo no memory
    logger = ConversationLogger()
    
    while True:
        raw = input("\n💬 Pergunta: ").strip()
        if raw.lower() == "sair":
            print("\n👋 Encerrando. Até mais!")
            break
        
        if not raw:
            continue
        
        # Parsing do prefixo "N | pergunta"
        selected_model = DEFAULT_MODEL
        question = raw
        m = re.match(r"^\s*(\d)\s*\|\s*(.+)$", raw)
        if m:
            num = m.group(1)
            question = m.group(2).strip()
            selected_model = MODEL_CHOICES.get(num, DEFAULT_MODEL)
        
        if question.lower() == "sair":
            print("\n👋 Encerrando. Até mais!")
            break
        
        print(f"\n🤖 Modelo: {selected_model}")
        print("-"*70)
        
        t0 = time.perf_counter()
        result = run_agent_turn_single_llm(
            memory=memory,
            question=question,
            logger=logger,
            model=selected_model,
            reasoning_effort=args.reasoning_effort,
            retriever_model=args.retriever_model,
            max_tool_calls=args.max_tool_calls,
            event_callback=_print_event_cli,
            anotador_model=args.seletor_model,
            anotador_reasoning_effort=args.seletor_reasoning
        )
        t1 = time.perf_counter()
        
        # Aguarda threads do seletor terminarem
        seletor_threads = result.get("seletor_threads", [])
        if seletor_threads:
            print("\n⏳ Aguardando seleção de chunks finalizar...")
            for thread in seletor_threads:
                thread.join()
            print("✅ Seleção concluída!")
        
        print("\n" + "="*70)
        print("  RESPOSTA:")
        print("="*70)
        print(result.get("answer", ""))
        
        # Métricas
        print("\n" + "-"*70)
        print("📊 MÉTRICAS:")
        print("-"*70)
        
        metrics = result.get("metrics", {})
        per_iteration = metrics.get("per_iteration", [])
        total_elapsed = metrics.get("total_elapsed_hms", "00:00:00")
        
        # Tokens totais
        total_tokens = sum(it.get("tokens", {}).get("total", 0) for it in per_iteration)
        print(f"⏱️  Tempo total: {total_elapsed}")
        print(f"🔢 Total de tokens: {total_tokens:,}")
        print(f"🔄 Iterações: {result.get('iteration_count', 0)}")
        print(f"🤖 Chamadas LLM: {result.get('llm_call_count', 0)}")
        
        # Tracking detalhado de tokens (se disponível)
        tokens_tracking = result.get("tokens_tracking")
        if tokens_tracking:
            resumo_total = tokens_tracking.get("resumo_total", {})
            custo = resumo_total.get("total_custo", 0.0)
            if custo > 0:
                print(f"💰 Custo estimado: ${custo:.4f}")
        
        # Chunks memorizados
        chunks_state = memory.get_chunks_relevantes()
        if chunks_state.tem_chunks():
            stats = chunks_state.obter_estatisticas()
            print(f"📝 Chunks memorizados: {stats.get('total_chunks', 0)} ({stats.get('total_documentos', 0)} doc(s))")
        
        print("="*70)


if __name__ == "__main__":
    main()


