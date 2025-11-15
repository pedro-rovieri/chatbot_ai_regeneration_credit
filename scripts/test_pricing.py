#!/usr/bin/env python3
"""
Script de teste para validação do módulo de precificação.

Testa:
- Normalização de nomes de modelos
- Detecção de providers
- Cálculo de custos (OpenAI e Anthropic)
- Validação de tokens
- Formatação de valores
"""
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.pricing import (
    normalizar_nome_modelo,
    detectar_provider,
    obter_precos_modelo,
    calcular_custo,
    calcular_custo_detalhado,
    formatar_custo,
    formatar_tokens,
    listar_modelos_disponiveis,
    validar_tokens,
)


def test_normalizacao():
    """Testa normalização de nomes de modelos"""
    print("\n" + "="*70)
    print("TESTE 1: NORMALIZAÇÃO DE NOMES")
    print("="*70)
    
    test_cases = [
        # OpenAI
        ("gpt-5-2025-08-07", "gpt-5"),
        ("gpt-5-mini-2025-08-07", "gpt-5-mini"),
        ("openai/gpt-4o", "gpt-4o"),
        ("o3-2025-04-16", "o3"),
        
        # Anthropic
        ("claude-sonnet-4-5-20250929", "claude-sonnet-4.5"),
        ("claude-haiku-3-5-20240307", "claude-haiku-3.5"),
        ("claude_opus_4", "claude-opus-4"),
        
        # Já normalizados
        ("gpt-5", "gpt-5"),
        ("claude-sonnet-4.5", "claude-sonnet-4.5"),
    ]
    
    passed = 0
    failed = 0
    
    for input_name, expected in test_cases:
        result = normalizar_nome_modelo(input_name)
        status = "OK" if result == expected else "FALHA"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {input_name:40s} -> {result:20s} (esperado: {expected})")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_deteccao_provider():
    """Testa detecção de provider"""
    print("\n" + "="*70)
    print("TESTE 2: DETECÇÃO DE PROVIDER")
    print("="*70)
    
    test_cases = [
        ("gpt-5", "openai"),
        ("gpt-5-2025-08-07", "openai"),
        ("o3-pro", "openai"),
        ("claude-sonnet-4.5", "anthropic"),
        ("claude-sonnet-4-5-20250929", "anthropic"),
        ("modelo-desconhecido", "unknown"),
    ]
    
    passed = 0
    failed = 0
    
    for model, expected in test_cases:
        result = detectar_provider(model)
        status = "OK" if result == expected else "FALHA"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {model:40s} -> {result:12s} (esperado: {expected})")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_calculo_custos_openai():
    """Testa cálculo de custos para modelos OpenAI"""
    print("\n" + "="*70)
    print("TESTE 3: CÁLCULO DE CUSTOS - OpenAI")
    print("="*70)
    
    test_cases = [
        {
            "modelo": "gpt-5",
            "tokens": {"input": 10000, "output": 2000},
            "esperado": 0.0325,  # (10000 * 1.25 + 2000 * 10) / 1_000_000
            "descricao": "gpt-5: 10k input + 2k output"
        },
        {
            "modelo": "gpt-5-mini",
            "tokens": {"input": 50000, "output": 5000},
            "esperado": 0.0225,  # (50000 * 0.25 + 5000 * 2) / 1_000_000
            "descricao": "gpt-5-mini: 50k input + 5k output"
        },
        {
            "modelo": "o3",
            "tokens": {"input": 10000, "output": 2000, "reasoning": 1000},
            "esperado": 0.044,  # (10000 * 2 + 2000 * 8 + 1000 * 8) / 1_000_000
            "descricao": "o3: 10k input + 2k output + 1k reasoning"
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        custo = calcular_custo(case["tokens"], case["modelo"])
        # Tolerância de 0.0001 para comparação de floats
        match = abs(custo - case["esperado"]) < 0.0001
        status = "OK" if match else "FALHA"
        if match:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {case['descricao']}")
        print(f"          Calculado: {formatar_custo(custo)} | Esperado: {formatar_custo(case['esperado'])}")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_calculo_custos_anthropic():
    """Testa cálculo de custos para modelos Anthropic"""
    print("\n" + "="*70)
    print("TESTE 4: CÁLCULO DE CUSTOS - Anthropic")
    print("="*70)
    
    test_cases = [
        {
            "modelo": "claude-sonnet-4.5",
            "tokens": {"input": 10000, "output": 2000},
            "esperado": 0.06,  # (10000 * 3 + 2000 * 15) / 1_000_000
            "descricao": "claude-sonnet-4.5: 10k input + 2k output"
        },
        {
            "modelo": "claude-haiku-3.5",
            "tokens": {"input": 50000, "output": 5000},
            "esperado": 0.06,  # (50000 * 0.80 + 5000 * 4) / 1_000_000
            "descricao": "claude-haiku-3.5: 50k input + 5k output"
        },
        {
            "modelo": "claude-opus-4",
            "tokens": {"input": 10000, "output": 2000},
            "esperado": 0.3,  # (10000 * 15 + 2000 * 75) / 1_000_000
            "descricao": "claude-opus-4: 10k input + 2k output"
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        custo = calcular_custo(case["tokens"], case["modelo"])
        match = abs(custo - case["esperado"]) < 0.0001
        status = "OK" if match else "FALHA"
        if match:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {case['descricao']}")
        print(f"          Calculado: {formatar_custo(custo)} | Esperado: {formatar_custo(case['esperado'])}")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_calculo_custos_cache_anthropic():
    """Testa cálculo de custos com cache de prompt (Anthropic)"""
    print("\n" + "="*70)
    print("TESTE 5: CÁLCULO DE CUSTOS COM CACHE - Anthropic")
    print("="*70)
    
    test_cases = [
        {
            "modelo": "claude-sonnet-4.5",
            "tokens": {
                "input": 10000,
                "output": 2000,
                "cache_creation_input_tokens": 5000,  # 5k tokens escritos no cache
                "cache_read_input_tokens": 2000,      # 2k tokens lidos do cache
            },
            "esperado": 0.05835,  # (3000*3 + 5000*3.75 + 2000*0.30 + 2000*15) / 1_000_000
            "descricao": "claude-sonnet-4.5 com cache: 3k normal + 5k write + 2k read + 2k output"
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        custo = calcular_custo(case["tokens"], case["modelo"])
        match = abs(custo - case["esperado"]) < 0.0001
        status = "OK" if match else "FALHA"
        if match:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {case['descricao']}")
        print(f"          Calculado: {formatar_custo(custo)} | Esperado: {formatar_custo(case['esperado'])}")
        
        # Mostrar detalhamento
        detalhado = calcular_custo_detalhado(case["tokens"], case["modelo"])
        print(f"          Detalhamento: {detalhado}")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_formatacao():
    """Testa formatação de valores"""
    print("\n" + "="*70)
    print("TESTE 6: FORMATAÇÃO DE VALORES")
    print("="*70)
    
    # Teste de formatação de custos
    print("\n  Formatação de custos:")
    custo_tests = [
        (0.0325, "$0.03"),
        (12.4567, "$12.46"),
        (0.001, "$0.00"),
        (1000.999, "$1001.00"),
    ]
    
    passed = 0
    failed = 0
    
    for valor, esperado in custo_tests:
        resultado = formatar_custo(valor)
        match = resultado == esperado
        status = "OK" if match else "FALHA"
        if match:
            passed += 1
        else:
            failed += 1
        print(f"    [{status}] {valor} -> {resultado} (esperado: {esperado})")
    
    # Teste de formatação de tokens
    print("\n  Formatação de tokens:")
    token_tests = [
        (450, "450"),
        (1500, "1.5K"),
        (12500, "12.5K"),
        (3500000, "3.5M"),
    ]
    
    for num, esperado in token_tests:
        resultado = formatar_tokens(num)
        match = resultado == esperado
        status = "OK" if match else "FALHA"
        if match:
            passed += 1
        else:
            failed += 1
        print(f"    [{status}] {num} -> {resultado} (esperado: {esperado})")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_validacao():
    """Testa validação de tokens"""
    print("\n" + "="*70)
    print("TESTE 7: VALIDAÇÃO DE TOKENS")
    print("="*70)
    
    test_cases = [
        ({"input": 1000, "output": 500}, "gpt-5", True, "Tokens válidos (input/output)"),
        ({"input_tokens": 1000, "output_tokens": 500}, "claude-sonnet-4.5", True, "Tokens válidos (input_tokens/output_tokens)"),
        ({"output": 500}, "gpt-5", False, "Falta campo input"),
        ({"input": 1000}, "gpt-5", False, "Falta campo output"),
        ("string invalida", "gpt-5", False, "Tipo inválido (string)"),
        ({}, "gpt-5", False, "Dict vazio"),
    ]
    
    passed = 0
    failed = 0
    
    for tokens, model, esperado, descricao in test_cases:
        resultado = validar_tokens(tokens, model)
        match = resultado == esperado
        status = "OK" if match else "FALHA"
        if match:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {descricao}: {resultado} (esperado: {esperado})")
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_listagem_modelos():
    """Testa listagem de modelos disponíveis"""
    print("\n" + "="*70)
    print("TESTE 8: LISTAGEM DE MODELOS DISPONÍVEIS")
    print("="*70)
    
    modelos = listar_modelos_disponiveis()
    
    print(f"\n  Total de modelos OpenAI: {len(modelos['openai'])}")
    print(f"  Exemplos: {', '.join(modelos['openai'][:5])}")
    
    print(f"\n  Total de modelos Anthropic: {len(modelos['anthropic'])}")
    print(f"  Exemplos: {', '.join(modelos['anthropic'][:5])}")
    
    # Validação básica
    passed = (len(modelos['openai']) > 0 and len(modelos['anthropic']) > 0)
    status = "OK" if passed else "FALHA"
    print(f"\n  [{status}] Modelos disponíveis carregados")
    
    return passed


def main():
    """Executa todos os testes"""
    print("="*70)
    print("SUITE DE TESTES - MÓDULO DE PRECIFICAÇÃO")
    print("="*70)
    
    results = []
    
    # Executar todos os testes
    results.append(("Normalização de nomes", test_normalizacao()))
    results.append(("Detecção de provider", test_deteccao_provider()))
    results.append(("Cálculo custos OpenAI", test_calculo_custos_openai()))
    results.append(("Cálculo custos Anthropic", test_calculo_custos_anthropic()))
    results.append(("Cálculo custos com cache", test_calculo_custos_cache_anthropic()))
    results.append(("Formatação de valores", test_formatacao()))
    results.append(("Validação de tokens", test_validacao()))
    results.append(("Listagem de modelos", test_listagem_modelos()))
    
    # Resumo final
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    total_passed = sum(1 for _, passed in results if passed)
    total_failed = len(results) - total_passed
    
    for nome, passed in results:
        status = "PASSOU" if passed else "FALHOU"
        symbol = "OK" if passed else "FALHA"
        print(f"  [{symbol}] {nome:30s} : {status}")
    
    print("\n" + "-"*70)
    print(f"  Total: {total_passed}/{len(results)} testes passaram")
    print("="*70)
    
    # Retornar código de saída apropriado
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

