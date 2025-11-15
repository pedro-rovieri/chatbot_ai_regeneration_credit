#!/usr/bin/env python3
"""
Script simples para calcular tokens LLM dos contratos Solidity
"""

import os
from pathlib import Path

def contar_tokens_aproximado(texto):
    """
    Conta tokens de forma aproximada (regra simples: ~4 chars = 1 token)
    Para cálculo mais preciso, instale: pip install tiktoken
    """
    # Aproximação simples: dividir por 4 (média de caracteres por token)
    return len(texto) // 4

def contar_tokens_tiktoken(texto):
    """
    Conta tokens usando tiktoken (OpenAI)
    Requer: pip install tiktoken
    """
    try:
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(texto))
    except ImportError:
        print("⚠️  tiktoken não instalado. Usando contagem aproximada.")
        print("   Para contagem precisa, execute: pip install tiktoken\n")
        return None

def processar_contratos(pasta_contratos):
    """
    Processa todos os arquivos .sol na pasta de contratos
    """
    pasta = Path(pasta_contratos)
    
    if not pasta.exists():
        print(f"❌ Pasta não encontrada: {pasta_contratos}")
        return
    
    # Encontrar todos os arquivos .sol
    arquivos_sol = list(pasta.rglob("*.sol"))
    
    if not arquivos_sol:
        print(f"❌ Nenhum arquivo .sol encontrado em: {pasta_contratos}")
        return
    
    print(f"📊 CALCULADORA DE TOKENS LLM")
    print(f"{'=' * 80}\n")
    print(f"📁 Pasta: {pasta_contratos}")
    print(f"📄 Arquivos encontrados: {len(arquivos_sol)}\n")
    
    # Verificar se tiktoken está disponível
    usar_tiktoken = False
    try:
        import tiktoken
        usar_tiktoken = True
        print("✅ Usando tiktoken (OpenAI) para contagem precisa\n")
    except ImportError:
        print("⚠️  Usando contagem aproximada (4 chars = 1 token)")
        print("   Para contagem precisa, execute: pip install tiktoken\n")
    
    total_tokens = 0
    total_chars = 0
    resultados = []
    
    # Processar cada arquivo
    for arquivo in sorted(arquivos_sol):
        try:
            conteudo = arquivo.read_text(encoding='utf-8')
            chars = len(conteudo)
            
            if usar_tiktoken:
                tokens = contar_tokens_tiktoken(conteudo)
            else:
                tokens = contar_tokens_aproximado(conteudo)
            
            total_tokens += tokens
            total_chars += chars
            
            # Caminho relativo para melhor visualização
            caminho_rel = arquivo.relative_to(pasta)
            
            resultados.append({
                'arquivo': str(caminho_rel),
                'tokens': tokens,
                'chars': chars
            })
            
        except Exception as e:
            print(f"⚠️  Erro ao processar {arquivo.name}: {e}")
    
    # Exibir resultados
    print(f"{'=' * 80}")
    print(f"{'ARQUIVO':<50} {'TOKENS':>12} {'CHARS':>12}")
    print(f"{'=' * 80}")
    
    for res in resultados:
        print(f"{res['arquivo']:<50} {res['tokens']:>12,} {res['chars']:>12,}")
    
    print(f"{'=' * 80}")
    print(f"{'TOTAL':<50} {total_tokens:>12,} {total_chars:>12,}")
    print(f"{'=' * 80}\n")
    
    # Estatísticas adicionais
    print(f"📈 ESTATÍSTICAS:")
    print(f"   • Total de arquivos: {len(arquivos_sol)}")
    print(f"   • Total de tokens: {total_tokens:,}")
    print(f"   • Total de caracteres: {total_chars:,}")
    print(f"   • Média de tokens por arquivo: {total_tokens // len(arquivos_sol):,}")
    print(f"   • Razão chars/token: {total_chars / total_tokens:.2f}")
    
    # Estimativa de custo (aproximada para GPT-4)
    custo_por_1k_tokens = 0.03  # USD (input)
    custo_estimado = (total_tokens / 1000) * custo_por_1k_tokens
    print(f"\n💰 ESTIMATIVA DE CUSTO (GPT-4 input):")
    print(f"   • ~${custo_estimado:.2f} USD por processamento completo")
    print(f"   • Baseado em ${custo_por_1k_tokens}/1K tokens\n")

if __name__ == "__main__":
    # Caminho para a pasta de contratos
    # Ajuste se necessário
    pasta_contratos = r"C:\Users\Pedro\Projeto_IA\regeneration-credit\contracts"
    
    # Ou use caminho relativo do script
    # pasta_contratos = Path(__file__).parent.parent.parent / "contracts"
    
    processar_contratos(pasta_contratos)

