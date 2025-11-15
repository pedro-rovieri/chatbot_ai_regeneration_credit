#!/usr/bin/env python3
"""
Script para testar as ferramentas RAG
"""
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tools.rag_tools import RAGTools


def test_tools():
    """Testa cada uma das ferramentas RAG"""
    
    print("="*70)
    print("TESTE DAS FERRAMENTAS RAG")
    print("="*70 + "\n")
    
    # Inicializar ferramentas
    print("Inicializando ferramentas...")
    rag_tools = RAGTools()
    tools = rag_tools.get_tools()
    
    print(f"[OK] {len(tools)} ferramentas carregadas\n")
    
    # Testes para cada ferramenta
    test_cases = [
        {
            "tool": "search_general",
            "query": "O que é o Regeneration Credit?",
            "description": "Busca geral sobre o projeto"
        },
        {
            "tool": "search_contracts",
            "query": "Como funciona a função withdraw?",
            "description": "Busca específica em contratos"
        },
        {
            "tool": "search_whitepaper",
            "query": "Quais são os tipos de usuário?",
            "description": "Busca no whitepaper"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print("-"*70)
        print(f"TESTE {i}: {test_case['description']}")
        print(f"Ferramenta: {test_case['tool']}")
        print(f"Query: '{test_case['query']}'")
        print("-"*70)
        
        # Encontrar ferramenta
        tool = next((t for t in tools if t.name == test_case['tool']), None)
        
        if not tool:
            print(f"[ERRO] Ferramenta '{test_case['tool']}' nao encontrada!\n")
            continue
        
        # Executar busca
        try:
            result = tool.func(test_case['query'])
            
            # Exibir resultado (primeiros 500 caracteres)
            print("\nResultado:")
            if len(result) > 500:
                print(result[:500] + "...")
                print(f"\n[...resultado truncado, total: {len(result)} caracteres]")
            else:
                print(result)
            
            print("\n[OK] Teste concluido com sucesso\n")
            
        except Exception as e:
            print(f"\n[ERRO] Erro ao executar ferramenta: {e}\n")
    
    print("="*70)
    print("TODOS OS TESTES CONCLUÍDOS")
    print("="*70)


if __name__ == "__main__":
    test_tools()

