from __future__ import annotations

from typing import Any, Dict, List


def extract_token_usage(msg: Any) -> Dict[str, int]:
    """Extrai contagem de tokens (input/output/reasoning/total) de uma resposta LLM."""
    # Helper para conversão segura
    def _safe_int(v: Any) -> int:
        try:
            return int(v) if v is not None else 0
        except (ValueError, TypeError):
            return 0
    
    # Tentativa principal: usage_metadata (LangChain >= 0.2)
    usage = getattr(msg, "usage_metadata", None)
    if usage:
        # Reasoning tokens podem estar em dois lugares (dependendo do modelo)
        reasoning = _safe_int(usage.get("reasoning_tokens"))
        if reasoning == 0:
            # Modelos o1/o3 colocam em output_token_details
            details = usage.get("output_token_details") or {}
            reasoning = _safe_int(details.get("reasoning"))
        
        return {
            "input": _safe_int(usage.get("input_tokens")),
            "output": _safe_int(usage.get("output_tokens")),
            "reasoning": reasoning,
            "total": _safe_int(usage.get("total_tokens")),
        }
    
    # Fallback mínimo: resposta direta da OpenAI (integrações externas)
    # Isso cobre casos onde msg não é AIMessage (ex: OpenAI SDK direto)
    if hasattr(msg, "usage"):
        raw_usage = msg.usage
        return {
            "input": _safe_int(getattr(raw_usage, "prompt_tokens", 0)),
            "output": _safe_int(getattr(raw_usage, "completion_tokens", 0)),
            "reasoning": _safe_int(getattr(raw_usage, "reasoning_tokens", 0)),
            "total": _safe_int(getattr(raw_usage, "total_tokens", 0)),
        }
    
    # Fallback final: retorna zeros (evita crashes)
    return {"input": 0, "output": 0, "reasoning": 0, "total": 0}


def content_to_text(content: Any) -> str:
    """Normaliza conteúdo heterogêneo (lista/dict/str) para texto simples."""
    try:
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, dict):
                    txt = item.get("text")
                    if isinstance(txt, str):
                        parts.append(txt)
                elif isinstance(item, str):
                    parts.append(item)
            if parts:
                return "\n".join(parts)
        if isinstance(content, dict):
            txt = content.get("text")
            if isinstance(txt, str):
                return txt
        if isinstance(content, str):
            return content
    except Exception:
        pass
    return str(content)


def fmt_hms(seconds: float) -> str:
    """Formata segundos no padrão HH:MM:SS."""
    total = int(max(0, seconds))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def start_turn(memory, logger, question: str):
    """Adiciona pergunta ao histórico/log e retorna histórico pronto para o LLM."""
    memory.add_user_message(question)
    logger.user(question)
    return memory.get_llm_history()


