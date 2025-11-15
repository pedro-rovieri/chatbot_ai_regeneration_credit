#!/usr/bin/env python3
"""
Script de consulta inteligente ao vector store usando retriever de 2 etapas com LLM.

Este script implementa um RAG para relatórios financeiros em duas etapas:

1) Etapa 1 — Seleção de Documentos:
- LLM analisa a solicitação do usuário
- Identifica documentos por metadados (ticker, report, period)
- Retorna um JSON com filtros de metadados (listas de valores por campo)

2) Etapa 2 — Seleção de Conteúdo e Estratégia de Busca:
- LLM recebe os documentos selecionados e, para cada documento, sua lista de headings_enriched
- Decide se filtra por headings específicos (ou não) e devolve:
  { filters, semantic_query, use_semantic }
  • filters: somente chaves {ticker, report, period, headings_enriched}
  • semantic_query: string com a consulta semântica (quando pertinente)
  • use_semantic: true para executar busca semântica; false para apenas filtragem por metadados
 - Boas práticas por tipo de report:
   • DF: tender a use_semantic=false, a menos que a solicitação seja ampla/aberta
   • planilha: SEMPRE use_semantic=false e NÃO filtrar por 'period' (série histórica)
   • Teleconferencia: tender a use_semantic=true e SEMPRE informar 'period' na seleção de documentos
   • Release + Teleconferencia (mesmo período): tender a use_semantic=true quando a consulta pedir conexão qualitativa entre ambos

Importante sobre headings:
- A exclusão de headings genéricos (ex.: "cabeçalho") acontece ANTES da Etapa 2. Assim, as listas de
  headings_enriched entregues ao LLM já estão filtradas desses termos.
- Não há deduplicação global entre documentos: o mesmo heading pode aparecer em documentos distintos e
  será apresentado separadamente por documento ao LLM.
- Para Teleconferencia, os headings_enriched podem estar alinhados com a taxonomia do Release correspondente, permitindo consultas combinadas por período.
- Validação: apenas headings que existem exatamente no índice são aceitos (match exato).

Outros detalhes:
- Fallbacks para sintaxes de filtro do Chroma ($in vs $or)
- Loga a decisão do LLM (use_semantic) e os filtros finais aplicados
- Impressão de resultados com distância cosseno quando use_semantic=true; caso contrário, distância é "N/A"
- Cronometragem do tempo de execução

Fluxo:
User Query → LLM (Etapa 1) → Filtros de Documento → LLM (Etapa 2) → {filters, semantic_query, use_semantic} →
Chroma (similarity_search_with_score OU apenas where) → Resultados

Dependências:
- Chroma + OpenAI text-embedding-3-large (dim=3072)
- Índice de headings (scripts/construir_headings_index.py)
- Variáveis: OPENAI_API_KEY, opcionalmente HEADINGS_EXCLUDED
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
import os
import unicodedata
from typing import Any, Dict, List, Tuple, Set
import time

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableConfig

# Import de extract_token_usage para capturar métricas de tokens
try:
    from scripts.finance_ai_utils import extract_token_usage
except ImportError:
    # Fallback caso o módulo não esteja disponível
    def extract_token_usage(msg):
        return {"input": 0, "output": 0, "reasoning": 0, "total": 0}


COLLECTION_NAME = "XPAsset_openai_te3_large_v1"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072
DEFAULT_RETRIEVER_MODEL = "gpt-5-2025-08-07"  # Modelo padrão do retriever (fallback)
# Conjunto de modelos permitidos quando houver override vindo da UI/config
RETRIEVER_ALLOWED_MODELS = {
    "gpt-5-mini-2025-08-07",
    "gpt-5-2025-08-07",
}
# Garantia: o default precisa pertencer ao conjunto permitido
if DEFAULT_RETRIEVER_MODEL not in RETRIEVER_ALLOWED_MODELS:
    # fallback defensivo: inclui o default se alguém alterar constants no futuro
    RETRIEVER_ALLOWED_MODELS.add(DEFAULT_RETRIEVER_MODEL)


# Retorna o diretório raiz do projeto (a pasta pai deste script), usado para resolver caminhos relativos.
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


# Caminho do índice consolidado de headings_enriched (gerado previamente) em formato JSONL.
def headings_index_path() -> Path:
    return project_root() / "headings_enriched_index" / "headings_enriched_index.jsonl"


# Cria o vector store Chroma apontando para a coleção e diretório persistidos, com embeddings OpenAI configurados.
def build_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIM)
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(project_root() / "chroma_vectorstore"),
        embedding_function=embeddings,
    )


# Instancia o LLM de chat que será usado para gerar as saídas das Etapas 1 e 2 do retriever.
def build_llm(retriever_model: str | None = None) -> ChatOpenAI:
    # Se um modelo válido for informado pela UI/config, usa-o; caso contrário, usa o default
    model_to_use = DEFAULT_RETRIEVER_MODEL
    if isinstance(retriever_model, str) and retriever_model in RETRIEVER_ALLOWED_MODELS:
        model_to_use = retriever_model
    return ChatOpenAI(model=model_to_use, use_responses_api=False)


# Carrega o arquivo JSONL de índice de headings_enriched, retornando uma lista de linhas (dicts).
def load_headings_index() -> List[Dict[str, Any]]:
    path = headings_index_path()
    if not path.exists():
        raise FileNotFoundError(
            "headings_enriched_index.jsonl não encontrado. Rode o construtor em scripts/construir_headings_index.py build"
        )
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


# Indexa o conjunto de headings por chave (ticker, report, period) para acesso rápido por documento.
def index_by_key(rows: List[Dict[str, Any]]) -> Dict[Tuple[str, str, str], List[str]]:
    by_key: Dict[Tuple[str, str, str], List[str]] = {}
    for r in rows:
        key = (
            str(r.get("ticker", "")),
            str(r.get("report", "")),
            str(r.get("period", "")),
        )
        headings = r.get("headings", []) or []
        by_key[key] = [str(h) for h in headings]
    return by_key


# Extrai um JSON válido de um texto (suporta bloco ```json ... ``` ou heurística do primeiro '{' ao último '}').
def extract_json_block(text: str) -> Dict[str, Any]:
    try:
        fenced = re.search(r"```json\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
        if fenced:
            return json.loads(fenced.group(1))
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
    except Exception:
        pass
    return json.loads(text)


# --- Exclusão de headings genéricos (ex.: "cabeçalho") ---
# Normaliza texto (lowercase, sem acentos) para comparações tolerantes, útil na filtragem de headings genéricos.
def _normalize_text(value: str) -> str:
    value = value.strip().lower()
    # remove acentos para ampliar match (cabecalho ~ cabeçalho)
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    return value


# Lê lista de headings a excluir do ambiente (HEADINGS_EXCLUDED) e combina com defaults como "cabeçalho".
def _load_excluded_headings() -> Set[str]:
    # Default inclui variações de "cabeçalho"
    defaults = {"cabecalho", "cabeçalho"}
    raw = os.getenv("HEADINGS_EXCLUDED", "").strip()
    if not raw:
        return {_normalize_text(x) for x in defaults}
    items = [x for x in (p.strip() for p in raw.split(",")) if x]
    items.extend(list(defaults))
    return {_normalize_text(x) for x in items}


EXCLUDED_HEADINGS_NORM: Set[str] = _load_excluded_headings()


# Remove da lista quaisquer headings que constem na lista de exclusão normalizada.
def _filter_excluded(headings: List[str]) -> List[str]:
    out: List[str] = []
    for h in headings:
        if _normalize_text(h) in EXCLUDED_HEADINGS_NORM:
            continue
        out.append(h)
    return out


def _build_headings_with_ids(
    doc_to_headings: Dict[str, List[str]]
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, str]]:
    """
    Converte listas de headings em dicionários numerados com IDs únicos globalmente.
    
    Args:
        doc_to_headings: {"ticker|report|period": ["heading1", "heading2", ...]}
    
    Returns:
        - doc_to_headings_with_ids: {"ticker|report|period": {"1": "heading1", "2": "heading2", ...}}
        - id_to_heading: {"1": "heading1", "2": "heading2", ...} (mapa global para validação)
    
    Exemplo:
        Input: {
            "MULT3|DF|2025-06-30": ["DRE", "Balanço"],
            "MULT3|DF|2024-12-31": ["DRE", "Fluxo de Caixa"]
        }
        Output: (
            {
                "MULT3|DF|2025-06-30": {"1": "DRE", "2": "Balanço"},
                "MULT3|DF|2024-12-31": {"3": "DRE", "4": "Fluxo de Caixa"}
            },
            {"1": "DRE", "2": "Balanço", "3": "DRE", "4": "Fluxo de Caixa"}
        )
    """
    doc_to_headings_with_ids = {}
    id_to_heading = {}
    current_id = 1
    
    for doc_key, headings_list in doc_to_headings.items():
        headings_dict = {}
        for heading in headings_list:
            heading_id = str(current_id)
            headings_dict[heading_id] = heading
            id_to_heading[heading_id] = heading
            current_id += 1
        doc_to_headings_with_ids[doc_key] = headings_dict
    
    return doc_to_headings_with_ids, id_to_heading


# Templates de prompt (expostos para UI/documentação)
RETRIEVER_STEP1_PROMPT: str = (
    "Você é um assistente que atua em um processo de investimentos em ações de companhias abertas brasileiras.\n\n"
    "Escopo e Objetivo da Análise: {escopo}\n"
    "Use este contexto para priorizar documentos mais relevantes ao objetivo.\n\n"
    "TAREFA:\n"
    "Analisar a solicitação e identificar quais documentos são necessários.\n"
    "Os documentos estão organizados por metadados: ticker (ex.: MULT3), report (DF, Release, planilha ou Teleconferencia) e period no formato ISO (YYYY-MM-DD).\n\n"
    "Regras específicas:\n"
    "- Para Teleconferencia, SEMPRE informe 'period'.\n"
    "- Para planilha, geralmente NÃO informe 'period' (série histórica).\n"
    "- Quando a solicitação pedir visão qualitativa da call associada ao release do mesmo período, selecione AMBOS: report=[\"Release\",\"Teleconferencia\"] com o mesmo 'period'.\n"
    "- Priorize documentos que contribuam diretamente para o escopo/objetivo definido.\n\n"
    "Retorne um JSON COMPACTO com listas de valores para cada campo.\n"
    "Campos possíveis: ticker (strings), report (strings; DF, Release, planilha, Teleconferencia), period (strings ISO YYYY-MM-DD).\n\n"
    "Formato estrito:\n"
    "{{\n  \"documents\": {{\n    \"ticker\": [string],\n    \"report\": [string],\n    \"period\": [string]\n  }}\n}}\n\n"
    "Você PODE omitir campos caso julgue pertinente (por falta de evidência).\n\n"
    "Solicitação do usuário:\n{query_nl}"
)

RETRIEVER_STEP2_PROMPT: str = (
    "Você é um assistente que atua em um processo de investimentos em ações de companhias abertas brasileiras.\n\n"
    "Escopo e Objetivo da Análise: {escopo}\n"
    "Priorize conteúdo alinhado a este objetivo.\n\n"
    "Você receberá: (1) a solicitação do usuário, (2) os documentos considerados pertinentes e previamente selecionados por metadados, e (3) os headings_enriched disponíveis em cada documento (como dicionários ID: nome).\n"
    "Tarefa:\n"
    "- Se a solicitação for ampla/genérica, NÃO filtre por headings_enriched; use somente os filtros de documento (ticker/report/period) e produza uma semantic_query abrangente.\n"
    "- Se a solicitação focar temas específicos, selecione os IDs numéricos dos headings_enriched relevantes e, se pertinente, formule uma semantic_query correspondente.\n"
    "- Defina use_semantic:\n"
    "  • DF: sempre false.\n"
    "  • planilha: SEMPRE false e NÃO inclua 'period' em filters.\n"
    "  • Teleconferencia: em geral true (conteúdo conversacional e disperso no tempo).\n"
    "  • Release + Teleconferencia juntos (mesmo período): em geral true, para conectar pontos qualitativos da call ao release.\n"
    "Retorne APENAS o JSON com este formato estrito:\n"
    "{{\n  \"filters\": {{\n    \"ticker\": {{\"$in\": [string]}},\n    \"report\": {{\"$in\": [string]}},\n    \"period\": {{\"$in\": [string]}},\n    \"headings_enriched\": {{\"$in\": [integer]}}\n  }},\n  \"semantic_query\": string,\n  \"use_semantic\": true|false\n}}\n\n"
    "Regras:\n"
    "- headings_enriched é OPCIONAL; quando presente, use somente os IDs numéricos fornecidos; múltiplos IDs representam UNIÃO.\n"
    "- period SEMPRE string YYYY-MM-DD; para planilha, omita 'period'.\n"
    "- filters: só pode conter as chaves ticker, report, period, headings_enriched.\n"
    "- semantic_query: você recebe o prompt do usuário e dele deve produzir uma query semântica objetiva e específica quando for o caso.\n\n"
    "Solicitação do usuário: {query_nl}\n"
    "Documentos selecionados: {selected_docs_json}\n"
    "Headings por documento (ID: nome): {headings_json}\n"
)


# Monta o prompt da Etapa 1 para o LLM identificar filtros de documentos (ticker/report/period) a partir da solicitação.
def prompt_step1(query_nl: str, escopo: str | None = None) -> str:
    return RETRIEVER_STEP1_PROMPT.format(query_nl=query_nl, escopo=(escopo or ""))


# Monta o prompt da Etapa 2 para o LLM decidir se filtra por headings_enriched e gerar a semantic_query adequada.
def prompt_step2(query_nl: str, selected_docs: Dict[str, List[str]], doc_to_headings: Dict[str, List[str]], escopo: str | None = None) -> str:
    # selected_docs: keys "ticker", "report", "period" com listas
    # doc_to_headings: chave textual "ticker|report|period" -> lista de headings
    selected_docs_json = json.dumps(selected_docs, ensure_ascii=False)
    # Enviamos TODAS as listas de headings (sem amostragem), conforme especificado
    headings_json = json.dumps(doc_to_headings, ensure_ascii=False)
    return RETRIEVER_STEP2_PROMPT.format(
        query_nl=query_nl,
        selected_docs_json=selected_docs_json,
        headings_json=headings_json,
        escopo=(escopo or ""),
    )


ALLOWED_OPS = {"$eq", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"}
SIMPLE_TYPES = (str, int, float, bool, type(None))


# Converte um dict de filtros em um formato aceito pelo Chroma, restringindo a operadores permitidos e encapsulando em $and.
def sanitize_where(filters: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if not filters:
        return None
    out: Dict[str, Any] = {}
    for field, expr in filters.items():
        if isinstance(expr, dict):
            clean: Dict[str, Any] = {}
            for op, val in expr.items():
                if op not in ALLOWED_OPS:
                    continue
                if op in {"$in", "$nin"}:
                    if isinstance(val, list) and all(isinstance(x, SIMPLE_TYPES) for x in val):
                        clean[op] = val
                else:
                    if isinstance(val, SIMPLE_TYPES):
                        clean[op] = val
            if clean:
                out[field] = clean
    if not out:
        return None
    and_terms: List[Dict[str, Any]] = []
    for field, expr in out.items():
        and_terms.append({field: expr})
    return {"$and": and_terms}


# Imprime resultados a partir de uma lista de documentos da LangChain com score (modo legado).
def imprimir_resultados_scores(docs_scores: List[Tuple[Any, float]]) -> None:
    print(f"Resultados: {len(docs_scores)}\n")
    for i, (d, score) in enumerate(docs_scores, 1):
        md = d.metadata or {}
        cid = md.get("chunk_id")
        ticker_v = md.get("ticker")
        report_v = md.get("report")
        page_no_v = md.get("page_no")
        headings_enriched_v = md.get("headings_enriched")
        period_v = md.get("period")
        header = (
            f"==========={{ [{i}] cosine distance : {score}, "
            f"chunk_id : {cid}, ticker : {ticker_v}, report : {report_v}, "
            f"page_no : {page_no_v}, headings_enriched : {headings_enriched_v}, periodo : {period_v} }}==========="
        )
        print(header)
        print()
        print("page_content:")
        print(d.page_content)
        print()


# Imprime resultados a partir da lista serializada de chunks (dicts) retornada por retriever_query.
def imprimir_chunks(chunks: List[Dict[str, Any]]) -> None:
    print(f"Resultados: {len(chunks)}\n")
    for i, ch in enumerate(chunks, 1):
        md = ch.get("metadata", {}) or {}
        cid = md.get("chunk_id")
        ticker_v = md.get("ticker")
        report_v = md.get("report")
        page_no_v = md.get("page_no")
        headings_enriched_v = md.get("headings_enriched")
        period_v = md.get("period")
        score_v = ch.get("score")
        header = (
            f"==========={{ [{i}] cosine distance : {score_v if score_v is not None else 'N/A'}, "
            f"chunk_id : {cid}, ticker : {ticker_v}, report : {report_v}, "
            f"page_no : {page_no_v}, headings_enriched : {headings_enriched_v}, periodo : {period_v} }}==========="
        )
        print(header)
        print()
        print("page_content:")
        print(ch.get("page_content", ""))
        print()


# Formata segundos transcorridos no padrão HH:MM:SS para logs de duração.
def format_hms(elapsed_seconds: float) -> str:
    total = int(elapsed_seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# Recupera o objeto interno da coleção do Chroma para operações de debug (amostras/contagens com where).
def _get_collection(vs: Chroma):
    coll = getattr(vs, "_collection", None)
    if coll is None and hasattr(vs, "_client"):
        try:
            coll = vs._client.get_collection(COLLECTION_NAME)
        except Exception:
            coll = None
    return coll


# Heurística de contagem: retorna 0 ou 1+ para indicar se há candidatos que satisfazem o filtro where.
def _count_with_where(coll, where: Dict[str, Any]) -> int:
    try:
        chunk = coll.get(include=["metadatas"], where=where, limit=1, offset=0)
        # Não há API de count com where; iteração completa é cara. Aqui usamos um atalho:
        # se há pelo menos 1, retornamos 1+ (indicativo). Para debug já ajuda.
        metas = chunk.get("metadatas", []) or []
        return len(metas)
    except Exception:
        return 0


# Obtém uma pequena amostra de resultados (ids, metadados e prévia do documento) para inspecionar o filtro where.
def _sample_with_where(coll, where: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
    try:
        chunk = coll.get(include=["documents", "metadatas", "ids"], where=where, limit=k, offset=0)
    except Exception:
        return []
    ids = chunk.get("ids", []) or []
    docs = chunk.get("documents", []) or []
    metas = chunk.get("metadatas", []) or []
    out: List[Dict[str, Any]] = []
    for i in range(min(k, len(metas))):
        md = metas[i] or {}
        out.append({
            "id": ids[i] if i < len(ids) else None,
            "chunk_id": md.get("chunk_id"),
            "ticker": md.get("ticker"),
            "report": md.get("report"),
            "period": md.get("period"),
            "heading": md.get("headings_enriched"),
            "preview": (docs[i] or "")[:120],
        })
    return out


# Função principal: orquestra as duas etapas do retriever, executa a busca semântica no Chroma e imprime resultados e tempo de execução.
def _extend_config(parent: RunnableConfig | None, run_name: str, extra_tags: List[str] | None = None) -> RunnableConfig:
    base: RunnableConfig = dict(parent or {})  # type: ignore
    tags = list(base.get("tags", []) or [])  # type: ignore
    for t in (extra_tags or []):
        if t not in tags:
            tags.append(t)
    if tags:
        base["tags"] = tags  # type: ignore
    base["run_name"] = run_name  # type: ignore
    return base


def retriever_query(
    query_nl: str,
    k: int = 10,
    debug: bool = False,
    config: RunnableConfig | None = None,
    retriever_model: str | None = None,
) -> Dict[str, Any]:
    load_dotenv()
    llm = build_llm(retriever_model=retriever_model)
    t0 = time.perf_counter()
    # Recupera escopo do metadata (se fornecido pelo chamador)
    escopo_ctx: str | None = None
    try:
        if isinstance(config, dict):
            meta = config.get("metadata") or {}
            v = meta.get("escopo")
            if isinstance(v, str) and v.strip():
                escopo_ctx = v.strip()
    except Exception:
        escopo_ctx = None

    # Etapa 1: seleção de documentos
    t_step1_start = time.perf_counter()
    step1_prompt = prompt_step1(query_nl, escopo=escopo_ctx)
    cfg1 = _extend_config(config, run_name="retriever_step1", extra_tags=["retriever", "step1"]) if config is not None else None
    resp1 = llm.invoke(step1_prompt, config=cfg1)
    t_step1_end = time.perf_counter()
    
    # Captura tokens do Step 1
    step1_tokens = extract_token_usage(resp1)
    
    # Captura resposta completa do LLM (Step 1)
    step1_raw_content = getattr(resp1, "content", resp1)
    data1 = extract_json_block(step1_raw_content)
    docs_sel = data1.get("documents") or {}

    # Normaliza para listas
    selected_docs: Dict[str, List[str]] = {}
    for key in ("ticker", "report", "period"):
        val = docs_sel.get(key)
        if val is None:
            continue
        if isinstance(val, list):
            selected_docs[key] = [str(x) for x in val]
        else:
            selected_docs[key] = [str(val)]

    # Carrega headings do índice para os documentos selecionados
    rows = load_headings_index()
    by_key = index_by_key(rows)
    doc_to_headings: Dict[str, List[str]] = {}
    excluded_exact_values: Set[str] = set()

    # Verifica se uma chave (ticker, report, period) do índice é compatível com os documentos selecionados na Etapa 1.
    def matches(doc_key: Tuple[str, str, str]) -> bool:
        t, r, p = doc_key
        ok_t = ("ticker" not in selected_docs) or (t in selected_docs.get("ticker", []))
        ok_r = ("report" not in selected_docs) or (r in selected_docs.get("report", []))
        ok_p = ("period" not in selected_docs) or (p in selected_docs.get("period", []))
        return ok_t and ok_r and ok_p

    for key, headings in by_key.items():
        if matches(key):
            t, r, p = key
            # Coleta os headings excluídos exatamente como aparecem para possível filtro $nin
            for h in headings:
                if _normalize_text(h) in EXCLUDED_HEADINGS_NORM:
                    excluded_exact_values.add(h)
            # Remove headings excluídos da lista oferecida ao LLM
            doc_to_headings[f"{t}|{r}|{p}"] = _filter_excluded(headings)

    # Converte headings para IDs numéricos para enviar ao LLM
    doc_to_headings_with_ids, id_to_heading = _build_headings_with_ids(doc_to_headings)

    # Etapa 2: seleção de headings + query semântica
    t_step2_start = time.perf_counter()
    step2_prompt = prompt_step2(query_nl, selected_docs, doc_to_headings_with_ids, escopo=escopo_ctx)
    cfg2 = _extend_config(config, run_name="retriever_step2", extra_tags=["retriever", "step2"]) if config is not None else None
    resp2 = llm.invoke(step2_prompt, config=cfg2)
    t_step2_end = time.perf_counter()
    
    # Captura tokens do Step 2
    step2_tokens = extract_token_usage(resp2)
    
    # Captura resposta completa do LLM (Step 2)
    step2_raw_content = getattr(resp2, "content", resp2)
    data2 = extract_json_block(step2_raw_content)

    raw_filters = data2.get("filters") or {}
    semantic_query = str(data2.get("semantic_query", "") or query_nl)
    use_semantic = bool(data2.get("use_semantic", False))

    # Validação de headings via IDs (apenas IDs que existem no mapa são aceitos)
    requested_ids: List[int] = []
    if isinstance(raw_filters.get("headings_enriched"), dict):
        he = raw_filters["headings_enriched"].get("$in")
        if isinstance(he, list):
            # LLM pode retornar ints ou strings, garantir conversão
            requested_ids = [int(x) if isinstance(x, (int, str)) and str(x).isdigit() else -1 for x in he]
            requested_ids = [x for x in requested_ids if x > 0]  # Remove IDs inválidos
    
    # Conversão de IDs → headings reais (validação automática)
    validated_headings: List[str] = []
    for heading_id in requested_ids:
        heading_id_str = str(heading_id)
        if heading_id_str in id_to_heading:
            heading_text = id_to_heading[heading_id_str]
            validated_headings.append(heading_text)
    
    # Atualiza filtros com headings validados
    if requested_ids and not validated_headings:
        raw_filters.pop("headings_enriched", None)
    elif validated_headings:
        raw_filters["headings_enriched"] = {"$in": validated_headings}

    # Se nada de headings, seguimos com filtros só de documento (fallback a)
    base_filters = {k: v for k, v in raw_filters.items() if k in {"ticker", "report", "period", "headings_enriched"}}
    # Política para planilha: não filtrar por period e semântica OFF
    reports = set()
    if isinstance(base_filters.get("report"), dict):
        lst = base_filters["report"].get("$in")
        if isinstance(lst, list):
            reports = {str(x).lower() for x in lst}
    if "planilha" in reports:
        base_filters.pop("period", None)
        use_semantic = False
    # Força exclusão via $nin de headings genéricos (ex.: "cabeçalho") mesmo quando o LLM não seleciona headings
    if "headings_enriched" not in base_filters and excluded_exact_values:
        base_filters["headings_enriched"] = {"$nin": sorted(excluded_exact_values)}
    chroma_where_in = sanitize_where(base_filters)

    vs = build_vectorstore()
    coll = _get_collection(vs)

    # Debug: testar $in vs $or quando houver múltiplos headings
    chroma_where_final = chroma_where_in
    headings_clause = base_filters.get("headings_enriched") if base_filters else None
    used_or = False
    if isinstance(headings_clause, dict) and "$in" in headings_clause and isinstance(headings_clause["$in"], list) and len(headings_clause["$in"]) > 1:
        heads: List[str] = [str(x) for x in headings_clause["$in"]]
        # Monta $or de $eq
        base_and = []
        for key in ("ticker", "report", "period"):
            if key in base_filters:
                base_and.append({key: base_filters[key]})
        where_or: Dict[str, Any] = {"$and": base_and + [{"$or": [{"headings_enriched": {"$eq": h}} for h in heads]}]}
        where_or = sanitize_where(where_or)

        # Checagem rápida de existência
        cnt_in = _count_with_where(coll, chroma_where_in) if coll else -1
        cnt_or = _count_with_where(coll, where_or) if coll else -1

        if debug:
            print(f"[debug] candidatos com $in: {cnt_in}; com $or: {cnt_or}")
            if coll:
                print(f"[debug] amostra $in: {json.dumps(_sample_with_where(coll, chroma_where_in), ensure_ascii=False)}")
                print(f"[debug] amostra $or: {json.dumps(_sample_with_where(coll, where_or), ensure_ascii=False)}")

        # Se $in aparenta vazio mas $or não, use $or
        if (cnt_in == 0 or cnt_in is None) and (cnt_or and cnt_or > 0):
            chroma_where_final = where_or
            used_or = True
        else:
            chroma_where_final = chroma_where_in

    # Execução da busca
    docs_scores: List[Tuple[Any, float]] = []
    if use_semantic:
        docs_scores = vs.similarity_search_with_score(query=semantic_query, k=k, filter=chroma_where_final)
    else:
        # Semântica OFF: buscar diretamente por where
        coll = _get_collection(vs)
        try:
            chunk = coll.get(include=["documents", "metadatas"], where=chroma_where_final, limit=k, offset=0) if coll else {"documents": [], "metadatas": []}
            documents = chunk.get("documents", []) or []
            metadatas = chunk.get("metadatas", []) or []
            from langchain_core.documents import Document
            for i in range(min(k, len(metadatas))):
                md = metadatas[i] or {}
                text = documents[i] if i < len(documents) else ""
                docs_scores.append((Document(page_content=text, metadata=md), float("nan")))
        except Exception as e:
            if debug:
                print("Falha no fetch por where (semântico OFF):", e)
            docs_scores = []

    # Serializa saída de chunks (para consumo por tools/LLM)
    import math
    chunks_out: List[Dict[str, Any]] = []
    for d, score in docs_scores:
        md = d.metadata or {}
        chunks_out.append({
            "page_content": d.page_content,
            "metadata": md,
            "score": (score if isinstance(score, (int, float)) and math.isfinite(score) else None),
        })

    t1 = time.perf_counter()
    audit: Dict[str, Any] = {
        # Etapa 1
        "step1_input": query_nl,
        "step1_output": step1_raw_content if isinstance(step1_raw_content, str) else str(step1_raw_content),
        "step1_elapsed": round(t_step1_end - t_step1_start, 3),
        "step1_tokens": step1_tokens,  # NOVO: tokens do Step 1
        
        # Etapa 2
        "step2_input": {
            "query_nl": query_nl,
            "selected_docs": selected_docs,
            "doc_to_headings": doc_to_headings,  # Headings originais (para referência)
            "doc_to_headings_with_ids": doc_to_headings_with_ids,  # IDs enviados ao LLM
        },
        "step2_output": step2_raw_content if isinstance(step2_raw_content, str) else str(step2_raw_content),
        "step2_requested_ids": requested_ids,  # IDs retornados pelo LLM
        "step2_elapsed": round(t_step2_end - t_step2_start, 3),
        "step2_tokens": step2_tokens,  # NOVO: tokens do Step 2
        
        # Campos existentes (mantidos para compatibilidade)
        "selected_docs": selected_docs,
        "validated_headings": validated_headings,
        "semantic_query": semantic_query,
        "use_semantic": use_semantic,
        "where_final": chroma_where_final,
        "used_or": used_or,
        "retriever_model": (retriever_model or DEFAULT_RETRIEVER_MODEL),  # NOVO: modelo usado
        "elapsed_seconds": round(t1 - t0, 3),
        "elapsed_hms": format_hms(t1 - t0),
    }

    if debug:
        print(f"\nConsulta (semantic_query): {semantic_query}")
        print(f"Documentos selecionados (etapa 1): {selected_docs}")
        print(f"Decisão do LLM (use_semantic): {use_semantic}")
        if validated_headings:
            print(f"Headings filtrados (validados): {validated_headings}")
        print(f"Filtros finais (where): {chroma_where_final}  {'[$or escolhido]' if used_or else ''}\n")
        imprimir_chunks(chunks_out)
        print(f"Tempo de execução (query -> resultado): {audit['elapsed_hms']}")

    return {"chunks": chunks_out, "audit": audit}


def main() -> None:
    load_dotenv()
    print("\n=== Retriever (2 etapas): seleção de documentos -> seleção de headings -> busca semântica ===")

    query_nl = input("Pergunta (linguagem natural): ").strip()
    try:
        k = int((input("k (nº de resultados) [5]: ").strip() or "5"))
    except Exception:
        k = 5

    result = retriever_query(query_nl=query_nl, k=k, debug=True)
    # A impressão detalhada já foi feita dentro de retriever_query(debug=True)


if __name__ == "__main__":
    main()


