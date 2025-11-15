"""
Script de teste para validar o loop ReAct manual do RegenerationCreditAgent.

Testa:
1. Chamada básica do chat
2. Captura de tokens
3. Retriever audits
4. Processamento de tool calls
"""
import sys
from pathlib import Path

# Adicionar chatbot-ia ao path
chatbot_dir = Path(__file__).parent.parent
if str(chatbot_dir) not in sys.path:
    sys.path.insert(0, str(chatbot_dir))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_chat():
    """Teste básico: pergunta simples ao agente"""
    print("\n" + "="*70)
    print("TESTE 1: Chat Básico")
    print("="*70)
    
    try:
        from agents.main_agent import RegenerationCreditAgent
        
        agent = RegenerationCreditAgent()
        print("[OK] Agente inicializado com sucesso")
        
        # Pergunta simples
        question = "O que e o Regeneration Credit?"
        print(f"\n[?] Pergunta: {question}")
        
        response = agent.chat(question)
        
        # Validar resposta
        assert response["success"], "Resposta nao foi bem-sucedida"
        print(f"\n[OK] Resposta recebida")
        print(f"[>>] Texto: {response['response'][:200]}...")
        
        # Validar tokens
        tokens = response.get("tokens", {})
        total_tokens = tokens.get("total", 0)
        custo = tokens.get("custo", 0.0)
        
        print(f"\n[$] TOKENS CAPTURADOS:")
        print(f"   Total: {total_tokens}")
        print(f"   Custo: ${custo:.4f}")
        print(f"   Formatado: {tokens.get('custo_formatado', 'N/A')}")
        
        if total_tokens > 0:
            print("\n[OK] [OK] [OK] SUCESSO! Tokens foram capturados corretamente!")
        else:
            print("\n[FAIL] [FAIL] [FAIL] FALHA! Tokens nao foram capturados!")
            return False
        
        # Validar stats
        stats = response.get("stats", {})
        print(f"\n[#] ESTATISTICAS:")
        print(f"   Chamadas LLM: {stats.get('total_chamadas_llm', 0)}")
        print(f"   Iteracoes: {stats.get('iterations', 0)}")
        print(f"   Tool calls: {stats.get('tool_calls', 0)}")
        print(f"   Retriever calls: {stats.get('total_retriever_calls', 0)}")
        
        # Validar audits do retriever
        audits = response.get("retriever_audits", [])
        if audits:
            print(f"\n[*] RETRIEVER AUDITS:")
            for i, audit in enumerate(audits, 1):
                print(f"   Audit {i}:")
                print(f"      Query: {audit.get('query', 'N/A')[:50]}...")
                print(f"      Chunks: {audit.get('num_results', 0)}")
                print(f"      Tool: {audit.get('tool_name', 'N/A')}")
        
        # Validar componentes
        componentes = tokens.get("por_componente", {})
        if componentes:
            print(f"\n[+] TOKENS POR COMPONENTE:")
            for comp_nome, comp_data in componentes.items():
                print(f"   {comp_nome}: {comp_data.get('total_tokens', 0)} tokens")
        
        print("\n" + "="*70)
        print("[OK] TESTE 1 PASSOU!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("TESTES DO LOOP REACT MANUAL")
    print("="*70)
    
    results = []
    
    # Teste 1
    results.append(("Chat Básico", test_basic_chat()))
    
    # Sumário
    print("\n" + "="*70)
    print("SUMÁRIO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] PASSOU" if result else "[FAIL] FALHOU"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n*** *** *** TODOS OS TESTES PASSARAM! *** *** ***")
        return 0
    else:
        print("\n[WARN] ALGUNS TESTES FALHARAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())

