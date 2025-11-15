#!/usr/bin/env python3
"""
Módulo de precificação de tokens para modelos LLM (OpenAI e Anthropic).

Preços atualizados:
- OpenAI: Janeiro 2025 (https://platform.openai.com/docs/pricing)
- Anthropic: Novembro 2024 (https://www.anthropic.com/pricing)

Todos os preços são por 1M tokens (Standard tier).

Suporte a cache de prompt:
- Anthropic: Cache 5min (1.25x), Cache 1h (2x), Cache Hits (0.1x)
- OpenAI: Cached input (varia por modelo)
"""
from __future__ import annotations
from typing import Dict, Any


# ==================== TABELA DE PREÇOS ====================

# Preços OpenAI (USD por 1M tokens)
PRICING_OPENAI: Dict[str, Dict[str, float]] = {
    # Modelos GPT-5
    "gpt-5": {
        "input": 1.25,
        "cached_input": 0.125,
        "output": 10.00,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "cached_input": 0.025,
        "output": 2.00,
    },
    "gpt-5-nano": {
        "input": 0.05,
        "cached_input": 0.005,
        "output": 0.40,
    },
    "gpt-5-chat-latest": {
        "input": 1.25,
        "cached_input": 0.125,
        "output": 10.00,
    },
    "gpt-5-codex": {
        "input": 1.25,
        "cached_input": 0.125,
        "output": 10.00,
    },
    "gpt-5-pro": {
        "input": 15.00,
        "output": 120.00,
    },
    
    # Modelos GPT-4.1
    "gpt-4.1": {
        "input": 2.00,
        "cached_input": 0.50,
        "output": 8.00,
    },
    "gpt-4.1-mini": {
        "input": 0.40,
        "cached_input": 0.10,
        "output": 1.60,
    },
    "gpt-4.1-nano": {
        "input": 0.10,
        "cached_input": 0.025,
        "output": 0.40,
    },
    
    # Modelos GPT-4o
    "gpt-4o": {
        "input": 2.50,
        "cached_input": 1.25,
        "output": 10.00,
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "cached_input": 0.075,
        "output": 0.60,
    },
    
    # Modelos o1/o3 (reasoning)
    "o1": {
        "input": 15.00,
        "cached_input": 7.50,
        "output": 60.00,
    },
    "o1-pro": {
        "input": 150.00,
        "output": 600.00,
    },
    "o3": {
        "input": 2.00,
        "cached_input": 0.50,
        "output": 8.00,
    },
    "o3-pro": {
        "input": 20.00,
        "output": 80.00,
    },
    "o3-deep-research": {
        "input": 10.00,
        "cached_input": 2.50,
        "output": 40.00,
    },
    
    # Modelos GPT-4 (legacy)
    "gpt-4": {
        "input": 30.00,
        "output": 60.00,
    },
    "gpt-4-32k": {
        "input": 60.00,
        "output": 120.00,
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00,
    },
    "gpt-4-turbo-preview": {
        "input": 10.00,
        "output": 30.00,
    },
}

# Preços Anthropic Claude (USD por 1M tokens)
PRICING_ANTHROPIC: Dict[str, Dict[str, float]] = {
    # Série Opus
    "claude-opus-4.1": {
        "input": 15.00,
        "cache_write_5m": 18.75,   # 1.25x do input
        "cache_write_1h": 30.00,    # 2x do input
        "cache_read": 1.50,         # 0.1x do input
        "output": 75.00,
    },
    "claude-opus-4": {
        "input": 15.00,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "cache_read": 1.50,
        "output": 75.00,
    },
    "claude-opus-3": {
        "input": 15.00,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "cache_read": 1.50,
        "output": 75.00,
    },
    
    # Série Sonnet
    "claude-sonnet-4.5": {
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00,
    },
    "claude-sonnet-4": {
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00,
    },
    "claude-sonnet-3.7": {
        "input": 3.00,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.00,
        "cache_read": 0.30,
        "output": 15.00,
    },
    
    # Série Haiku
    "claude-haiku-4.5": {
        "input": 1.00,
        "cache_write_5m": 1.25,
        "cache_write_1h": 2.00,
        "cache_read": 0.10,
        "output": 5.00,
    },
    "claude-haiku-3.5": {
        "input": 0.80,
        "cache_write_5m": 1.00,
        "cache_write_1h": 1.60,
        "cache_read": 0.08,
        "output": 4.00,
    },
    "claude-haiku-3": {
        "input": 0.25,
        "cache_write_5m": 0.30,
        "cache_write_1h": 0.50,
        "cache_read": 0.03,
        "output": 1.25,
    },
}

# Combinação de todos os preços
PRICING_ALL = {**PRICING_OPENAI, **PRICING_ANTHROPIC}


# ==================== ALIASES DE MODELOS ====================

MODEL_ALIASES: Dict[str, str] = {
    # OpenAI - Aliases com sufixos de data
    "gpt-5-2025-08-07": "gpt-5",
    "gpt-5-mini-2025-08-07": "gpt-5-mini",
    "gpt-5-pro-2025-10-06": "gpt-5-pro",
    "o3-2025-04-16": "o3",
    "o3-pro-2025-06-10": "o3-pro",
    
    # Anthropic - Aliases com sufixos de data
    "claude-opus-4-20241120": "claude-opus-4",
    "claude-opus-4.1-20250101": "claude-opus-4.1",
    "claude-sonnet-4-20241120": "claude-sonnet-4",
    "claude-sonnet-4-5-20250929": "claude-sonnet-4.5",
    "claude-sonnet-3-7-20240620": "claude-sonnet-3.7",
    "claude-haiku-4-5-20250301": "claude-haiku-4.5",
    "claude-haiku-4-5-20251001": "claude-haiku-4.5",
    "claude-haiku-3-5-20240307": "claude-haiku-3.5",
    "claude-haiku-3-20240229": "claude-haiku-3",
    
    # Anthropic - Aliases alternativos (com underscore)
    "claude_opus_4": "claude-opus-4",
    "claude_sonnet_4_5": "claude-sonnet-4.5",
    "claude_haiku_3_5": "claude-haiku-3.5",
}


# ==================== FUNÇÕES DE NORMALIZAÇÃO ====================

def normalizar_nome_modelo(model: str) -> str:
    """
    Normaliza o nome do modelo, resolvendo aliases e removendo prefixos de provider.
    
    Args:
        model: Nome do modelo (pode incluir sufixo de data ou prefixo de provider)
        
    Returns:
        Nome normalizado do modelo para lookup na tabela de preços
        
    Examples:
        >>> normalizar_nome_modelo("gpt-5-2025-08-07")
        "gpt-5"
        >>> normalizar_nome_modelo("openai/gpt-5-mini")
        "gpt-5-mini"
        >>> normalizar_nome_modelo("claude-sonnet-4-5-20250929")
        "claude-sonnet-4.5"
    """
    if not model:
        return "claude-sonnet-4.5"  # Fallback padrão (modelo atual do projeto)
    
    # Remove prefixo de provider (ex: "openai/gpt-5" → "gpt-5")
    if "/" in model:
        model = model.split("/", 1)[1]
    
    # Resolve alias (ex: "gpt-5-2025-08-07" → "gpt-5")
    if model in MODEL_ALIASES:
        return MODEL_ALIASES[model]
    
    return model


def detectar_provider(model: str) -> str:
    """
    Detecta o provider (OpenAI ou Anthropic) baseado no nome do modelo.
    
    Args:
        model: Nome do modelo (normalizado ou não)
        
    Returns:
        "openai", "anthropic" ou "unknown"
    """
    model_norm = normalizar_nome_modelo(model)
    
    if model_norm.startswith("claude"):
        return "anthropic"
    elif model_norm.startswith(("gpt", "o1", "o3")):
        return "openai"
    else:
        return "unknown"


# ==================== FUNÇÕES DE PRECIFICAÇÃO ====================

def obter_precos_modelo(model: str) -> Dict[str, float] | None:
    """
    Obtém os preços de um modelo específico.
    
    Args:
        model: Nome do modelo (será normalizado automaticamente)
        
    Returns:
        Dicionário com preços ou None se modelo desconhecido
    """
    model_norm = normalizar_nome_modelo(model)
    return PRICING_ALL.get(model_norm)


def calcular_custo(
    tokens: Dict[str, int],
    model: str,
    use_cached: bool = False
) -> float:
    """
    Calcula o custo total baseado no uso de tokens.
    
    Args:
        tokens: Dicionário com contagens. Campos esperados:
            - input: tokens de entrada
            - output: tokens de saída
            - reasoning: tokens de raciocínio (opcional, OpenAI)
            - cache_creation_input_tokens: tokens de criação de cache (opcional, Anthropic)
            - cache_read_input_tokens: tokens de leitura de cache (opcional, Anthropic)
        model: Nome do modelo usado
        use_cached: Se True, usa preço de cached_input quando disponível (OpenAI apenas)
        
    Returns:
        Custo total em USD (float preciso, não arredondado)
        
    Examples:
        >>> tokens = {"input": 10000, "output": 2000}
        >>> calcular_custo(tokens, "claude-sonnet-4.5")
        0.06  # (10000 * 3.00 + 2000 * 15.00) / 1_000_000
    """
    precos = obter_precos_modelo(model)
    if not precos:
        # Modelo desconhecido: retorna custo zero e loga warning
        import sys
        print(f"[WARNING] Modelo desconhecido para precificação: {model}", file=sys.stderr)
        return 0.0
    
    provider = detectar_provider(model)
    
    # Extrai contadores de tokens (com defaults)
    input_tokens = tokens.get("input", 0) or tokens.get("input_tokens", 0)
    output_tokens = tokens.get("output", 0) or tokens.get("output_tokens", 0)
    reasoning_tokens = tokens.get("reasoning", 0) or tokens.get("reasoning_tokens", 0)
    
    custo_total = 0.0
    
    if provider == "anthropic":
        # Anthropic: suporte a cache de prompt
        cache_creation = tokens.get("cache_creation_input_tokens", 0)
        cache_read = tokens.get("cache_read_input_tokens", 0)
        
        # Input normal (sem cache)
        input_normal = input_tokens - cache_creation - cache_read
        if input_normal > 0:
            custo_total += (input_normal * precos["input"]) / 1_000_000
        
        # Cache creation (usa preço de write, default 5m)
        if cache_creation > 0:
            preco_cache_write = precos.get("cache_write_5m", precos["input"])
            custo_total += (cache_creation * preco_cache_write) / 1_000_000
        
        # Cache read (hits)
        if cache_read > 0:
            custo_total += (cache_read * precos["cache_read"]) / 1_000_000
        
        # Output
        custo_total += (output_tokens * precos["output"]) / 1_000_000
        
    else:  # OpenAI
        # Escolhe preço de input (cached ou normal)
        if use_cached and "cached_input" in precos:
            preco_input = precos["cached_input"]
        else:
            preco_input = precos["input"]
        
        # Input
        custo_total += (input_tokens * preco_input) / 1_000_000
        
        # Output
        custo_total += (output_tokens * precos["output"]) / 1_000_000
        
        # Reasoning tokens são cobrados como output tokens (padrão OpenAI)
        if reasoning_tokens > 0:
            custo_total += (reasoning_tokens * precos["output"]) / 1_000_000
    
    return custo_total


def calcular_custo_detalhado(
    tokens: Dict[str, int],
    model: str
) -> Dict[str, float]:
    """
    Calcula custo detalhado por tipo de token.
    
    Returns:
        {
            "input": custo_input,
            "output": custo_output,
            "cache_creation": custo_cache (se aplicável),
            "cache_read": custo_cache_read (se aplicável),
            "reasoning": custo_reasoning (se aplicável),
            "total": custo_total
        }
    """
    precos = obter_precos_modelo(model)
    if not precos:
        return {"total": 0.0}
    
    provider = detectar_provider(model)
    
    input_tokens = tokens.get("input", 0) or tokens.get("input_tokens", 0)
    output_tokens = tokens.get("output", 0) or tokens.get("output_tokens", 0)
    reasoning_tokens = tokens.get("reasoning", 0) or tokens.get("reasoning_tokens", 0)
    
    resultado = {}
    
    if provider == "anthropic":
        cache_creation = tokens.get("cache_creation_input_tokens", 0)
        cache_read = tokens.get("cache_read_input_tokens", 0)
        
        input_normal = input_tokens - cache_creation - cache_read
        
        resultado["input"] = (input_normal * precos["input"]) / 1_000_000 if input_normal > 0 else 0.0
        resultado["output"] = (output_tokens * precos["output"]) / 1_000_000
        resultado["cache_creation"] = (cache_creation * precos.get("cache_write_5m", 0)) / 1_000_000 if cache_creation > 0 else 0.0
        resultado["cache_read"] = (cache_read * precos["cache_read"]) / 1_000_000 if cache_read > 0 else 0.0
        
    else:  # OpenAI
        resultado["input"] = (input_tokens * precos["input"]) / 1_000_000
        resultado["output"] = (output_tokens * precos["output"]) / 1_000_000
        if reasoning_tokens > 0:
            resultado["reasoning"] = (reasoning_tokens * precos["output"]) / 1_000_000
    
    resultado["total"] = sum(resultado.values())
    return resultado


# ==================== FUNÇÕES DE FORMATAÇÃO ====================

def formatar_custo(valor: float) -> str:
    """
    Formata um valor de custo em USD.
    
    Args:
        valor: Valor em USD (float)
        
    Returns:
        String formatada (ex: "$0.0325", "$12.4567")
        
    Examples:
        >>> formatar_custo(0.0325)
        "$0.0325"
        >>> formatar_custo(12.4567)
        "$12.4567"
    """
    return f"${valor:.4f}"


def formatar_tokens(num: int) -> str:
    """
    Formata um número de tokens de forma legível (K, M).
    
    Args:
        num: Número de tokens
        
    Returns:
        String formatada (ex: "1.2K", "3.5M", "450")
        
    Examples:
        >>> formatar_tokens(450)
        "450"
        >>> formatar_tokens(12500)
        "12.5K"
        >>> formatar_tokens(3500000)
        "3.5M"
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def listar_modelos_disponiveis() -> Dict[str, list[str]]:
    """
    Retorna lista de todos os modelos com preços definidos, agrupados por provider.
    
    Returns:
        {"openai": [...], "anthropic": [...]}
    """
    openai_models = sorted(PRICING_OPENAI.keys())
    anthropic_models = sorted(PRICING_ANTHROPIC.keys())
    
    return {
        "openai": openai_models,
        "anthropic": anthropic_models
    }


# ==================== FUNÇÕES DE VALIDAÇÃO ====================

def validar_tokens(tokens: Dict[str, int], model: str) -> bool:
    """
    Valida se o dicionário de tokens contém os campos esperados para o modelo.
    
    Returns:
        True se válido, False caso contrário
    """
    if not isinstance(tokens, dict):
        return False
    
    # Campos mínimos obrigatórios
    has_input = "input" in tokens or "input_tokens" in tokens
    has_output = "output" in tokens or "output_tokens" in tokens
    
    return has_input and has_output


if __name__ == "__main__":
    # Testes básicos
    print("=" * 70)
    print("TESTE DO MÓDULO DE PRECIFICAÇÃO")
    print("=" * 70)
    
    # Teste 1: Normalização de nomes
    print("\n1. NORMALIZAÇÃO DE NOMES:")
    test_names = [
        "gpt-5-2025-08-07",
        "claude-sonnet-4-5-20250929",
        "openai/gpt-4o",
        "claude-haiku-3.5"
    ]
    for name in test_names:
        normalized = normalizar_nome_modelo(name)
        provider = detectar_provider(name)
        print(f"   {name:40s} -> {normalized:20s} ({provider})")
    
    # Teste 2: Cálculo de custos OpenAI
    print("\n2. CÁLCULO DE CUSTOS - OpenAI:")
    tokens_openai = {"input": 10000, "output": 2000, "reasoning": 1000}
    modelo_openai = "gpt-5"
    custo = calcular_custo(tokens_openai, modelo_openai)
    detalhado = calcular_custo_detalhado(tokens_openai, modelo_openai)
    print(f"   Modelo: {modelo_openai}")
    print(f"   Tokens: {tokens_openai}")
    print(f"   Custo total: {formatar_custo(custo)}")
    print(f"   Detalhamento: {detalhado}")
    
    # Teste 3: Cálculo de custos Anthropic
    print("\n3. CÁLCULO DE CUSTOS - Anthropic:")
    tokens_anthropic = {"input": 10000, "output": 2000}
    modelo_anthropic = "claude-sonnet-4.5"
    custo = calcular_custo(tokens_anthropic, modelo_anthropic)
    detalhado = calcular_custo_detalhado(tokens_anthropic, modelo_anthropic)
    print(f"   Modelo: {modelo_anthropic}")
    print(f"   Tokens: {tokens_anthropic}")
    print(f"   Custo total: {formatar_custo(custo)}")
    print(f"   Detalhamento: {detalhado}")
    
    # Teste 4: Listagem de modelos
    print("\n4. MODELOS DISPONÍVEIS:")
    modelos = listar_modelos_disponiveis()
    print(f"   OpenAI: {len(modelos['openai'])} modelos")
    print(f"   Anthropic: {len(modelos['anthropic'])} modelos")
    
    print("\n" + "=" * 70)
    print("TESTE CONCLUÍDO")
    print("=" * 70)

