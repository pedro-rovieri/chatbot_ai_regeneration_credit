#!/usr/bin/env python3
"""
finance_ai_pricing.py

Módulo de precificação de tokens para modelos OpenAI.
Preços atualizados em janeiro de 2025 (fonte: https://platform.openai.com/docs/pricing)

Todos os preços são por 1M tokens (Standard tier).
"""
from __future__ import annotations
from typing import Dict, Any

# Tabela de preços por modelo (valores em USD por 1M tokens)
# Fonte: https://platform.openai.com/docs/pricing (Standard tier)
PRICING: Dict[str, Dict[str, float]] = {
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

# Mapeamento de nomes de modelos com sufixos de data para nomes reais da API
MODEL_ALIASES: Dict[str, str] = {
    "gpt-5-2025-08-07": "gpt-5",
    "gpt-5-mini-2025-08-07": "gpt-5-mini",
    "gpt-5-pro-2025-10-06": "gpt-5-pro",
    "o3-2025-04-16": "o3",
    "o3-pro-2025-06-10": "o3-pro",
    # Adicione mais aliases conforme necessário
}


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
    """
    if not model:
        return "gpt-5"  # Fallback padrão
    
    # Remove prefixo de provider (ex: "openai/gpt-5" → "gpt-5")
    if "/" in model:
        model = model.split("/", 1)[1]
    
    # Resolve alias (ex: "gpt-5-2025-08-07" → "gpt-5")
    if model in MODEL_ALIASES:
        return MODEL_ALIASES[model]
    
    return model


def obter_precos_modelo(model: str) -> Dict[str, float] | None:
    """
    Obtém os preços de um modelo específico.
    
    Args:
        model: Nome do modelo (será normalizado automaticamente)
        
    Returns:
        Dicionário com preços {input, cached_input?, output} ou None se modelo desconhecido
    """
    model_norm = normalizar_nome_modelo(model)
    return PRICING.get(model_norm)


def calcular_custo(
    tokens: Dict[str, int],
    model: str,
    use_cached: bool = False
) -> float:
    """
    Calcula o custo total baseado no uso de tokens.
    
    Args:
        tokens: Dicionário com contagens {input, output, reasoning, total}
        model: Nome do modelo usado
        use_cached: Se True, usa preço de cached_input quando disponível
        
    Returns:
        Custo total em USD (float preciso, não arredondado)
        
    Examples:
        >>> tokens = {"input": 10000, "output": 2000, "reasoning": 1000, "total": 13000}
        >>> calcular_custo(tokens, "gpt-5")
        0.0325  # (10000 * 1.25 + 2000 * 10.00 + 1000 * 10.00) / 1_000_000
    """
    precos = obter_precos_modelo(model)
    if not precos:
        # Modelo desconhecido: retorna custo zero e loga warning
        import sys
        print(f"[WARNING] Modelo desconhecido para precificação: {model}", file=sys.stderr)
        return 0.0
    
    input_tokens = tokens.get("input", 0)
    output_tokens = tokens.get("output", 0)
    reasoning_tokens = tokens.get("reasoning", 0)
    
    # Escolhe preço de input (cached ou normal)
    if use_cached and "cached_input" in precos:
        preco_input = precos["cached_input"]
    else:
        preco_input = precos["input"]
    
    # Reasoning tokens são cobrados como output tokens (padrão OpenAI)
    preco_output = precos["output"]
    
    # Cálculo preciso (por 1M tokens)
    custo_input = (input_tokens * preco_input) / 1_000_000
    custo_output = (output_tokens * preco_output) / 1_000_000
    custo_reasoning = (reasoning_tokens * preco_output) / 1_000_000
    
    return custo_input + custo_output + custo_reasoning


def formatar_custo(valor: float) -> str:
    """
    Formata um valor de custo em USD com 2 casas decimais.
    
    Args:
        valor: Valor em USD (float)
        
    Returns:
        String formatada (ex: "$0.03", "$12.45")
        
    Examples:
        >>> formatar_custo(0.0325)
        "$0.03"
        >>> formatar_custo(12.4567)
        "$12.46"
    """
    return f"${valor:.2f}"


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


def listar_modelos_disponiveis() -> list[str]:
    """
    Retorna lista de todos os modelos com preços definidos.
    
    Returns:
        Lista de nomes de modelos
    """
    return sorted(PRICING.keys())

