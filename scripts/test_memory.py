#!/usr/bin/env python3
"""
Script para testar o gerenciamento de memória conversacional
"""
import sys
from pathlib import Path

# Adicionar chatbot-ia ao path
chatbot_dir = Path(__file__).parent.parent
if str(chatbot_dir) not in sys.path:
    sys.path.insert(0, str(chatbot_dir))

import logging
import sys

# Configurar encoding para suportar emojis no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.DEBUG,  # Mudado para DEBUG para ver os logs detalhados
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_memory():
    """Testa se a memória mantém o contexto entre mensagens"""
    print("\n" + "="*70)
    print("TESTE DE MEMÓRIA CONVERSACIONAL")
    print("="*70)
    
    try:
        from agents.main_agent import RegenerationCreditAgent
        
        agent = RegenerationCreditAgent()
        print("[OK] Agente inicializado\n")
        
        # Primeira pergunta
        print("-"*70)
        print("MENSAGEM 1: Oi")
        print("-"*70)
        response1 = agent.chat("Oi")
        print(f"\nResposta 1 (primeiros 200 chars):")
        print(response1["response"][:200] + "...\n")
        
        # Verificar histórico após primeira mensagem
        history = agent.get_conversation_history()
        print(f"[DEBUG] Histórico após mensagem 1:")
        print(f"   Total de mensagens na memória: {len(history)}")
        for i, msg in enumerate(history, 1):
            role = msg["role"]
            content_preview = msg["content"][:80].replace("\n", " ")
            print(f"   {i}. [{role}] {content_preview}...")
        
        # Segunda pergunta
        print("\n" + "-"*70)
        print("MENSAGEM 2: Você tem histórico de mensagens anteriores?")
        print("-"*70)
        
        # Verificar memória ANTES de enviar segunda mensagem
        print(f"\n[DEBUG] Memória ANTES da mensagem 2:")
        print(f"   Mensagens na memória: {len(agent.memory.chat_memory.messages)}")
        for i, msg in enumerate(agent.memory.chat_memory.messages, 1):
            msg_type = type(msg).__name__
            content_preview = str(msg.content)[:60].replace("\n", " ")
            print(f"   {i}. [{msg_type}] {content_preview}...")
        
        response2 = agent.chat("Você tem histórico de mensagens que trocamos anteriormente?")
        print(f"\nResposta 2 (primeiros 300 chars):")
        print(response2["response"][:300] + "...")
        
        # Verificar histórico após segunda mensagem
        history = agent.get_conversation_history()
        print(f"\n[DEBUG] Histórico após mensagem 2:")
        print(f"   Total de mensagens na memória: {len(history)}")
        for i, msg in enumerate(history, 1):
            role = msg["role"]
            content_preview = msg["content"][:80].replace("\n", " ")
            print(f"   {i}. [{role}] {content_preview}...")
        
        # Análise
        print("\n" + "="*70)
        print("ANÁLISE")
        print("="*70)
        
        if len(history) >= 4:  # 2 perguntas + 2 respostas = 4 mensagens
            print("[OK] Memória contém histórico completo")
            
            # Verificar se o agente mencionou o histórico
            if "não tenho" in response2["response"].lower() or "não consigo" in response2["response"].lower():
                print("[PROBLEMA] Agente NÃO reconheceu o histórico!")
                print("   - A memória está funcionando (histórico salvo)")
                print("   - MAS o LLM não está usando o histórico corretamente")
                print("   - Possível causa: System prompt ou carregamento de mensagens")
                return False
            else:
                print("[OK] Agente reconheceu o histórico")
                return True
        else:
            print(f"[PROBLEMA] Memória incompleta - esperado 4 mensagens, encontradas {len(history)}")
            return False
        
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_memory()
    print("\n" + "="*70)
    if success:
        print("✅ TESTE PASSOU - Memória funcionando")
    else:
        print("❌ TESTE FALHOU - Problema com memória")
    print("="*70 + "\n")
    sys.exit(0 if success else 1)

